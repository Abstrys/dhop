/// A command-line utility for hopping around the filesystem.
///
/// Copyright © 2013-2025, Abstrys / Eron Hennessey (eron@abstrys.com)
/// This file is released under the terms of the BSD-3-Clause license. See LICENSE.txt or go to:
/// https://opensource.org/license/BSD-3-clause
///
/// Full documentation is in this file and in README.rst

use clap::{Command, arg, command};
use std::path::PathBuf;
use std::env;
use std::fs;

const DHOP_CMD_FILE: &str = ".dhopcmd";
const DHOP_STORE: &str = ".dhop.json";
const MAIN_DESC: &str = "Name, mark, or push Filesystem paths; print or travel to them later.";

const CMD_SET_DESC: &str = "Set a name for a specified directory path.";
const CMD_SET_HELP: &str = concat!(
    "A name is required. It should consist of alpha-numeric characters, underscores or hyphens ",
    "only, and should not conflict with any of the dhop command names.\n",
    "\n",
    "Note: For a list of command names, type 'dhop help'.\n",
    "\n",
    "If no path is provided, then the name is set for the current directory.\n"
);

const CMD_PATH_DESC: &str = "Print the full path to a named location.";
const CMD_PATH_HELP: &str = concat!(
    "If a relative path is given, then the full path to that location is printed.\n",
    "\n",
    "Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to ",
    "be interpreted as a 'set' location instead of a path.\n",
    "\n",
    "Tip: You can use this to inject dhop-known locations into other CLI commands such as ",
    "'cd', 'cp', 'ls', and so on!\n",
);

fn goto_path(cmd_file_path: &PathBuf, desired_path: &PathBuf, verbosity: u8) {
    if desired_path.is_dir() {
        let _ = fs::write(&cmd_file_path, format!("cd {}\n\n", desired_path.display()));
        if verbosity > 0 {
            println!("Wrote command file to '{}'.", cmd_file_path.display());
        }
        println!("Moving to '{}'.", desired_path.display());
    }
    else {
        println!("ERROR: '{}' is a non-existent path!", desired_path.display());
    }
}

///
/// Main program sequence.
///
fn main() {
    let matches = command!()
        .version("2.0")
        .about(MAIN_DESC)
        .arg(arg!([location] "Location to 'go' to."))
        .subcommand(
            Command::new("set")
                .visible_aliases(["add"])
                .about(CMD_SET_DESC)
                .arg(arg!(<name> "A name that will be used to refer to this path."))
                .arg(arg!([path] "Optional path to set. Uses current directory otherwise."))
                .after_help(CMD_SET_HELP)
        )
        .subcommand(
            Command::new("go")
                .aliases(["goto"])
                .visible_aliases(["to"])
                .about("Go to the named path. The default if no command is given.")
                .arg(arg!(<name> "Named path to travel to."))
        )
        .subcommand(
            Command::new("forget")
                .visible_aliases(["unset", "delete", "remove"])
                .about("Forget a named path that was previously 'set'.")
                .arg(arg!(<name> "Name to forget."))
        )
        .subcommand(
            Command::new("list")
                .about("List all known paths.")
        )
        .subcommand(
            Command::new("path")
                .visible_aliases(["show", "resolve"])
                .about(CMD_PATH_DESC)
                .after_help(CMD_PATH_HELP)
                .arg(arg!(<name> "name to print the path for."))
        )
        .subcommand(
            Command::new("mark")
                .about("Marks a path to 'recall' later. There can be only one!")
                .arg(arg!([path] "Optional path to mark. Uses current directory otherwise."))
        )
        .subcommand(
            Command::new("recall")
                .about("Return to the 'mark'ed path.")
                .arg(arg!(--peek "Reveal the marked path, without traveling there."))
        )
        .subcommand(
            Command::new("push")
                .about("Push the current path onto the stack and go to the named location or path.")
                .arg(arg!([name] "A named location or path travel to."))
        )
        .subcommand(
            Command::new("pop")
                .about("Pop the last path from the stack (and go there if not there already).")
                .arg(arg!(--peek "Reveal the last path on the stack, without traveling there."))
        )
        .arg(arg!(-v --verbose... "Specify one or more times to increase verbosity. Default is minimal output.'"))
        .get_matches();

    // Set the verbosity level for output.
    let verbosity: u8 = *matches.get_one::<u8>("verbose").unwrap();
    if verbosity > 1 {
        println!("Debug output set to level {}", verbosity);
    }

    // Remove the command file if it exists.
    let mut cmd_file_path: PathBuf = env::home_dir().unwrap();
    cmd_file_path.push(DHOP_CMD_FILE);
    if cmd_file_path.is_file() {
        if verbosity > 1 {
            println!("Command file exists. Removing it!");
        }
        let _ = fs::remove_file(&cmd_file_path);
    }

    // This is the Dhop data store. a json::JsonValue object.
    let mut dhop_store = json::object!{};

    // Check for the presence of a data file. If it exists, then load data from it.
    let mut data_path: PathBuf = env::home_dir().unwrap();
    data_path.push(DHOP_STORE);
    if data_path.is_file() {
        let file_contents = fs::read_to_string(&data_path).expect("ERROR: Can't read from Dhop store!");
        dhop_store = json::parse(file_contents.as_str()).unwrap();
        if verbosity > 1 {
            println!("Loaded Dhop store from {}.", data_path.display());
        }
    }
    else {
        if verbosity > 1 {
            println!("Data store '{}' doesn't exist! Creating new, empty, data store.", data_path.display());
        }
        dhop_store["locations"] = json::object!{};
        dhop_store["mark"] = ".".into();
        dhop_store["stack"] = json::array![];
    }

    // Check to see if a (sub)command was specified.

    match matches.subcommand() {
        Some(("set", sub_matches)) => {
            if verbosity > 2 {
                println!("'set' command used!");
            }

            // 'set' needs a name and an optional path.
            let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
            let path_arg = sub_matches.get_one::<String>("path").map(|s| s.as_str());

            // Is a path provided?
            let mut path = PathBuf::new();
            if path_arg.is_none() {
                // No path, use the current working directory.
                path = env::current_dir().unwrap();
            }
            else {
                path.push(path_arg.unwrap());
                // Validate the user-supplied path.
                if !path.is_dir() {
                    println!("ERROR: {:?} is not a valid path!", path);
                    return;
                }
            }
            // Add the name and path to the store.
            dhop_store["locations"][name] = path.to_str().into();
            println!("Set location '{}' to '{}'.", name, path.display());
        }
        Some(("go", sub_matches)) => {
            if verbosity > 1 {
                println!("'go' called!");
            }
            let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
            if verbosity > 1 {
                println!("name = {:?}", name);
            }
            // See if the name exists in the store.
            if dhop_store["locations"].has_key(name) {
                // Write an appropriate command to change to its path in the command file.
                let mut path: PathBuf = PathBuf::new();
                path.push(dhop_store["locations"][name].to_string());
                goto_path(&cmd_file_path, &path, verbosity);
            }
            else {
                println!("Location '{}' doesn't exist in the store!", name);
            }
        }
        Some(("forget", sub_matches)) => {
            if verbosity > 1 {
                println!("'forget' called!");
            }
            let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
            if verbosity > 1 {
                println!("name = {:?}", name);
            }
            // See if the name exists in the store.
            if dhop_store["locations"].has_key(name) {
                dhop_store["locations"].remove(name);
                println!("Removed location named '{}'.", name);
            }
            else {
                println!("No existing location named '{}'! Forgetting nothing.", name);
            }
        }
        Some(("list", _sub_matches)) => {
            if verbosity > 1 {
                println!("'list' called!");
            }
            println!("{}", dhop_store.pretty(3));
        }
        Some(("path", sub_matches)) => {
            if verbosity > 1 {
                println!("'path' called!");
            }
            let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
            if verbosity > 1 {
                println!("name = {:?}", name);
            }
            // See if the name exists in the store.
            if dhop_store["locations"].has_key(name) {
                let mut path: PathBuf = PathBuf::new();
                path.push(dhop_store["locations"][name].to_string());
                if verbosity < 1 {
                    println!("{}", path.display());
                }
                else {
                    println!("The path for '{}' is '{}'.", name, path.display());
                }
            }
            else {
                // The name doesn't exist, but perhaps a path was used in its place. We can still
                // print the full path if so.
                let mut path: PathBuf = PathBuf::new();
                path.push(name);
                if path.is_dir() {
                    println!("{}", path.display());
                }
                else {
                    println!("No existing location named '{}'!", name);
                    println!("Hint: Try 'dhop list' to view existing locations.");
                }
            }
        }
        Some(("mark", sub_matches)) => {
            if verbosity > 1 {
                println!("'mark' called!");
            }
            // Check to see if a path was provided.
            let path_arg = sub_matches.get_one::<String>("path").map(|s| s.as_str());
            let mut path = PathBuf::new();
            if path_arg.is_none() {
                path = env::current_dir().unwrap();
            }
            else {
                path.push(path_arg.unwrap());
                if !path.is_dir() {
                    println!("ERROR: {:?} is not a valid path!", path);
                    return;
                }
            }
            if verbosity > 1 {
                println!("path = {:?}", path);
            }
            dhop_store["mark"] = path.to_str().into();
            println!("Path '{}' is now marked.", path.display())
        }
        Some(("recall", _sub_matches)) => {
            if verbosity > 1 {
                println!("'recall' called!");
            }
            let path_arg = dhop_store["mark"].as_str();
            let mut path = PathBuf::new();
            path.push(path_arg.unwrap());
            goto_path(&cmd_file_path, &path, verbosity);
        }
        Some(("push", sub_matches)) => {
            if verbosity > 1 {
                println!("'push' called!");
            }
            let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
            let mut path: PathBuf = PathBuf::new();
            // See if the name exists in the store.
            if dhop_store["locations"].has_key(name) {
                path.push(dhop_store["locations"][name].to_string());
            }
            else {
                // The name doesn't exist, but perhaps a path was used in its place.
                path.push(name);
            }

            if path.is_dir() {
                // A named location or valid path was provided.
                if verbosity > 1 {
                    println!("path = {:?}", path);
                }
                let cur_dir = env::current_dir().expect("No current dir?");
                let _ = dhop_store["stack"].push(cur_dir.to_str());
                println!("Added '{}' to stack.", cur_dir.display());
                goto_path(&cmd_file_path, &path, verbosity);
            }
            else {
               println!("ERROR: No existing location named '{}', nor is it a path!!", name);
            }
        }
        Some(("pop", _sub_matches)) => {
            if verbosity > 1 {
                println!("'pop' called!");
            }
            if dhop_store["stack"].len() > 0 {
                let last_stack_val = dhop_store["stack"].pop();
                let path_arg = last_stack_val.as_str();
                let mut path = PathBuf::new();
                path.push(path_arg.unwrap());
                goto_path(&cmd_file_path, &path, verbosity);
            }
            else {
                println!("No paths exist on the stack! Going... nowhere.");
            }
        }
        Some((x, _sub_matches)) => {
            println!("ERROR: Unknown subcommand: '{}'!", x);
        }
        None => {
            if matches.args_present() {
                let args: Vec<String> = env::args().collect();
                if args.len() >= 2 {
                    // Look for the first argument without a '-' in front of it.
                    for i in 1..args.len() {
                        let arg_str = &args[i];
                        if arg_str.chars().next().unwrap() != '-' {
                            // See if the name exists in the store.
                            if dhop_store["locations"].has_key(arg_str) {
                                // Write an appropriate command to change to its path in the command file.
                                let mut path: PathBuf = PathBuf::new();
                                path.push(dhop_store["locations"][arg_str].to_string());
                                goto_path(&cmd_file_path, &path, verbosity);
                            }
                            else {
                                // The argument is neither a command or named location. Is it a
                                // path, tho?
                                let mut path: PathBuf = PathBuf::new();
                                path.push(arg_str);
                                if path.is_dir() {
                                    // Yes, it's a path. Go there.
                                    goto_path(&cmd_file_path, &path, verbosity);
                                } else {
                                    // It's nothing recognizable.
                                    println!("ERROR: Provided argument '{}' is neither a command, named location, or path!", arg_str);
                                }
                            }
                            break;
                        }
                    }
                }
            }
            else {
                println!("ERROR: No arguments provided!");
                println!("Hint: Use --help for a list of commands");
            }
        }
    }

    // Write the Dhop data store.
    let _ = fs::write(&data_path, json::stringify(dhop_store));
    if verbosity > 1 {
        println!("Wrote Dhop store to {}.", data_path.display())
    }
}

