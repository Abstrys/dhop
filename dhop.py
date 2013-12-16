#!/usr/bin/env python
from datetime import datetime
import cPickle
import glob
import os
import random
import shutil
import sys

# A command-line utility for hopping around the filesystem.
#
# Copyright (C) 2013, Abstrys / Eron Hennessey
#
# This file is released under the terms of the GNU General Public License, v3.  For details about this license, see
# LICENSE.txt or go to <http://www.gnu.org/licenses/gpl.html>
#
# Full documentation is in this file and in README.md
#

def __print_error__(string):
    """Print an error message."""
    print "*** Dhop error: %s" % (string)
    return


def __confirm__(query):
    """
    Asks the user a Y/N question, and returns true/false depending on their
    answer."""
    answer = raw_input("%s (y/n): " % (query))

    if answer.lower() == 'y':
        return True

    return False


# adapted from http://www.python.org/dev/peps/pep-0257/
def __format_doc__(string, line_start = 0, line_end = -1):
    """
    Remove significant leading space from all lines and return the resulting
    string."""

    if not string:
        return ''

    # Convert tabs to spaces and split into a list of lines:
    lines = string.expandtabs(4).splitlines()

    # Determine minimum indentation (first line doesn't count, and blank lines don't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    # if line_end is negative, then set it to the last line in the list.
    if line_end == -1:
        line_end = len(lines)

    # put the lines together, removing the first num_spaces characters from each line (except for line 0).
    result_text = ""

    if line_start == 0:
        result_text = lines[0] + '\n'
        line_start = 1

    for cur_line in lines[line_start:line_end]:
        result_text += cur_line[indent:] + '\n'

    return result_text


class Dhop:
    """Contains the public dhop class."""

    # some default data
    DHOP_CMD_FILE = '.dhopcmd'
    DHOP_STORE = '.dhop'
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
        'locations': {}, # empty dictionary
        'mark': "",      # empty string
        'stack': []      # empty list
    }


    def __init__(self):
        """Initialize Dhop."""
        home_dir = os.path.expanduser('~') # should work on all systems.
        # if the command file is there, remove it.
        try:
#            os.remove(os.path.join(home_dir, DHOP_CMD_FILE))
            pass
        except:
            pass

        # attempt to load the store.
        try:
            store_file = open(os.path.join(home_dir, Dhop.DHOP_STORE), 'rb')
            self.store = cPickle.load(store_file)
            store_file.close()
        except:
            pass

        if not hasattr(self, 'store') or self.store == None or len(self.store) == 0:
            self.store = Dhop.DEFAULT_STORE

        return


    def write_store(self):
        """Write the current Dhop data to disk."""
        store_file = open(os.path.join(os.path.expanduser('~'), Dhop.DHOP_STORE), 'wb')
        cPickle.dump(self.store, store_file)
        store_file.close()
        return

    def __cp_or_mv__(self, mv, args):
        op = 'cp'
        if mv:
            op = 'mv'

        # there must be (at least) two arguments.
        if len(args) < 2:
            __print_error__("%s requires two arguments!" % op)
            self.show_help(op)
            return

        # if there are more than two arguments, then its likely that the shell
        # already dereferenced a file-glob. File-globs are only allowed on the first
        # argument, so the *final* argument is assumed to be the destination.

        dest_path = self.resolve_location_or_path(args[-1]) # there can be only one!
        dest_is_dir = os.path.isdir(dest_path)

        source_paths = args[:-1] # we are many.

        # in the case where source_paths has only one value, it may be an unexpanded
        # file-glob. If so, expand it here.
        expanded = False
        if len(source_paths) == 1:
            source_paths = self.resolve_location_or_path(source_paths[0])
            source_paths = glob.glob(source_paths)
            expanded = True

        for source_path in source_paths:
            if not expanded:
                source_path = self.resolve_location_or_path(source_path)

        if dest_is_dir:
            dest_iny_path = os.path.join(dest_path, os.path.basename(source_path))
        else:
            dest_iny_path = dest_path

        if mv:
            shutil.move(source_path, dest_iny_path)
        elif os.path.isfile(source_path):
            shutil.copy2(source_path, dest_iny_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, dest_iny_path)
        else:
            __print_error__("The source location is neither a file nor a directory!")

        return

    def cp(self, args):
        """Copy files from one location/path to another

        Usage: dhop cp <source_path> <dest_path>

        Either source_path or dest_path can begin with a named location.

        If source_path is a directory, then the operation will copy the entire directory
        structure recursively, beginning at that location.

        File-globs (wildcards) can be used in source_path to specify multiple
        files/directories that match a pattern. In this case, all files or directories
        that match the pattern will be copied. If any directories match the pattern, the
        entire directory will be copied, recursively.

        In the case where source_path refers to a single file or directory, you can
        specify a different name for the file/directory in dest_path to rename the file
        during the copy. Specifying a filename in dest_path when source_path contains a
        file-glob will result in an error."""
        return self.__cp_or_mv__(False, args)


    def mv(self, args):
        """Move files from one location/path to another

        Usage: dhop mv <source_path> <dest_path>

        Either source_path or dest_path can begin with a named location.

        If source_path is a directory, then the operation will copy the entire directory
        structure recursively, beginning at that location.

        File-globs (wildcards) can be used in source_path to specify multiple
        files/directories that match a pattern. In this case, all files or directories
        that match the pattern will be copied. If any directories match the pattern, the
        entire directory will be copied, recursively.

        In the case where source_path refers to a single file or directory, you can
        specify a different name for the file/directory in dest_path to rename the file
        during the copy. Specifying a filename in dest_path when source_path contains a
        file-glob will result in an error."""
        return self.__cp_or_mv__(True, args)


    def set_location(self, args):
        """Set a name for a specified directory path.

        Usage: dhop set <name> [path]

        A name is required. It should consist of alpha-numeric characters, underscores
        or hyphens only, and should not conflict with any of the dhop command names.

        Note: For a list of command names, type 'dhop help'.

        If no path is provided, then the name is set for the current directory."""

        if len(args) == 0:
            __print_error__("You must specify at least one argument for set.")
            self.show_help('set');
            return

        name = args[0]
        pathname = ""

        if len(args) == 1 or len(args[1]) == 0:
            pathname = os.getcwd()
        else:
            # Sometimes a pathname can be cut into different args (if there are spaces in
            # the name), so collect all remaining arguments as one name.
            name = args[0]
            pathname = self.resolve_location_or_path(" ".join(args[1:]))

        if pathname == None:
            __print_error__("No such location or path 1: %s" % (args[1]))
            return

        self.store['locations'][name] = pathname
        return


    def forget(self, args):
        """Forget (delete) a named location that was previously set.

        Usage: dhop forget [location]"""

        if len(args) == 0 or len(args[0]) == 0:
            __print_error__("Can't forget nothing!")
            self.help(['forget'])
            return

        name = args[0]

        if name in self.store['locations']:
            del(self.store['locations'][name])

        return


    def mark(self, args):
        """Marks the provided path so that you can later return to it with the 'recall'
        command.

        Usage: dhop mark [path]

        If no path is given, then the current directory is assumed. This command
        overwrites any previous marks; there can be only one!"""
        path = ""

        if len(args) == 0 or len(args[0]) == 0:
            path = os.getcwd()
        else:
            path = self.resolve_location_or_path(args[0])

        if path == None:
            __print_error__("No such location or path 2: %s" % (args[0]))
        else:
            self.store['mark'] = path
        return


    def recall(self, args):
        """Return to the directory that was last marked with the 'mark' command.

        Usage: dhop recall"""
        path = self.store['mark']

        if path == None or len(path) == 0:
            __print_error__("Mark is not set! Use 'mark' to set a mark.")
            self.show_help('mark')
        else:
            self.go([path])

        return

    def path(self, args):
        """Print the full path for the named location.

        Usage: dhop resolve [location]

        If location refers to a named location, its full path will be printed.

        If location refers to a path, then the full path will be printed.

        Otherwise, an error will be printed."""

        if len(args) != 1:
            __print_error__("You must supply one argument to resolve!")
            self.show_help('resolve')
            return

        pathname = self.resolve_location_or_path(args[0])
        if pathname == None or len(path) == 0:
            __print_error__("No such location or path 3: %s" % (args[0]))
        else:
            print pathname

        return

    def push(self, args):
        """Push the current working directory onto the directory stack, then go to the
        named location or path.

        Usage: dhop push [location]

        If a location is not given, then the current working directory will still be
        pushed onto the stack, but no other action will be taken."""
        old_path = os.getcwd()
        path = ""

        if len(args) == 0 or len(args[0]) == 0:
            path = os.getcwd()
        else:
            path = self.resolve_location_or_path(args)

        if path == None:
            __print_error__("No such location or path 4: %s" % (args))
        else:
            self.store['stack'].append(old_path)
            self.go([path])

        return

    # Pops the last pushed location from the stack, and then transports you to
    # that location. You can set the following option:
    #
    # - all - Pops all of the pushed locations from the stack, then transports you
    # to the final location popped from the stack.
    def pop(self, args):
        """Pops the last pushed location from the stack, and then transports you to that
        location.

        Usage: dhop pop [all]

        Usually, this is used without specifying any arguments.

        There is one optional argument: 'all'. If specified, it pops all of the pushed
        locations from the stack, then transports you to the final location popped from
        the stack."""
        path = ""

        # first, check to see if we have anything to pop! If not, return an error.
        if len(self.store['stack']) == 0:
            __print_error__("Empty stack; can't pop!")
            return

        if len(args) == 1 and args[0] == 'all':
            while len(self.store['stack']) > 0:
                path = self.store['stack'].pop()
        else:
            path = self.store['stack'].pop()

        if path == None or len(path) == 0:
            __print_error__("Weird... no path returned!")
        else:
            self.go([path])

        return


    def show_list(self, args):
        """List all of the currently known locations.

        Usage: dhop list"""

        for key in sorted(self.store.keys()):
            data = self.store[key]

            # if there's no data for the section, skip ahead to the next section.
            if data == None or len(data) == 0:
                continue

            # print the section heading
            print "\n%s" % key.capitalize()
            print '=' * len(key)

            # the output depends on the type of data
            if type(data) is dict:
                for data_key in sorted(data.keys()):
                    print "%s: %s" % (data_key, data[data_key])
            elif type(data) is set or type(data) is list:
                pos = 1
                for li in reversed(data):
                  print "%3d: %s" % (pos, li)
                  pos += 1
            elif type(data) is str:
                print data
            else:
                __print_error__("Uknown data type: %s" % (type(data)))

        print ""
        return


    # Prints help.
    def show_help(self, args = None):
        """Shows command-line help.

        Usage: dhop help [cmd] ...

        You can specify multiple commands after 'help' to get help on more than one
        command at a time, or specify 'all' to get detailed help on all commands.

        To get help for the 'mark', 'forget', and 'push' commands:

            dhop help mark forget push

        To get help for all commands:

            dhop help all"""

        if args == None or len(args) == 0:
            print "\nDhop.py - https://github.com/Abstrys/dhop\n"
            print "The following commands are available:\n"

            for cmd in sorted(Dhop.USER_COMMANDS.keys()):
                print "- " + cmd

            print ""

            if __confirm__('more help?'):
                print __format_doc__(self.show_help.__doc__, 3)

                if __confirm__('even more help?'):
                    print "%s\n" % (__format_doc__("""
                There are three ways to use dhop:

                * 'set' a location, and then use that name in place of the path. For
                  example:

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

                * 'push' a path, which changes your directory to that path, and saves
                  the previous path (where you pushed) onto the stack, which can contain many
                  levels of such pushed directories. 'pop' to get back to the last one you
                  pushed.  'pop' again to get to the previous one, et cetera.

                      dhop push /some/very/long/path

                  You'll be taken to /some/very/long path. Then, to get back to where you were
                  before, type:

                      dhop pop"""))
        else:
            # fix args, if necessary. A quick check that makes using this function
            # easier.
            if isinstance(args, str):
                args = [args]

            for arg in args:
                # get the function associated with the command, and print its doc string.
                if arg in Dhop.USER_COMMANDS.keys():
                    print "\n%s - %s\n" % (arg, getattr(self, Dhop.USER_COMMANDS[arg]).__doc__)
                elif arg == 'all':
                    for cmd in sorted(Dhop.USER_COMMANDS.keys()):
                        print "\n%s - %s\n" % (cmd, getattr(self, Dhop.USER_COMMANDS[cmd]).__doc__)
                else:
                    __print_error__("Unknown command: %s" % (arg))

        return


    def go(self, args):
        """Go (cd) to the named location (or path).

        The args parameter is a list, so to call this function with a single location
        (the normal case), enclose it with square braces:

            dhop_instance.go([path])"""

        if len(args) != 1:
            __print_error__("You must specify one, and *only* one location to go to!")

        path = self.resolve_location_or_path(args)

        if path == None:
            __print_error__("Couldn't find either a stored location or a file-system path that matches:")
            __print_error__("  " + args[0])
            return False

        # OK, it looks like we're clear to *go*. Write the command file and return.
        home_dir = os.path.expanduser('~') # should work on all systems.
        f = open(os.path.join(home_dir, Dhop.DHOP_CMD_FILE), 'w')

        if os.name == 'posix':
            # if there are any spaces in the pathname, escape them.
            path = path.replace(" ", "\\ ")
            f.write("%s" % (path))
        else: # windows?
            f.write("cd /d %s" % (path))

        f.close()

        return True


    def resolve_location_or_path(self, name):
        """
        Check to see if the passed-in name refers to a stored location or path. If it
        does, return the path.

        If it doesn't exist either as a stored location or path, this method will return
        `None`."""

        # if name is a list, convert it to a string by joining together the elements.
        if type(name) is list:
            name = " ".join(name)

        # First, if the name is an absolute path (starts with '/' on Unix-likes, and something like 'D:\' on Windows),
        # then no processing needs to be done.  Just check to see if its valid.
        if os.path.isabs(name):
            if os.path.isdir(name) or os.path.isfile(name):
                return os.path.normpath(name)
            return None

        # Now that we've gotten that out of the way...
        locations = self.store['locations']

        # The path might have directories or a filespec attached. No worries, just
        # chop off the nose and use that as the part of the path to dereference.
        rest_of_the_path = ''

        if name.count(os.sep) != 0:
            name, rest_of_the_path = name.strip().split(os.sep, 1)

        resolved_path = None

        # The undecorated name *might* refer to a stored location...
        if name in self.store['locations']:
            resolved_path = os.sep.join([locations[name], rest_of_the_path])
        elif os.path.isdir(name): # Or it might be a path...
            resolved_path = os.sep.join([name, rest_of_the_path])
        else: # Or it might be a file, or something not created yet...
            resolved_path = name

        if resolved_path != None:
            return os.path.normpath(resolved_path)

        # whatever it is (or isn't), return it.
        return resolved_path


    def run(self, args):
        """Run the Dhop main loop"""
        # The first arg should be either a command (cp, mv, set, etc.), or a location
        # (with or without @)
        command_or_location = args[0]

        # The rest are args associated with the command.
        remaining_args = args[1:]

        # first, see if its a known command.
        if command_or_location in Dhop.USER_COMMANDS:
            getattr(self, Dhop.USER_COMMANDS[command_or_location])(remaining_args)
            # Write the store (some of the commands might change it).
            self.write_store()

        else: # it might be a location or path, in which case, just go there...

            path = self.resolve_location_or_path([command_or_location])

            if path == None:
                __print_error__("The first argument is not a location, path, or command that I recognize.")
                print "Type `dhop help` for a list of commands"
                return
            else:
                self.go([path])
                # There's no need to write the store here... going someplace doesn't
                # change a thing. Well, not in dhop.

        return

# ==========
# the script
# ==========

dhop = Dhop()
if len(sys.argv) < 2:
    dhop.show_help()
    exit()

dhop.run(sys.argv[1:])

