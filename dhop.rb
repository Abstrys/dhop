require 'yaml' # only needed by the dump method
require 'rbconfig' # to find the host OS.
require 'curses'
require 'fileutils' # for `cp` and `mv`.

module Abstrys
  # A command-line utility for hopping around the filesystem.
  #
  # Copyright (C) 2013, Abstrys / Eron Hennessey
  #
  # This file is released under the terms of the GNU General Public License, v3.
  # For details about this license, see LICENSE.txt or go to
  # <http://www.gnu.org/licenses/gpl.html>
  #
  # Full documentation is in this file (run yard doc to generate it) and in
  # README.md
  #
  class Dhop

    @@DHOP_CMD_FILE = '.dhopcmd'
    @@DHOP_STORE = '.dhop'

    #
    # ** DHOP COMMANDS **
    #
    # The user can type the names of these methods on the dhop command-line.
    # Arguments typed on the command-line will be passed as arguments to the
    # method. See the `run` method for details.
    #
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

    def process_cp_or_mv_args(*args)

      if args.length < 2
        raise "you must specify at least two arguments!"
      end

      # take the last argument to be the name or location to copy to. All of the
      # rest of the arguments comprise the list of files to copy.
      name = args.slice!(-1)
      path_or_glob = args

      if name[0] == '@'
        # chop off the `@` and use this as the name
        name = (name[1..-1])
      end
      dir = @store[:locations][name.to_sym]
      if(dir == nil)
        # assume that *name* is actually a path_or_glob.
        if Dir.exists?(name)
          dir = name
        else
          raise "#{name} does not refer to a stored location or path."
        end
      end

      return [path_or_glob, dir]
    end

    # Copies a file from the given path to a named location.
    def cp(*args)
      cp_args = process_cp_or_mv_args(*args)
      FileUtils.cp_r(cp_args[0], cp_args[1])
    end

    # Copies a file from the given path to a named location.
    def mv(*args)
      mv_args = process_cp_or_mv_args(*args)
      FileUtils.mv(mv_args[0], mv_args[1])
    end

    # Writes the path to the `@cmd_path_file`, which can be used by the wrapper
    # script to actually change the directory.
    #
    # @param cmd_path
    #   The path to chdir to after execution of this script has completed.
    #
    def write_cmd_path(cmd_path)
      file = ""
            # make sure the path is expanded
            cmd_path = File::expand_path(cmd_path)

            # we need to do something slightly different on Windows.
            if @host_os == :windows
                file = File.open("#{@cmd_path_file}.bat", 'w')
                file.print "cd /d #{cmd_path}"
          else
                file = File.open(@cmd_path_file, 'w')
                file.print cmd_path
            end
      file.close
    end

    # Forget the named location. This removes the location from the saved list
    # of known locations. If there is no such location, then nothing occurs.
    #
    # @param name
    #   The name of the location to forget.
    #
    def forget(name)
      if(@store[:locations][name.to_sym] != nil)
        @store[:locations].delete(name.to_sym)
      end
    end

    # Mark a directory so that you can return to it with the {#recall} method.
    # If a previous mark exists, it is overwritten.
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
    #   The path to push. if no value is supplied, the current directory is
    #   assumed. You can also substitute a named location by prepending the
    #   value with the `@` symbol.
    #
    # @example Calling push to go to the directory `documents`.
    #   dhop push documents
    #
    # @example Calling push to go to the stored location `documents`.
    #   dhop push @documents
    #
    def push(path = nil)
      if path == nil || path == ""
        path = Dir.pwd
      end

      @store[:stack].push(Dir.pwd)

      if path[0] == '@'
        # chop off the `@` and go.
        go(path[1..-1])
        return
      end

      if Dir.exists?(path)
        write_cmd_path(path)
      else
        # Special bonus feature. If the path is not recognized, but matches a
        # known location, go to that location instead. Since we pushed the
        # current directory anyway, if this isn't what we want we can always get
        # back by popping.
        dir = @store[:locations][path.to_sym]
        if(dir.nil?)
          raise "Invalid location: #{path}"
        else
          go(path)
        end
      end
    end

    # Pops the last {#push}ed path from the persistent path stack.
    #
    # @param mod
    #   A modifier for the pop method. The following modifiers can be used:
    #
    #   * 'all' - pops all entries from teh persistent path stack, and changes
    #       to the final entry.
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

    # Lists the contents of the current store in a pleasant way (as opposed to
    # {#dump}).
    #
    # @param (String) key
    #   The key used to limit the results ('locations', 'stack', or 'mark').
    #
    def list(key = nil)
      puts ""
      @store.each do | section |
        # show the section title.
        title = "#{section[0]}".capitalize

        # if there's no data for the section, skip ahead to the next section.
        if section[1].nil? || section[1] == [] || section[1] == {} || section[1] == ''
          next
        end

        # the output depends on the type of section it is.
        case title
          when 'Locations'
            puts title
            puts title.gsub(/./, '=')
            section[1].sort.each do | subsection |
              puts "#{subsection[0]}: #{subsection[1]}"
            end
          when 'Stack'
            puts title
            puts title.gsub(/./, '=')
            stack_pos = 1
            section[1].reverse.each do | subsection |
              puts "#{stack_pos}. #{subsection}"
              stack_pos += 1
            end
          when 'Mark'
            puts "#{title}: #{section[1]}"
        end
        puts ""
      end
    end

    # Prints some help.
    def help
      line_count = 0
      DATA.each_line do | line |
        puts line
#        line_count += 1
#        if line_count > 24
#          print '[Press any key to continue...]'
#          line_count = 0
#        end
      end
    end

    #
    # ** NON-COMMANDS **
    #
    # These are used by dhop itself, and not by the user.
    #

    # Creates a new instance of the Dhop class, with an empty store.
    #
    def initialize
      @host_os = find_host_os
            if @host_os == :windows
                home = Dir.home
                if(home[0] == '"') # sometimes, this might have quotes around it.
                    home = home[1..-2]
                end
                @cmd_path_file = "#{home}/#{@@DHOP_CMD_FILE}"
                @store_path = "#{home}/#{@@DHOP_STORE}"
            else
                @cmd_path_file = "#{Dir.home}/#{@@DHOP_CMD_FILE}"
                @store_path = "#{Dir.home}/#{@@DHOP_STORE}"
            end

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
      @store = Marshal::load(File.read(@store_path))
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

    # Dumps the current store in yaml
    # @!visibility private
    def dump
      puts @store.to_yaml
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
      when 'set', 'go', 'forget', 'mark', 'push', 'pop', 'list', 'cp', 'mv'
        self.send(cmd.to_sym, *ARGV)
      else
        if cmd[0] == '@'
          # if the command is preceded by an '@' symbol, it's assumed to be a
          # location.
          go(cmd[1..-1])
        elsif @store[:locations][cmd.to_sym] != nil
          go(cmd)
        elsif Dir.exists?(cmd)
          # Another bit of convenience. If the command isn't recognized, but
          # matches a valid directory path, assume that the user wanted to go
          # there.
          write_cmd_path(cmd)
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

    # Finds the host operating system.
    #
    # @return [:windows,:linux,:macosx]
    #   The detected host OS.
    #
    def find_host_os
      host = RbConfig::CONFIG['host_os'].downcase
      if host =~ /^mingw.*|^win.*/
        return :windows
      else
        return :linux
      end
    end
  end
end

Abstrys::Dhop.new.run

__END__

Dhop - it takes you places!
===========================

Dhop (command name: dhop) is a command-line utility written in Ruby that
provides a number of ways to get around your filesystem quickly:

-   set named directory locations and then go to them by name.

-   push and pop locations from a stack.

-   marking and recalling a single, unnamed location.

Each of these states is persistent and can be used even after your
terminal session has finished, your computer rebooted, etc.

You can also copy and move files to any location you've named with set.

Usage
-----

dhop <cmd_or_location_or_path> [command_args]

Where cmd_or_location represents either a named location (recorded with
set) or one of the known commands. Any further arguments on the
command-line are considered parameters for the given command.

Commands

cp <from>, <to>
    Copies the file(s) specified by from to the location specified by
    to. File-globs can be used in the first argument. If to represents a
    directory, then the file is copied to the directory, retaining its
    name. Otherwise, the file is renamed to the name specified in to.

mv <from>, <to>
    Moves the file(s) specified by from to the location specified by to.
    File-globs can be used in the first argument. If to represents a
    directory, then the file is moved to the directory, retaining its
    name. Otherwise, the file is renamed to the name specified in to.

set <name> [path]
    Sets a name for a specified directory path. If no path is provided,
    then the name is set for the current directory.

go <name>
    Goes to the location previously set, represented by name.

forget <name>
    Forgets (deletes) a named location that was previously set.

mark [path]
    Marks the provided path so you can later recall it to return. If the
    location isn't provided, the current directory is assumed. This also
    overwrites any previous marks.

recall
    Goes to the directory that was last marked.

push <path>
    Pushes the current working directory to the directory stack, then
    goes to the location referenced by path.

pop [option]
    Pops the last pushed location from the stack, and then transports
    you to that location. You can set the following option:

-   all - Pops all of the pushed locations from the stack, then
    transports you to the final location popped from the stack.

help
    Prints help.

