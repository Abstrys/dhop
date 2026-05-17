/// A command-line utility for hopping around the filesystem.
///
/// Copyright © 2013-2025, Abstrys / Eron Hennessey (eron@abstrys.com)
/// This file is released under the terms of the BSD-3-Clause license. See LICENSE.txt or go to:
/// https://opensource.org/license/BSD-3-clause
///
/// Full documentation is in this file and in README.rst

use clap::{Parser, Subcommand};
use std::collections::HashMap;
use std::env;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(name="dhop", version, about, long_about=None)]
struct DhopCli {
    #[command(subcommand)]
    command: Option<Subcommand>,
}

/// The store of values for Dhop.
struct DhopStore {
    locations: HashMap<String, PathBuf>, // Locations known by a name.
    mark: PathBuf, // The location saved by the 'mark' command, there is only one.
    stack: Vec<PathBuf>, // A stack of values pushed and popped.
}

/// Set a name for the current (or optionally, a specified) directory path.
///
/// You can use this name to refer to the path for other dhop commands, such as 'go', 'path',
/// and so on.
///
/// name: The name for the provided path.
/// path: The path to associate with the name. If not provided, the current path is used.
fn cmd_set(name: &String, path: &PathBuf) {
    let path_str = path.display();
    println!("cmd_set: received name='{name}', path='{path_str}'");
}

/// Go (chdir) to a named location or path. This is the default if no command is provided.
///
/// name: The name of the location (previously 'set') or path to hop to.
///
/// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
/// interpreted as a 'set' location instead of a path.
///
/// Tip: Use 'list' to list all known locations.
fn cmd_go(name: &String) {
    println!("cmd_go: received name='{name}'");
}

/// Forget (delete) a named location previously 'set'.
///
/// name: The location name to forget...
fn cmd_forget(name: &String) {
    println!("cmd_forget: received name='{name}'");
}

/// Push the current (or optionally, a specified named location or path) to the stack.
///
/// Use 'pop' to return to the last 'push'ed location.
///
/// path: The path to push. If not provided, the current path is used.
///
/// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
/// interpreted as a 'set' location instead of a path.
fn cmd_push(path: &PathBuf) {
    let path_str = path.display();
    println!("cmd_push: received path='{path_str}'");
}


/// Go to the last 'push'-ed location, and remove it from the stack.
fn cmd_pop() {
}

/// Mark the current (or optionally, a specified named location or path) as the place to return
/// to when 'recall' is invoked.
///
/// path: The path to mark. If not provided, the current path is used.
///
/// Note: There can be only one!
fn cmd_mark(path: &PathBuf) {
    let path_str = path.display();
    println!("cmd_mark: received path='{path_str}'");
}

/// Return to the last 'mark'-ed location.
fn cmd_recall() {
    println!("cmd_recall called!");
}

/// List all of the currently known 'set', 'mark'ed, and 'push'ed locations.
fn cmd_list() {
    println!("cmd_list called!");
}

const CMD_PATH_DESC: &str = "Print the full path to a named location.";
const CMD_PATH_HELP: &str = concat!(
    "Usage:\n",
    "\n",
    "   dhop path <name>\n",
    "\n",
    "Where:\n",
    "\n",
    "   name: The named location to print.\n",
    "\n",
    "If a relative path is given, then the full path to that location is printed.",
    "\n",
    "Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to\n",
    "  be interpreted as a 'set' location instead of a path.\n",
    "\n",
    "Tip: You can use this to inject dhop-known locations into other CLI commands such as\n",
    "  'cd', 'cp', 'ls', and so on!\n",
);

fn cmd_path(name: &String)
{
    println!("cmd_path received name='{name}'");
}

const MAIN_DESC: &str = "Name, list, mark, and recall frequently-used paths on your filesystem.";
const MAIN_HELP: &str = concat!(
    "Usage:\n",
    "\n",
    "   dhop <cmd_or_location_or_path> [command_args]\n",
    "\n",
    "Where:\n",
    "\n",
    "   cmd_or_location: Either a named location (recorded with set) or one of the known commands.\n",
    "\n",
    "Any further arguments on the command-line are considered parameters for the given command.\n",
);

///
/// Main program sequence.
///
fn main() {
    // Grab the command-line args.
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
    }
}

