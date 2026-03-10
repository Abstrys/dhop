use std::collections::HashMap;
use env_home::env_home_dir as home_dir;
use std::path::PathBuf;

mod dhopstore;

const DHOP_CMD_FILE: PathBuf = PathBuf::from(".dhopcmd");

pub struct Dhop {
    store: dhopstore::DhopStore,
}

impl Dhop {
    /// Contains all data and functionality needed for an active `dhop` session.

    pub fn new(&self) {
        // The proper way to make a Dhop!

        // Remove the command file if it exists.
        let command_file_path: PathBuf = [home_dir(), DHOP_CMD_FILE].iter().collect();
        if command_file_path.exists() {
            fs::remove_file(command_file_path);
        }

        // Load the store file if it exists.
        let path_to_store: PathBuf = [home_dir(), dhopstore::DHOP_STORE].iter().collect();
        if path_to_store.exists() {
            // load the existing store.
            let store_file_contents: String = fs::read_to_string(path_to_store).expect("Can't read from {path_to_store}");
            self.store = json::parse(&store_file_contents).expect("Couldn't parse {path_to_store} as JSON!");
        }
    }

    pub fn run(&self, &args: Vec<String>) {
        // Maps ordinary strings to a path, also represented by a string.
        let mut location_map: HashMap<String, String> = HashMap::new();

        location_map.insert(String::from("music"), String::from("~/Music/"));

        let path: PathBuf = PathBuf::from(&args[1]);
        if path.is_dir() {
            let mut dhop_cmd_path: PathBuf = home_dir().expect("User has no home dir?!");
            dhop_cmd_path.push(DHOP_CMD_FILE);
            let mut cd_cmd = String::from("cd ");
            cd_cmd.push_str(&path.display().to_string());
            cd_cmd.push('\n');
            fs::write(dhop_cmd_path, cd_cmd.clone())?;
            Ok(())
        } else {
            let path: String = path.display().to_string();
            println!("'{path}' isn't a directory; I can't go there!");
            process::exit(1);
        }
    }
}

