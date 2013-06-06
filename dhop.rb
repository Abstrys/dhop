# A command-line utility for hopping around the filesystem.
#
# Copyright (C) 2013, Abstrys / Eron Hennessey
#
# This file is released under the terms of the GNU General Public License, v3.
# For details about this license, see LICENSE.txt or go to
# http://www.gnu.org/licenses/gpl.html
#
# Full documentation is in this file (run yard doc to generate it) and in README.md
#
module Abstrys
  class DirHop

     @@DHOP_CMD_FILE = '.dhopcmd'
     @@DHOP_STORE = '.dhoprb'

     # Gives a name to a filesystem path.
     #
     # @param name
     #   The name to assign a path to. This must be only one alpha-numeric word;
     #   no whitespace or special characters are allowed. Additionally, the name
     #   should not be any of the following:
     #
     #   * set, go, forget, mark, recall, push, pop, help
     #
     #   When run from the command-line, you can simply type `dhop docs` to go
     #   to the location with the name 'docs'. If your name conflicts with a known
     #   command, however, you'll need to add the `go` command to your
     #   command-line, such as:
     #
     #       $ dhop go mark
     #
     #   This command will go to the location stored with the name 'mark', and not
     #   to the location stored by the `mark` command. Because much confusion can
     #   arise from this, it's recommended to simply not use any of the names used
     #   by the commands.
     #
     # @param path
     #   The path to assign to the name. If no path is given, the current
     #   directory is assumed.
     #
     def set(name, path = nil)

       if path == nil || path == ""
         path = Dir.pwd
       end

       if Dir.exists?(path)
         @store[:locations][name.to_sym] = File.expand_path(path) # store full paths
       else
         raise "Invalid location: #{path}"
       end
     end

     # Goes to the location represented by the name.
     #
     # @param name
     #   The name of the stored location to go to.  If there is no such name, then
     #   an error will be generated.
     #
     def go(name)
       dir = @store[:locations][name.to_sym]
       if(dir != nil)
         write_cmd_path(dir)
       else
         raise "No such stored location: #{name}"
       end
     end

     # Writes the path to the DHOP_CMD_FILE, which can be used by the wrapper
     # script to actually change the directory.
     #
     # @param cmd_path
     #   The path to chdir to after execution of this script has completed.
     #
     def write_cmd_path(cmd_path)
       file = File.open(@cmd_path_file, 'w')
       file.puts cmd_path
       file.close
     end

     # Forget the named location. This removes the location from the saved list of
     # known locations. If there is no such location, then nothing occurs.
     #
     # @param name
     #   The name of the location to forget.
     #
     def forget(name)
       if(@store[:locations][name.to_sym] != nil)
         @store[:locations].delete(name.to_sym)
       end
     end

     # Mark a directory so that you can return to it with the {#recall} method. If
     # a previous mark exists, it is overwritten.
     #
     # @param path
     #   The path to mark. If this is empty, the current directory is assumed.
     #
     def mark(path = nil)

       if path == nil || path == ""
          path = Dir.pwd
       end

       if Dir.exists?(path)
         @store[:mark] = File.expand_path(path)
       else
         raise "Invalid location: #{path}"
       end
     end

     # Goes to the location that was previously marked by the {#mark} method.
     #
     def recall
       if @store[:mark] != nil
         path = @store[:mark]
         if Dir.exists?(path)
           write_cmd_path(path)
         else
           raise "A location is stored in :mark, but it is currently invalid: #{path}"
         end
       else
         raise "Nothing is currently stored in :mark. You must mark a path before you can recall it!"
       end
     end

     # Pushes a path onto the persistent path stack.
     #
     # @param path
     #   The path to push. if no value is supplied, the current directory is assumed.
     def push(path = nil)
       if path == nil || path == ""
          path = Dir.pwd
       end

       @store[:stack].push(Dir.pwd)

       if Dir.exists?(path)
         write_cmd_path(path)
       else
         raise "Invalid location: #{path}"
       end
     end

     # Pops the last {#push}ed path from the persistent path stack.
     #
     # @param mod
     #   A modifier for the pop method. The following modifiers can be used:
     #
     #   * 'all' - pops all entries from teh persistent path stack, and changes to the final entry.
     #
     def pop(mod = nil)
       if mod == 'all'
         path = @store[:stack].last
         @store[:stack] = []
         return
       elsif mod != nil
         raise "Unknown option for pop: #{mod}"
         return
       end

       if @store[:stack] != nil && @store[:stack].length > 0
         path = @store[:stack].pop
         if Dir.exists?(path)
           write_cmd_path(path)
         else
           raise "A location was popped, but it is currently invalid: #{path}"
         end
       else
         raise "Nothing currently stored in the location stack. You must push a path before you can pop."
       end
     end

     # Prints some help.
     def help
       line_count = 0
       DATA.each_line do | line |
         puts line
         line_count += 1
         if line_count > 24
           print '<Press \'return\' to continue...>'
           x = gets
           line_count = 0
         end
       end
     end

     # Creates a new instance of the DirHop class, with an empty store.
     #
     def initialize
       @cmd_path_file = "#{Dir.home}/#{@@DHOP_CMD_FILE}"
       @store_path = "#{Dir.home}/#{@@DHOP_STORE}"

       # remove the existing cmd_path_file if it exists. It should only be there
       # if we need to change the command path upon exit.
       if File.exists?(@cmd_path_file)
         File.delete(@cmd_path_file)
       end

       # Setup the default store (empty)
       @store = { :locations => {}, :stack => [], :mark => nil }
       # If there's information in the store, load it.
       if File.exists?(@store_path)
         read_store
       end
     end

    # Reads options from the file store.
    def read_store
      if File.exists?(@store_path)
        @store = Marshal::load(File.read(@store_path))
      end
    end

    # Writes options to the file store.
    def write_store
      file = File.open(@store_path, 'w')
      file.print(Marshal::dump(@store))
      file.close
    end

    # writes any necessary changes to the persistent store and exits exexution.
    def shutdown
      write_store
      exit
    end

    # Dumps the current values of everything in @store.
    # @!visibility private
    def dump
      puts @store
    end

    # Runs the command-line interface.
    def run
      if(ARGV.length == 0)
        help
        exit
      end

      cmd = ARGV.shift
      case cmd
      when 'help', 'recall', 'dump'
        self.send(cmd.to_sym)
      when 'set', 'go', 'forget', 'mark', 'push', 'pop'
        self.send(cmd.to_sym, *ARGV)
      else
        if @store[:locations][cmd.to_sym] != nil
          go(cmd)
        else
          raise "Unknown command: #{cmd}"
        end
      end

      shutdown

    rescue Exception => e
      if(e.message != 'exit')
        puts "Error: #{e.message}"
      end
    end
  end
end

Abstrys::DirHop.new.run

__END__

Dhop - it takes you places!
===========================

DirHop (command name: dhop) is a command-line utility written in Ruby
that provides a number of ways to get around your filesystem quickly:

-   marking and recalling a single, unnamed location.
-   pushing and popping locations from a stack.
-   naming directory locations and then recalling them by name.

All of these states are persistent and can be used even after your
terminal session has finished, your computer rebooted, etc.

License
-------

This software is provided under the terms of the GNU General Public
License, v3. For complete info, refer to LICENSE.txt provided with the
source code, or go to http://www.gnu.org/licenses/gpl.html for full
information about the license.

  Note: The license does not restrict your ability to use the software
  itself; it affects only your ability to modify and use the software's
  code, or to claim ownership of it.

Usage
-----

dhop cmd_or_location command_args

Where cmd_or_location represents either a named location (recorded with
set) or one of the known commands. Any further arguments on the
command-line are considered parameters for the given command.

Commands

set name path
    Sets a name for a given directory path. If no path is given, then
    the current directory is assumed.

go name
    Goes to the location previously set, and represented by name.

forget name
    Forgets (deletes) a named location that was previously set.

mark path
    Marks the provided path so you can later recall it to return. If the
    location isn't provided, the current directory is assumed.

  Note: This also overwrites any previous marks.

recall
    Goes to the directory that was last marked.

push path
    Pushes the current working directory to the directory stack, then
    goes to the location referenced by path.

pop option
    Pops the last pushed location from the stack, and then transports
    you to that location. You can set the following option:

-   all - Pops all of the pushed locations from the stack, then
    transports you to the final location popped from the stack.

help
    Prints help.

Examples
--------

Example 1: Setting and returning to a named location

    $ dhop set docs ~/Documents

Then you can either use:

    $ dhop docs

or

    $ dhop go docs

to go to ~/Documents.

Example 2: Marking and recalling a location

    $ dhop mark

marks the current directory (overwriting any previous mark)

    $ dhop recall

takes you back to the marked location.

Example 3: Pushing and popping locations

    $ dhop push

pushes the current directory on the stack.

    $ dhop pop

pops the last pushed directory from the stack and transports you there.

* * * * *

Copyright © 2013, Abstrys / Eron Hennessey

