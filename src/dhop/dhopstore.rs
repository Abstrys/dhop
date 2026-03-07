use json::JsonValue;
use json::object::Object;
use std::path::PathBuf;
use env_home::env_home_dir as home_dir;

pub const DHOP_STORE: PathBuf = PathBuf::from(".dhop.json");
pub struct DhopStore {
    store: Object,
}

impl DhopStore {
    fn new(&self) {
        self.store = JsonValue::new_object();
    }

    /// Load the store from the store file, if it exists.
    /// If the file doesn't exist, or there's an error, then return `false`.
    fn load(&self) -> bool {
        let mut path_to_store: PathBuf::from<home_dir()>;
        path_to_store.push(DHOP_STORE);
        if path_to_store.exists() {
            // load the existing store.
            let store_file_contents: String = fs::read_to_string(path_to_store).expect("Can't read from {path_to_store}");
            self.store = json::parse(&store_file_contents).expect("Couldn't parse {path_to_store} as JSON!");
            return true;
        } else {
            return false;
        }
    }

    fn save() -> bool {
        let mut success: bool = false;
        return success;
    }

    fn set_location(&self, loc_name: &str, loc_path: &str) {
    }

    fn has_location(loc_name: &str) -> bool {
    }

    fn get_location(loc_name: &str) -> &'static PathBuf {
    }

    fn rm_location(loc_name: &str) {
    }

    fn get_mark() -> &'static PathBuf {
    }

    fn push_stack(path: &str) {
    }

    fn pop_stack() -> &'static PathBuf {
    }
}

