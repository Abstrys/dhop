/// A command-line utility for hopping around the filesystem.
///
/// Copyright © 2013-2025, Abstrys / Eron Hennessey (eron@abstrys.com)
///
/// This file is released under the terms of the BSD-3-Clause license. See LICENSE.txt or go to:
/// https://opensource.org/license/BSD-3-clause
///
/// Full documentation is in this file and in README.rst

use std::collections::HashMap;
use std::env;
// use std::fs;
// use std::process;
// use dirs;
mod dhop;
// use std::collections::HashMap;

const USER_COMMANDS: HashMap<&str, &str> = HashMap::from([
    ("add", "set_location"),
    ("cp", "cp"),
    ("delete", "forget"),
    ("forget", "forget"),
    ("help", "show_help"),
    ("list", "show_list"),
    ("mark", "mark"),
    ("mv", "mv"),
    ("path", "path"),
    ("pop", "pop"),
    ("push", "push"),
    ("recall", "recall"),
    ("remove", "forget"),
    ("resolve", "path"),
    ("set", "set_location"),
    ("unset", "forget"),
]);


fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("You need to supply a command, location or path!");
    }

    let dhop_inst: dhop::Dhop = dhop::Dhop::new();
    dhop_inst.run(args);
}

