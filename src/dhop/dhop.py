#!/usr/bin/env python3
import json
import glob
import os
import shutil
import sys

# A command-line utility for hopping around the filesystem.
#
# Copyright (C) 2013-2018, Abstrys / Eron Hennessey
#
# This file is released under the terms of the GNU General Public License, v3.
# For details about this license, see LICENSE.txt or go to
# <http://www.gnu.org/licenses/gpl.html>
#
# Full documentation is in this file and in README.rst

# for Python 2|3 compatibility.
if not hasattr(__builtins__, 'raw_input'):
      raw_input=input

def __print_error__(string):
    """
    Print an error message.
    """
    print("!! dhop error: %s" % string)
    return


def __confirm__(query):
    """
    Asks the user a Y/N question, and returns true/false depending on their
    answer.
    """
    answer = raw_input("%s (y/n): " % (query))

    if answer.lower() == 'y':
        return True

    return False


# adapted from http://www.python.org/dev/peps/pep-0257/
def __format_doc__(string, extra_indent=0, line_start=0, line_end=-1):
    """
    Remove significant leading space from all lines and return the resulting
    string.
    """
    if not string:
        return ''

    # Convert tabs to spaces and split into a list of lines:
    lines = string.expandtabs(4).splitlines()

    # Determine minimum indentation (first line doesn't count, and blank lines
    # don't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    # if line_end is negative, then set it to the last line in the list.
    if line_end == -1:
        line_end = len(lines)

    # put the lines together, removing the first num_spaces characters from
    # each line (except for line 0).
    result_text = ""

    if line_start == 0:
        result_text = lines[0] + '\n'
        line_start = 1

    # convert the extra indent number into spaces
    extra_indent = ' ' * extra_indent

    # add each line to the result.
    for cur_line in lines[line_start:line_end]:
        result_text += "%s%s\n" % (extra_indent, cur_line[indent:])

    return result_text


class Dhop:
    """
    Contains the public dhop class.
    """
    # some default data
    DHOP_CMD_FILE = '.dhopcmd'
    DHOP_STORE = '.dhop.json'
    USER_COMMANDS = {
        'add': 'set_location',
        'cp': 'cp',
        'delete': 'forget',
        'forget': 'forget',
        'help': 'show_help',
        'list': 'show_list',
        'mark': 'mark',
        'mv': 'mv',
        'path': 'path',
        'pop': 'pop',
        'push': 'push',
        'recall': 'recall',
        'remove': 'forget',
        'resolve': 'path',
        'set': 'set_location',
        'unset': 'forget',
    }

    DEFAULT_STORE = {
        'locations': {},  # empty dictionary
        'mark': "",       # empty string
        'stack': []       # empty list
    }

    def __init__(self):
        """
        Initialize Dhop.
        """
        home_dir = os.path.expanduser('~')  # should work on all systems.

        # remove the command file if it exists
        command_file_path = os.path.join(home_dir, self.DHOP_CMD_FILE)
        if os.path.exists(command_file_path):
            os.remove(command_file_path)

        # check to see if a store file exists
        path_to_store = os.path.join(home_dir, self.DHOP_STORE)
        if os.path.exists(path_to_store):
            # load the existing store.
            store_file = open(os.path.join(home_dir, Dhop.DHOP_STORE), 'r')
            self.store = json.load(store_file)
            store_file.close()
        else:
            self.store = Dhop.DEFAULT_STORE


    def __write_store__(self):
        """
        Write the current Dhop data to disk.
        """
        store_file = open(os.path.join(os.path.expanduser('~'), Dhop.DHOP_STORE), 'w')
        json_str = json.JSONEncoder().encode(self.store)
        store_file.write(json_str)
        store_file.close()
        return


    def __interpret_src_args__(self, src_args):
        """
        Returns a list of resolved src_args (which may involve expanding a
        fileglob).
        """
        src_paths = list()

        for x in range(0, len(src_args) - 1):
            src_paths[x] = self.resolve_location_or_path(src_args[x])

        # In the case where src_args has only one value, it may be an
        # unexpanded file-glob. If so, resolve it and expand the glob here.
        if len(src_paths) == 1:
            src_paths = glob.glob(src_paths)

        return src_paths

    def __cp_or_mv__(self, args, op='cp'):
        """
        Copies (or moves) files given a source and destination path.
        """
        # there must be (at least) two arguments.
        if len(args) < 2:
            __print_error__("%s requires two arguments!" % op)
            self.show_help(op)
            return

        # dest_path: there can be only one! (in last place)
        dest_path = self.resolve_location_or_path(args[-1])
        dest_is_dir = os.path.isdir(dest_path)

        # source_paths: we are many (nobody else can be last!)
        source_paths = self.__interpret_src_args__(args[:-1])

        # no globs allowed here!
        for source_path in source_paths:
            # if dest_path is a directory, append the filename part of the
            # source path to the destination path.
            if dest_is_dir:
                fname = os.path.basename(source_path)
                dest_path = os.path.join(dest_path, fname)

            if op == 'mv':
                # move path -> path. 'move' doesn't care if the source is a
                # file or dir.
                shutil.move(source_path, dest_path)
            elif os.path.isfile(source_path):
                # if source_path is a file, use 'copy2'
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                # if source is a dir, then use 'copytree' instead.
                shutil.copytree(source_path, dest_path)
            else:
                __print_error__("The source location is neither a file nor a"
                                "directory!")
        return

    def cp(self, args):
        """
        Copy files from one location/path to another

        Usage: dhop cp <source_path> <dest_path>

        Either source_path or dest_path can begin with a named location.

        If source_path is a directory, then the operation will copy the entire
        directory structure recursively, beginning at that location.

        File-globs (wildcards) can be used in source_path to specify multiple
        files/directories that match a pattern. In this case, all files or
        directories that match the pattern will be copied. If any directories
        match the pattern, the entire directory will be copied, recursively.

        In the case where source_path refers to a single file or directory, you
        can specify a different name for the file/directory in dest_path to
        rename the file during the copy. Specifying a filename in dest_path
        when source_path contains a file-glob will result in an error."""
        return self.__cp_or_mv__(args)

    def mv(self, args):
        """
        Move files from one location/path to another

        Usage: dhop mv <source_path> <dest_path>

        Either source_path or dest_path can begin with a named location.

        If source_path is a directory, then the operation will copy the entire
        directory structure recursively, beginning at that location.

        File-globs (wildcards) can be used in source_path to specify multiple
        files/directories that match a pattern. In this case, all files or
        directories that match the pattern will be copied. If any directories
        match the pattern, the entire directory will be copied, recursively.

        In the case where source_path refers to a single file or directory, you
        can specify a different name for the file/directory in dest_path to
        rename the file during the copy. Specifying a filename in dest_path
        when source_path contains a file-glob will result in an error."""
        return self.__cp_or_mv__(args, op='mv')

    def set_location(self, args):
        """
        Set a name for a specified directory path.

        Usage: dhop set <name> [path]

        A name is required. It should consist of alpha-numeric characters,
        underscores or hyphens only, and should not conflict with any of the
        dhop command names.

        Note: For a list of command names, type 'dhop help'.

        If no path is provided, then the name is set for the current
        directory.
        """

        if len(args) == 0:
            __print_error__("You must specify at least one argument for set.")
            self.show_help('set')
            return

        name = args[0]
        pathname = ""

        if len(args) == 1 or len(args[1]) == 0:
            pathname = os.getcwd()
        else:
            # Sometimes a pathname can be cut into different args (if there are
            # spaces in the name), so collect all remaining arguments as one
            # name.
            name = args[0]
            pathname = self.resolve_location_or_path(" ".join(args[1:]))

        if pathname is not None:
            self.store['locations'][name] = pathname


    def forget(self, args):
        """
        Forget (delete) a named location that was previously set.

        Usage: dhop forget [location]
        """
        if len(args) == 0 or len(args[0]) == 0:
            __print_error__("Can't forget nothing!")
            self.help(['forget'])
            return

        name = args[0]

        if name in self.store['locations']:
            del(self.store['locations'][name])


    def mark(self, args):
        """
        Marks the provided path so that you can later return to it with the
        'recall' command.

        Usage: dhop mark [path]

        If no path is given, then the current directory is assumed. This
        command overwrites any previous marks; there can be only one!
        """
        path = ""

        if len(args) == 0 or len(args[0]) == 0:
            path = os.getcwd()
        else:
            path = self.resolve_location_or_path(args[0])

        if path is not None:
            self.store['mark'] = path


    def recall(self, args):
        """
        Return to the directory that was last marked with the 'mark'
        command.

        Usage: dhop recall
        """
        path = self.store['mark']

        if path is not None and len(path) != 0:
            self.go([path])
        else:
            __print_error__("Mark is not set! Use 'mark' to set a mark.")
            self.show_help('mark')


    def path(self, args):
        """
        Print the full path for the named location.

        Usage: dhop path [location]

        * If location refers to a named location, its full path will be printed.
        * If location refers to a path, then the full path will be printed.
        * Otherwise, an error will be printed.
        """
        if len(args) != 1:
            __print_error__("You must supply one argument to resolve!")
            self.show_help('resolve')
            return

        pathname = self.resolve_location_or_path(args[0])

        if pathname != None and len(pathname) != 0:
            print(pathname)


    def push(self, args):
        """
        Push the current working directory onto the directory stack, then go
        to the named location or path.

        Usage: dhop push [location]

        If a location is not given, then the current working directory will
        still be pushed onto the stack, but no other action will be taken.
        """
        old_path = os.getcwd()
        path = ""

        if len(args) == 0 or len(args[0]) == 0:
            path = os.getcwd()
        else:
            path = self.resolve_location_or_path(args)

        if path is not None:
            self.store['stack'].append(old_path)
            self.go([path])


    def pop(self, args):
        """
        Pops the last pushed location from the stack, and then transports
        you to that location.

        Usage: dhop pop [all]

        Usually, this is used without specifying any arguments.

        There is one optional argument: 'all'. If specified, it pops all of the
        pushed locations from the stack, then transports you to the final
        location popped from the stack.
        """
        path = ""

        # first, check to see if we have anything to pop! If not, return an
        # error.
        if len(self.store['stack']) == 0:
            __print_error__("Empty stack; can't pop!")
            return

        if len(args) == 1 and args[0] == 'all':
            while len(self.store['stack']) > 0:
                path = self.store['stack'].pop()
        else:
            path = self.store['stack'].pop()

        if path is None or len(path) == 0:
            __print_error__("Weird... no path returned!")
        else:
            self.go([path])

        return

    def show_list(self, args):
        """
        List all of the currently known locations.

        Usage: dhop list
        """
        for key in sorted(self.store.keys()):
            data = self.store[key]

            # if there's no data for the section, skip ahead to the next
            # section.
            if data is None or len(data) == 0:
                continue

            # print the section heading
            print("\n%s" % key.capitalize())
            print('=' * len(key))

            # the output depends on the type of data
            if type(data) is dict:
                for data_key in sorted(data.keys()):
                    print("%s: %s" % (data_key, data[data_key]))
            elif type(data) is set or type(data) is list:
                pos = 1
                for li in reversed(data):
                    print("%3d: %s" % (pos, li))
                    pos += 1
            elif type(data) is str:
                print(data)
            else:
                __print_error__("Uknown data type: %s" % (type(data)))

        print("")
        return

    def show_all_cmd_help(self):
        """
        Shows all of the commands with help
        """
        # A primary feature of this display is that the commands are collected
        # by function, so that we don't print the same information multiple
        # times.
        func_list = set(Dhop.USER_COMMANDS.viewvalues())

        uniq_cmds = list()

        for func_name in func_list:
            x = (cmd for (cmd, func) in Dhop.USER_COMMANDS.items() if func ==
                 func_name)
            uniq_cmds.append(sorted(x))

        for cmd in sorted(uniq_cmds):
            print("\n%s" % ", ".join(cmd))
            ds = getattr(self, Dhop.USER_COMMANDS[cmd[0]]).__doc__
            print("\n  %s" % __format_doc__(ds, 2))

    def show_basic_help(self):
        print("\nDhop.py - https://github.com/Abstrys/dhop\n")
        print("The following commands are available:\n")

        for cmd in sorted(Dhop.USER_COMMANDS.keys()):
            print("- %s" % cmd)

        # print an extra line after the command list
        print("")

    def show_extra_help(self):
        print("%s" % (__format_doc__("""
            There are three ways to remember locations with dhop:

            * 'set' a location, and then use that name in place of the
               path. For example:

                   dhop set secret_proj /some/very/long/path/

                or, if you're already in the /some/very/long/path directory:

                   dhop set secret_proj

                then, from wherever you are in the filesystem:

                   dhop secret_proj

            * 'mark' a location, and then use 'recall' to get back.

                   dhop mark /some/very/long/path

               or, if you're already in the /some/very/long/path directory:

                   dhop mark

               then, from wherever you are in the filesystem:

                   dhop recall

            * 'push' a path, which changes your directory to that path, and
               saves the previous path (where you pushed) onto the stack,
               which can contain many levels of such pushed directories.
               'pop' to get back to the last one you pushed. 'pop' again to
               get to the previous one, et cetera.

                   dhop push /some/very/long/path

               You'll be taken to /some/very/long path. Then, to get back to
               where you were before, type:

                   dhop pop""")))

    def show_help(self, args=None):
        """
        Shows command-line help.

        Usage: dhop help [cmd] ...

        You can specify multiple commands after 'help' to get help on more than
        one command at a time, or specify 'all' to get detailed help on all
        commands.

        To get help for the 'mark', 'forget', and 'push' commands:

            dhop help mark forget push

        To get help for all commands:

            dhop help all
        """

        if args is None or len(args) == 0:

            self.show_basic_help()

            if not __confirm__('more help?'):
                print("")
                return

            # next, show help about help.
            print(__format_doc__(self.show_help.__doc__, 0, 3))

            if not __confirm__('even more help?'):
                print("")
                return

            self.show_extra_help()
        else:
            # Make sure args is a list. If not, make it so. A quick check that
            # makes using this function easier.
            if isinstance(args, str):
                args = [args]

            # Iterate through the arguments (there may be more than one command
            # name that the user wants help with)
            for arg in args:
                if arg in Dhop.USER_COMMANDS.keys():
                    # get the function associated with the command, and print
                    # its doc string.
                    ds = getattr(self, Dhop.USER_COMMANDS[arg]).__doc__
                    print("\n%s - %s" % (arg, __format_doc__(ds, 2)))
                elif arg == 'all':
                    self.show_all_cmd_help()
                else:
                    # the user wants help for something we don't know about
                    # (yet).
                    __print_error__("Unknown command: %s" % (arg))
        return

    def go(self, args):
        """
        Go (cd) to the named location (or path).

        The args parameter is a list, so to call this function with a single
        location (the normal case), enclose it with square braces:

            dhop_instance.go([path])
        """
        if len(args) != 1:
            __print_error__("You must specify one, and *only* one location to"
                            "go to!")

        path = self.resolve_location_or_path(args)

        if path is None:
            __print_error__("Couldn't find either a stored location or a"
                            "file-system path that matches:")
            __print_error__("  " + args[0])
            return False

        # OK, it looks like we're clear to *go*. Write the command file and
        # return.
        home_dir = os.path.expanduser('~')  # should work on all systems.
        cmd_file_location = os.path.join(home_dir, Dhop.DHOP_CMD_FILE)
        f = open(cmd_file_location, 'w')
        if os.name == 'posix':
            # if there are any spaces in the pathname, escape them.
            path = path.replace(" ", "\\ ")
            f.write("cd " + path)
        else: # windows?
            f.write("cd /d %s" % (path))
        f.close()
        return True

    def resolve_location_or_path(self, name):
        """
        Check to see if the passed-in name refers to a stored location or path.
        If it does, return the path.

        If it doesn't exist either as a stored location or path, this method
        will return `None`.
        """
        # if name is a list, convert it to a string by joining together the
        # elements.
        if type(name) is list:
            name = " ".join(name)

        # First, if the name is an absolute path (starts with '/' on
        # Unix-likes, and something like 'D:\' on Windows), then no processing
        # needs to be done. Just check to see if its valid.
        if os.path.isabs(name):
            if os.path.exists(name):
                return os.path.normpath(name)
            else:
                __print_error__("Path doesn't exist: %s" % name)
                return None

        # Now that we've gotten that out of the way...
        locations = self.store['locations']

        # The path might have directories or a filespec attached. No worries,
        # just chop off the nose and use that as the part of the path to
        # dereference.
        rest_of_the_path = ''

        if name.count(os.sep) != 0:
            name, rest_of_the_path = name.strip().split(os.sep, 1)

        resolved_path = None

        # The undecorated name *might* refer to a stored location...
        if name in self.store['locations']:
            resolved_path = os.sep.join([locations[name], rest_of_the_path])
            if not os.path.exists(resolved_path):
                __print_error__("Location %s is set, but does not refer to a valid location!" %
                    (name, resolved_path))
                resolved_path = None
        else:
            if rest_of_the_path == '':
                resolved_path = name
            else:
                resolved_path = os.sep.join([name, rest_of_the_path])
            if os.path.exists(resolved_path):
                resolved_path = os.path.normpath(resolved_path)
            else:
                __print_error__("Location or path doesn't exist: %s" % resolved_path)
                resolved_path = None

        # whatever it is (or isn't), return it.
        return resolved_path

    def run(self, args):
        """
        Run the Dhop main loop
        """
        # first, see if its a known command.
        if args[0] in Dhop.USER_COMMANDS:
            getattr(self, Dhop.USER_COMMANDS[args[0]])(args[1:])
            # Write the store (some of the commands might change it).
            self.__write_store__()
        else:
            # it might be a location or path, in which case, just go there...
            path = self.resolve_location_or_path(args)

            if path is None:
                print("Type `dhop help` for a list of commands.")
                return
            else:
                self.go([path])
                # There's no need to write the store here... going someplace
                # doesn't change a thing. Well, not in dhop.
        return

# ==========
# the script
# ==========
if sys.argv[0] == __file__:
    dhop = Dhop()

    # Dhop needs at least one command.
    if len(sys.argv) < 2:
        dhop.show_help()
        sys.exit(0)

    # A command was provided... run it.
    dhop.run(sys.argv[1:])
    sys.exit(0)

