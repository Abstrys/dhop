# Dhop - it takes you places!

Dhop (command name: `dhop`) is a command-line utility written in Ruby that provides a number of ways to get around your
filesystem quickly:

* marking and recalling a single, unnamed location.
* pushing and popping locations from a stack.
* naming directory locations and then recalling them by name.

All of these states are persistent and can be used even after your terminal session has finished, your computer
rebooted, etc.

## License

This software is provided under the terms of the GNU General Public License, v3. For complete info, refer to LICENSE.txt
(provided with the source code), or go to <http://www.gnu.org/licenses/gpl.html>.

> **Note**: The license does not restrict your ability to use the software itself; it affects only your ability to
> modify and use the software's *code*, or to claim ownership of it.

## Usage

**dhop** *cmd_or_location* *command_args*

Where *cmd_or_location* represents either a named location (recorded with **set**) or one of the [known
commands](#dhop-commands). Any further arguments on the command-line are considered parameters for the given command.

### Commands

**set** *name* *path*
:    Sets a name for a given directory path. If no path is given, then the current directory is assumed.

**go** *name*
:    Goes to the location previously **set**, and represented by *name*.

**forget** *name*
:    Forgets (deletes) a named location that was previously **set**.

**mark** *path*
:    Marks the provided path so you can later **recall** it to return. If the location isn't provided, the current
    directory is assumed.

> **Note**: This also overwrites any previous marks.

**recall**
:    Goes to the directory that was last **mark**ed.

**push** *path*
:    Pushes the current working directory to the directory stack, then goes to the location referenced by *path*.

**pop** *option*
:    Pops the last pushed location from the stack, and then transports you to that location.  You can set the following option:

* **all** - Pops all of the pushed locations from the stack, then transports you to the final location popped from the
  stack.

**help**
:    Prints help.

## Examples

### Example 1: Setting and returning to a named location

    $ dhop set docs ~/Documents

Then you can either use:

    $ dhop docs

or

    $ dhop go docs

to go to ~/Documents.

### Example 2: Marking and recalling a location

    $ dhop mark

marks the current directory (overwriting any previous `mark`)

    $ dhop recall

takes you back to the marked location.

### Example 3: Pushing and popping locations

    $ dhop push

pushes the current directory on the stack.

    $ dhop pop

pops the last pushed directory from the stack and transports you there.

## Special Conveniences

I've added these special conveniences because I use them.  ;)

### Using the `@` symbol

If you enter an `@` symbol at the beginning of a command, it assumes you mean `go`. So you can type:

    $ dhop @docs

This will take you to the named location 'docs'.

You can also use `@` with `push`:

    $ dhop push @docs

Which will take you to the location `docs`, but will first push the current directory onto the stack.

### Auto-interpretation of paths

If the command isn't recognized, but refers to an actual filesystem location, `dhop` will assume that you want to go there, so typing:

    $ dhop ~

will take you to your home directory (on *nix, *BSD, and Mac OS X, at least).

---
Copyright &copy; 2013, Abstrys / Eron Hennessey

