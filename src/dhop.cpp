#include <stdio.h>
#include <filesystem>
#include "CLI11.hpp"

const char* DHOP_DESC = "dhop - Mark and recall filesystem paths";

bool configure_set_cmd(CLI::App &app) {
   CLI::App* set_cmd = app.add_subcommand("set", "Set a name for a specified filesystem path, or for the current location if no path is provided.");
   set_cmd->alias("add");
   return true;
}

bool configure_forget_cmd(CLI::App &app) {
   CLI::App* forget_cmd = app.add_subcommand("forget", "Forget (delete) a named location that was previously set.");
   forget_cmd->alias("unset");
   forget_cmd->alias("delete");
   return true;
}

bool configure_mark_cmd(CLI::App &app) {
   CLI::App* mark_cmd = app.add_subcommand("mark", "Marks the provided path so that you can later return to it with the 'recall' command.");
   return true;
}

bool configure_recall_cmd(CLI::App &app) {
   CLI::App* recall_cmd = app.add_subcommand("recall", "Return to the path that was last marked with the 'mark' command.");
   return true;
}

bool configure_push_cmd(CLI::App &app) {
   CLI::App* push_cmd = app.add_subcommand("push", "Push the current path onto the stack, then go to the named location or path.");
   return true;
}

bool configure_pop_cmd(CLI::App &app) {
   CLI::App* pop_cmd = app.add_subcommand("pop", "Pops the last pushed path off of the stack, and then transports you to that location.");
   return true;
}

bool configure_list_cmd(CLI::App &app) {
   CLI::App* list_cmd = app.add_subcommand("list", "List all of the currently known locations.");
   return true;
}

bool configure_path_cmd(CLI::App &app) {
   CLI::App* path_cmd = app.add_subcommand("path", "Print the full path for the named location.");
   return true;
}

int main(int argc, char** argv) {
   CLI::App app(DHOP_DESC);
   argv = app.ensure_utf8(argv);
   app.allow_extras();

   std::string filename = "default";

   configure_set_cmd(app);
   configure_forget_cmd(app);
   configure_mark_cmd(app);
   configure_recall_cmd(app);
   configure_push_cmd(app);
   configure_pop_cmd(app);
   configure_list_cmd(app);
   configure_path_cmd(app);

   CLI11_PARSE(app, argc, argv);
   return 0;
}

