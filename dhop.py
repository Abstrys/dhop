#!/usr/bin/env python
import os
import sys
import cPickle

# A command-line utility for hopping around the filesystem.
#
# Copyright (C) 2013, Abstrys / Eron Hennessey
#
# This file is released under the terms of the GNU General Public License, v3.
# For details about this license, see LICENSE.txt or go to
# <http://www.gnu.org/licenses/gpl.html>
#
# Full documentation is in this file and in README.md
#

def __print_error__(string):
  """Print an error message."""
  print "*** Dhop error: %s" % (string)

class Dhop:

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
    'path': 'resolve',
    'pop': 'pop',
    'push': 'push',
    'recall': 'recall',
    'remove': 'forget',
    'resolve': 'resolve',
    'set': 'set_location',
    'unset': 'forget'
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
      os.remove(os.path.join(home_dir, DHOP_CMD_FILE))
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


  def write_store(self):
    """Write the current Dhop data to disk."""
    store_file = open(os.path.join(os.path.expanduser('~'), Dhop.DHOP_STORE), 'wb')
    cPickle.dump(self.store, store_file)

  # Copies the file(s) specified by from to the location specified by to.
  # File-globs can be used in the first argument. If to represents a directory,
  # then the file is copied to the directory, retaining its name. Otherwise, the
  # file is renamed to the name specified in to.
  def cp(self, args):
    return


  # Moves the file(s) specified by from to the location specified by to.
  # File-globs can be used in the first argument. If to represents a directory,
  # then the file is moved to the directory, retaining its name. Otherwise, the
  # file is renamed to the name specified in to.
  def mv(self, args):
    return


  # Sets a name for a specified directory path. If no path is provided, then the
  # name is set for the current directory.
  def set_location(self, args):
    """Sets a name for a specified directory path.

    Usage: dhop set <name> [path]

    A name is required. If no path is provided, then the name is set for the
    current directory."""
    if len(args) == 0:
      return

    name = args[0]
    path = ""

    if len(args) == 1 or len(args[1]) == 0:
      path = os.getcwd()
    else:
      path = self.resolve_stored_location_or_path(args[1])

    if path == None:
      __print_error__("No such location or path: %s" % (args[1]))
    else:
      self.store['locations'][name] = path
    return


  def forget(self, args):
    """Forget (delete) a named location that was previously set.

    Usage: dhop forget [location]"""

    if len(args) == 0 or len(args[0]) == 0:
      __print_error__("Can't forget nothing!")
      self.help(['forget'])
      return

    name = args[0]

    if self.store['locations'].has_key(name):
      del(self.store['locations'][name])

    return


  def mark(self, args):
    """Marks the provided path so that you can later return to it with the 'recall' command.

    Usage: dhop mark [path]

    If no path is given, then the current directory is assumed. This command
    overwrites any previous marks; there can be only one!"""
    path = ""

    if len(args) == 0 or len(args[0]) == 0:
      path = os.getcwd()
    else:
      path = self.resolve_stored_location_or_path(args[0])

    if path == None:
      __print_error__("No such location or path: %s" % (args[0]))
    else:
      self.store['mark'] = path
    return


  def recall(self, args):
    """Return to the directory that was last marked with the 'mark' command.

    Usage: dhop recall"""
    path = self.store['mark']

    if path == None or len(path) == 0:
      __print_error__("Mark is not set! Use 'mark' to set a mark.")
      self.show_help(['mark'])
    else:
      self.go([path])

    return

  def resolve(self, args):
    """Get the full path for the named location.

    Usage: dhop resolve [location]

    If location refers to a named location, its full path will be printed.

    If location refers to a path, then the full path will be printed.

    Otherwise, an error will be printed."""
    path = self.resolve_stored_location_or_path(args[0])
    if path == None or len(path) == 0:
      __print_error__("No such location: %s" % (args[0]))
    else:
      print path

  # Pushes the current working directory to the directory stack, then goes to
  # the location referenced by path.
  def push(self, args):
    """Push the current working directory onto the directory stack, then go to the named location or path.

    Usage: dhop push [location]

    If a location is not given, then the current working directory will still be
    pushed onto the stack, but no other action will be taken."""
    old_path = os.getcwd()
    path = ""

    if len(args) == 0 or len(args[0]) == 0:
      path = os.getcwd()
    else:
      path = self.resolve_stored_location_or_path(args[0])

    if path == None:
      __print_error__("No such location or path: %s" % (args[0]))
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
    """Pops the last pushed location from the stack, and then transports you to that location.

    Usage: dhop pop [all]

    Usually, this is used without specifying any arguments.

    There is one optional argument: 'all'. If specified, it pops all of the pushed
    locations from the stack, then transports you to the final location popped
    from the stack."""
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
    print ""
    for key in sorted(self.store.keys()):
      data = self.store[key]

      # if there's no data for the section, skip ahead to the next section.
      if data == None or len(data) == 0:
        continue

      # print the section heading
      print key.capitalize()
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
  def show_help(self, args):
    """Shows command-line help.

    Usage: dhop help [cmd] ...

    You can specify multiple commands after 'help' to get help on more than one
    command at a time, or specify 'all' to get detailed help on all commands.

    To get help for the 'mark', 'forget', and 'push' commands:

      dhop help mark forget push

    To get help for all commands:

      dhop help all"""

    if args == None or len(args) == 0:
      print "Dhop.py - DHOP in Python"
      print "The following commands are available:\n"

      for cmd in sorted(Dhop.USER_COMMANDS.keys()):
        print "- " + cmd

      print ""
      print self.show_help.__doc__
      print ""
    else:
      for arg in args:
        # get the function associated with the command, and print its doc string.
        if arg in Dhop.USER_COMMANDS.keys():
          print "\n%s - %s" % (arg, getattr(self, Dhop.USER_COMMANDS[arg]).__doc__)
        elif arg == 'all':
          for cmd in sorted(Dhop.USER_COMMANDS.keys()):
            print "\n%s - %s" % (cmd, getattr(self, Dhop.USER_COMMANDS[cmd]).__doc__)
        else:
          __print_error__("Unknown command: %s" % (arg))
      print ""


  def go(self, args):
    """Go (cd) to the named location (or path).

    The args parameter is a list, so to call this function with a single
    location (the normal case), enclose it with square braces:

      dhop_instance.go([path])
    """
    if len(args) != 1:
      __print_error__("You must specify one, and *only* one location to go to!")

    path = self.resolve_stored_location_or_path(args[0])

    if(path == None):
      __print_error__("Couldn't find either a stored location or a file-system path that matches:")
      __print_error__("  " + args[0])
      return False

    # OK, it looks like we're clear to *go*. Write the command file and return.
    home_dir = os.path.expanduser('~') # should work on all systems.
    f = open(os.path.join(home_dir, Dhop.DHOP_CMD_FILE), 'w')
    if os.name == 'posix':
      f.write(path)
    else: # windows?
      f.write("cd /d {}".format(path))
    f.close()

    # if we're here, it's because we're so successful!
    return True


  def resolve_stored_location_or_path(self, name):
    """Check to see if the passed-in name refers to a stored location or path. If it does, return the path.

    If it doesn't exist either as a stored location or path, this method will return `None`."""
    locations = self.store['locations']

    # if the user decorated the name with a leading '@' character, it definitely refers to a stored location.
    if name.startswith('@'):
      name = name[1:] # strip off the `@`.
      if self.store['locations'].has_key(name):
        return self.store['locations'][name]
      else:
        # If the decorated name *doesn't* refer to a stored location, don't even check to see if there's a matching
        # path.  Just return None.
        return None
    else:
      # The undecorated name *might* refer to a stored location...
      if self.store['locations'].has_key(name):
        return self.store['locations'][name]
      elif os.path.isdir(name): # Or it might be a path...
        return name
      else: # Or it could be nothing.
        return None

  def run(self, args):
    """Run the Dhop main loop"""
    # The first arg should be either a command (cp, mv, set, etc.), or a location
    # (with or without @)
    command_or_location = args[0]
    # The rest are args associated with the command.
    remaining_args = args[1:]

    path = self.resolve_stored_location_or_path(command_or_location)

    if path == None:
      # It's not a location or path, see if it's a command.
      if Dhop.USER_COMMANDS.has_key(command_or_location):
        getattr(self, Dhop.USER_COMMANDS[command_or_location])(remaining_args)
      else:
        __print_error__("The first argument is not a location, path, or command that I recognize.")
        print "Type `dhop help` for a list of commands"
        return
    else:
      self.go([path])

    self.write_store()

# ==========
# the script
# ==========

dhop = Dhop()
if len(sys.argv) < 2:
  dhop.show_help(None)
  exit()

dhop.run(sys.argv[1:])

