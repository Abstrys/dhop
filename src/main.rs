/// A command-line utility for hopping around the filesystem.
///
/// Copyright © 2013-2025, Abstrys / Eron Hennessey (eron@abstrys.com)
/// This file is released under the terms of the BSD-3-Clause license. See LICENSE.txt or go to:
/// https://opensource.org/license/BSD-3-clause
///
/// Full documentation is in this file and in README.rst

use clap::{Parser, Subcommand};
use std::path::PathBuf;
use std::env;

#[derive(Parser, Debug)]
#[command(name="dhop", version, about, long_about=None)]
struct DhopCli {
    #[command(subcommand)]
    command: Option<Subcommands>,
}

#[derive(Subcommand, Debug)]
enum Subcommands {
    /// Set a name for the current (or optionally, a specified) directory path.
    ///
    /// You can use this name to refer to the path for other dhop commands, such as 'go', 'path',
    /// and so on.
    Set {
        /// The name for the provided path.
        name: String,
        /// The path to associate with the name. If not provided, the current path is used.
        path: Option<PathBuf>,
    },

    /// Go (chdir) to a named location or path. This is the default if no command is provided.
    Go { 
        /// The name of the location (previously 'set') or path to hop to.
        ///
        /// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
        /// interpreted as a 'set' location instead of a path.
        ///
        /// Tip: Use 'list' to list all known locations.
        location: String,
    },

    /// Forget (delete) a named location previously 'set'.
    Forget {
        /// The location name to forget...
        name: String,
    },

    /// Push the current (or optionally, a specified named location or path) to the stack.
    ///
    /// Use 'pop' to return to the last 'push'ed location.
    Push {
        /// The path to push. If not provided, the current path is used.
        ///
        /// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
        /// interpreted as a 'set' location instead of a path.
        location: String,
    },

    /// Go to the last 'push'-ed location, and remove it from the stack.
    Pop { },

    /// Mark the current (or optionally, a specified named location or path) as the place to return
    /// to when 'recall' is invoked.
    ///
    /// Note: There can be only one!
    Mark {
        /// The path to mark. If not provided, the current working directory is used.
        ///
        /// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
        /// interpreted as a 'set' location instead of a path.
        location: String,
    },

    /// Return to the last 'mark'-ed location.
    Recall { },

    /// List all of the currently known 'set', 'mark'ed, and 'push'ed locations.
    List { },

    /// Print the full path to a named location or path.
    Path {
        /// The named location or path to print.
        ///
        /// If a relative path is given, then the full path to that location is printed.
        ///
        /// Note: Prepending `@` to the beginning of the location, as '@<location>', forces it to be
        /// interpreted as a 'set' location instead of a path.
        ///
        /// Tip: You can use this to inject dhop-known locations into other CLI commands such as
        /// 'cd', 'cp', 'ls', and so on!   
        location: String,
    },
}

/// The store of values for Dhop.
/*
struct DhopStore {
    locations: Map<String, PathBuf>, // Locations known by a name.
    mark: PathBuf, // The location saved by the 'mark' command, there is only one.
    stack: Vec<PathBuf>, // A stack of values pushed and popped.
}
*/

/// Implementation for 'set' command.
fn cmd_set(name: &String, path: PathBuf) {
    let path_str = path.display();
    println!("cmd_set: received name='{name}', path='{path_str}'");
}

fn main() {
    let _dhop = DhopCli::parse();

    match &_dhop.command {
        Some(Subcommands::Set{ name, path }) => {
            println!("DEBUG: 'dhop set' was called");
            println!("DEBUG:    name: {name}");
            let set_dir: PathBuf; // will hold the final path.
            match path {
                Some(user_path) => {
                    // The user provided a path...
                    println!("DEBUG:   path: {:?}", user_path.to_str());
                    set_dir = user_path.clone();
                }
                None => {
                    // No path was provided. Use the current directory.
                    match env::current_dir() {
                        Ok(cur_dir) => {
                            set_dir = cur_dir.clone();
                        }
                        Err(e) => {
                            println!("ERROR! Could not get current dir!");
                            println!("       {e}");
                            return;
                        }
                    }
                }
            }
            cmd_set(name, set_dir);
        }
        Some(Subcommands::Go{ location }) => {
            println!("'dhop go' was used");
            println!("   location: {location}");
        }
        Some(Subcommands::Forget{ name }) => {
            println!("'dhop forget' was used");
            println!("   name: {name}");
        }
        Some(Subcommands::Push{ location }) => {
            println!("'dhop push' was used");
            println!("   location: {location}");
        } Some(Subcommands::Pop{ }) => {
            println!("'dhop pop' was used");
        }
        Some(Subcommands::Mark{ location }) => {
            println!("'dhop mark' was used");
            println!("   location: {location}");
        }
        Some(Subcommands::Recall{ }) => {
            println!("'dhop mark' was used");
        }
        Some(Subcommands::List{ }) => {
            println!("'dhop mark' was used");
        }
        Some(Subcommands::Path{ location }) => {
            println!("'dhop mark' was used");
            println!("   location: {location}");
        }
        None => {
            println!("Default subcommand");
        }
    }
}

