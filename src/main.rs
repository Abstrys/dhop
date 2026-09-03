/// A command-line utility for hopping around the filesystem.
///
/// Copyright © 2013-2025, Abstrys / Eron Hennessey (eron@abstrys.com)
/// This file is released under the terms of the BSD-3-Clause license. See LICENSE.txt or go to:
/// https://opensource.org/license/BSD-3-clause
///
/// Full documentation is in this file and in README.rst

use clap::{Command, arg, command, ArgMatches};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

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
const ERR_HOME_DIR: &str = "ERROR: Cannot determine user's home directory!";

/// The serialized data struct for Dhop. It holds all named locations, the marked location, and the
/// push/pop stack.
#[derive(Serialize, Deserialize)]
struct DhopStore {
    locations: HashMap<String, PathBuf>,
    mark: Option<PathBuf>,
    stack: Vec<PathBuf>,
}

impl DhopStore {
    /// Load DhopStore data from a JSON file.
    fn load(path: &Path, verbosity: u8) -> serde_json::Result<Self> {
        if path.is_file() {
            let file_contents = fs::read_to_string(&path).expect("ERROR: Can't read from Dhop store!");
            let data: DhopStore = serde_json::from_str(file_contents.as_str())?;
            if verbosity > 0 {
                println!("Loaded data from '{}'", path.display());
            }
            Ok(data)
        }
        else {
            let new_store = r#"
                {
                    locations: {},
                    mark: "",
                    stack: []
                }
                "#;
            let data = serde_json::from_str(new_store)?;
            if verbosity > 0 {
                println!("Dhop data not found at '{}'. Creating new, empty, data store.", path.display());
            }
            Ok(data)
        }
    }

    /// Save DhopStore data to a JSON file.
    fn save(&self, path: &Path, verbosity: u8) -> serde_json::Result<()> {
        // Get a JSON string that represents this data.
        let json_string = serde_json::to_string(&self).expect("Cannot convert Dhop store to JSON!");
        // Write the Dhop data store.
        fs::write(&path, json_string).expect("Could not write to Dhop store!");
        if verbosity > 1 {
            println!("Wrote Dhop store to {}.", path.display())
        }
        Ok(())
    }
}

fn goto_path(cmd_file_path: &PathBuf, desired_path: &PathBuf, verbosity: u8) {
    if desired_path.is_dir() {
        match fs::write(&cmd_file_path, format!("cd {}\n\n", desired_path.display())) {
            Ok(_) => {
                if verbosity > 0 {
                    println!("Wrote command file to '{}'.", cmd_file_path.display());
                }
                println!("Moving to '{}'.", desired_path.display());
            }
            Err(_) => {
                eprintln!("ERROR: Failed to write to '{}'!", cmd_file_path.display());
            }
        }
    }
    else {
        eprintln!("ERROR: '{}' is a non-existent path!", desired_path.display());
    }
}

/// If a path is provided, use it. Otherwise, return the current working directory (CWD).
fn resolve_path_or_cwd(path_arg: Option<&str>) -> Result<PathBuf, &str> {
    match path_arg {
        Some(p) => {
            let path = PathBuf::from(p);
            match path.is_dir() {
                true => { Ok(path) }
                false => { Err("Provided path is not a directory!") }
            }
        }
        None => {
            match env::current_dir() {
                Ok(p) => { Ok(p) }
                Err(_) => { Err("Could not read current directory!") }
            }
        }
    }
}

/// Define the CLI interface and parse arguments from the command line, returning an
/// [ArgMatches](https://docs.rs/clap/latest/clap/struct.ArgMatches.html).
fn define_and_parse_args() -> ArgMatches {
    command!()
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
        .get_matches()
}

/// Handle the "set" command.
fn handle_set_cmd(sub_matches: &ArgMatches, dhop_store: &mut DhopStore, verbosity: u8) {
    if verbosity > 2 {
        println!("'set' command used!");
    }

    // 'set' needs a name and an optional path.
    let name = sub_matches.get_one::<String>("name").expect("Name is required!");

    // If the user supplied a path, use it. Otherwise, use the current dir.
    let path_arg = sub_matches.get_one::<String>("path").map(|s| s.as_str());
    let path = resolve_path_or_cwd(path_arg).expect("Could not resolve path!");

    // Add the name and path to the store.
    dhop_store.locations.insert(name.clone(), path.clone());
    println!("Set location '{}' to '{}'.", name, path.display());
}

/// Handle the "go" command.
fn handle_go_cmd(sub_matches: &ArgMatches, dhop_store: &mut DhopStore, cmd_file_path: &PathBuf, verbosity: u8) {
    if verbosity > 1 {
        println!("'go' called!");
    }
    let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
    if verbosity > 1 {
        println!("name = {:?}", name);
    }
    // See if the name exists in the store.
    if dhop_store.locations.contains_key(name) {
        // Write an appropriate command to change to its path in the command file.
        let mut path: PathBuf = PathBuf::new();
        path.push(dhop_store.locations[name].clone());
        goto_path(cmd_file_path, &path, verbosity);
    }
    else {
        println!("Location '{}' doesn't exist in the store!", name);
    }
}

/// Handle the "forget" command.
fn handle_forget_cmd(sub_matches: &ArgMatches, dhop_store: &mut DhopStore, verbosity: u8) {
    if verbosity > 1 {
        println!("'forget' called!");
    }
    let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
    if verbosity > 1 {
        println!("name = {:?}", name);
    }
    // See if the name exists in the store.
    if dhop_store.locations.contains_key(name) {
        dhop_store.locations.remove(name);
        println!("Removed location named '{}'.", name);
    }
    else {
        println!("No existing location named '{}'! Forgetting nothing.", name);
    }
}

/// Handle the "list" command.
fn handle_list_cmd(_sub_matches: &ArgMatches, dhop_store: &DhopStore, verbosity: u8) {
    if verbosity > 1 {
        println!("'list' called!");
    }
    println!("{}", serde_json::to_string_pretty(&dhop_store).expect("Cannot format store as JSON!"));
}

/// Handle the "path" command.
fn handle_path_cmd(sub_matches: &ArgMatches, dhop_store: &DhopStore, verbosity: u8) {
    if verbosity > 1 {
        println!("'path' called!");
    }
    let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
    if verbosity > 1 {
        println!("name = {:?}", name);
    }
    // See if the name exists in the store.
    if dhop_store.locations.contains_key(name) {
        let mut path: PathBuf = PathBuf::new();
        path.push(dhop_store.locations[name].clone());
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

/// Handle the "mark" command.
fn handle_mark_cmd(sub_matches: &ArgMatches, dhop_store: &mut DhopStore, verbosity: u8) {
    if verbosity > 1 {
        println!("'mark' called!");
    }
    // If the user supplied a path, use it. Otherwise, use the current dir.
    let path_arg = sub_matches.get_one::<String>("path").map(|s| s.as_str());
    let path = resolve_path_or_cwd(path_arg).expect("Could not resolve path!");
    if verbosity > 1 {
        println!("path = {:?}", path);
    }
    dhop_store.mark = Some(path.clone());
    println!("Path '{}' is now marked.", path.display())
}

/// Handle the "recall" command.
fn handle_recall_cmd(_sub_matches: &ArgMatches, dhop_store: &mut DhopStore, cmd_file_path: &PathBuf, verbosity: u8) {
    if verbosity > 1 {
        println!("'recall' called!");
    }
    match dhop_store.mark.clone() {
        Some(p) => {
            goto_path(&cmd_file_path, &p, verbosity);
        }
        None => {
            println!("No path has been marked!");
            println!("Call 'mark' within a directory first.");
        }
    }
}

/// Handle the "push" command.
fn handle_push_cmd(sub_matches: &ArgMatches, dhop_store: &mut DhopStore, cmd_file_path: &PathBuf, verbosity: u8) {
    if verbosity > 1 {
        println!("'push' called!");
    }
    let name = sub_matches.get_one::<String>("name").expect("Name is required!").as_str();
    let mut path: PathBuf = PathBuf::new();
    // See if the name exists in the store.
    if dhop_store.locations.contains_key(name) {
        path.push(dhop_store.locations[name].clone());
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
        dhop_store.stack.push(cur_dir.clone());
        println!("Added '{}' to stack.", cur_dir.display());
        goto_path(&cmd_file_path, &path, verbosity);
    }
    else {
       eprintln!("ERROR: No existing location named '{}', nor is it a path!!", name);
    }
}

/// Handle the "pop" command.
fn handle_pop_cmd(_sub_matches: &ArgMatches, dhop_store: &mut DhopStore, cmd_file_path: &PathBuf, verbosity: u8) {
    if verbosity > 1 {
        println!("'pop' called!");
    }
    match dhop_store.stack.pop() {
        Some(p) => {
            goto_path(&cmd_file_path, &p, verbosity);
        }
        None => {
            println!("No paths exist on the stack! Going... nowhere.");
        }
    }
}

/// Handles the case where no command was provided, but
fn handle_non_command_arg(matches: &ArgMatches, dhop_store: &mut DhopStore, cmd_file_path: &PathBuf, verbosity: u8) {
    if matches.args_present() {
        let args: Vec<String> = env::args().collect();
        if args.len() >= 2 {
            // Look for the first argument without a '-' in front of it.
            for i in 1..args.len() {
                let arg_str = &args[i];
                if arg_str.chars().next().is_some() {
                    // See if the name exists in the store.
                    if dhop_store.locations.contains_key(arg_str) {
                        // Write an appropriate command to change to its path in the command file.
                        let mut path: PathBuf = PathBuf::new();
                        path.push(dhop_store.locations[arg_str].clone());
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
                            eprintln!("ERROR: Provided argument '{}' is neither a command, named location, or path!", arg_str);
                        }
                    }
                    break;
                }
            }
        }
    }
    else {
        eprintln!("ERROR: No arguments provided!");
        eprintln!("Hint: Use --help for a list of commands");
    }
}

///
/// Main program sequence.
///
fn main() {
    // Parse
    let matches = define_and_parse_args();

    // Set the verbosity level for output.
    let verbosity: u8 = *matches.get_one::<u8>("verbose").expect("ERROR: Unable to determine verbosity level!");
    if verbosity > 1 {
        println!("Debug output set to level {}", verbosity);
    }

    // Remove the command file if it exists.
    let mut cmd_file_path: PathBuf = env::home_dir().expect(ERR_HOME_DIR);
    cmd_file_path.push(DHOP_CMD_FILE);
    if cmd_file_path.is_file() {
        if verbosity > 1 {
            println!("Command file exists. Removing it!");
        }
        let _ = fs::remove_file(&cmd_file_path);
    }

    // This is the Dhop data store. a json::JsonValue object.
    let mut store_path: PathBuf = env::home_dir().expect(ERR_HOME_DIR);
    store_path.push(DHOP_STORE);
    let mut dhop_store = DhopStore::load(&store_path, verbosity).expect("ERROR: Could not load store or create a new one!");

    // Check to see if a (sub)command was specified.
    match matches.subcommand() {
        Some(("set", sub_matches)) => {
            handle_set_cmd(&sub_matches, &mut dhop_store, verbosity);
        }
        Some(("go", sub_matches)) => {
            handle_go_cmd(&sub_matches, &mut dhop_store, &cmd_file_path, verbosity);
        }
        Some(("forget", sub_matches)) => {
            handle_forget_cmd(&sub_matches, &mut dhop_store, verbosity);
        }
        Some(("list", sub_matches)) => {
            handle_list_cmd(&sub_matches, &mut dhop_store, verbosity);
        }
        Some(("path", sub_matches)) => {
            handle_path_cmd(&sub_matches, &mut dhop_store, verbosity);
        }
        Some(("mark", sub_matches)) => {
            handle_mark_cmd(&sub_matches, &mut dhop_store, verbosity);
        }
        Some(("recall", sub_matches)) => {
            handle_recall_cmd(&sub_matches, &mut dhop_store, &cmd_file_path, verbosity)
        }
        Some(("push", sub_matches)) => {
            handle_push_cmd(&sub_matches, &mut dhop_store, &cmd_file_path, verbosity);
        }
        Some(("pop", sub_matches)) => {
            handle_pop_cmd(&sub_matches, &mut dhop_store, &cmd_file_path, verbosity);
        }
        Some((x, _sub_matches)) => {
            eprintln!("ERROR: Unknown subcommand: '{}'!", x);
        }
        None => {
            handle_non_command_arg(&matches, &mut dhop_store, &cmd_file_path, verbosity);
        }
    }

    // Write the Dhop data store.
    if let Err(_) = dhop_store.save(&store_path, verbosity)
    {
        eprintln!("Failed to save Dhop store!");
    }
}

