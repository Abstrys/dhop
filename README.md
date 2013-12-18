# Dhop - it takes you places!

[ [Usage](#usage) | [Examples](#examples) | [Conveniences](#special-conveniences)
| [Installing](#installing) | [License](#license) | [Problems?](#problems) ]

Dhop (command name: `dhop`) is a command-line utility written in Python that provides a number of ways to get around
your filesystem quickly:

* **set** named directory locations and then **go** to them by name.

* **push** and **pop** locations from a stack.

* **marking** and **recalling** a single, unnamed location.

Each of these states is *persistent* and can be used even after your terminal session has finished, your computer
rebooted, etc.

You can also copy and move files to any location you've named with *set*.

## Usage

**dhop** \<*cmd_or_location_or_path*\> \[*command_args*\]

Where *cmd_or_location* represents either a named location (recorded with **set**) or one of the [known
commands](#dhop-commands). Any further arguments on the command-line are considered parameters for the given command.

### Commands

**cp** \<*from*\>, \<*to*\>
:    Copies the file(s) specified by *from* to the location specified by *to*. File-globs can be used in the first
    argument. If *to* represents a directory, then the file is copied to the directory, retaining its name. Otherwise,
    the file is renamed to the name specified in *to*.

**mv** \<*from*\>, \<*to*\>
:    Moves the file(s) specified by *from* to the location specified by *to*. File-globs can be used in the first
    argument. If *to* represents a directory, then the file is moved to the directory, retaining its name. Otherwise,
    the file is renamed to the name specified in *to*.

**set** \<*name*\> \[*path*\]
:    Sets a name for a specified directory path. If no path is provided, then the name is set for the current directory.

**forget** \<*name*\>
:    Forgets (deletes) a named location that was previously **set**.

**mark** \[*path*\]
:    Marks the provided path so you can later **recall** it to return. If the location isn't provided, the current
    directory is assumed. *This also overwrites any previous marks.*

**recall**
:    Goes to the directory that was last **mark**ed.

**push** \<*path*\>
:    Pushes the current working directory to the directory stack, then goes to the location referenced by *path*.

**pop** \[*option*\]
:    Pops the last pushed location from the stack, and then transports you to that location.  You can set the following
    option:

  * **all** - Pops all of the pushed locations from the stack, then transports you to the final location popped from
    the stack.

**help**
:    Prints help.

## Examples

### Example 1: Setting and returning to a named location

~~~~sh
dhop set docs ~/Documents
~~~~

Then you can either use:

~~~~sh
dhop docs
~~~~

or

~~~~sh
dhop go docs
~~~~

to go to ~/Documents.

### Example 2: Marking and recalling a location

~~~~sh
dhop mark
~~~~

marks the current directory (overwriting any previous `mark`)

~~~~sh
dhop recall
~~~~

takes you back to the marked location.

### Example 3: Pushing and popping locations

~~~~sh
dhop push
~~~~

pushes the current directory on the stack.

~~~~sh
dhop pop
~~~~

pops the last pushed directory from the stack and transports you there.

## Special Conveniences

I've added these special conveniences because I use them.  ;)

### Using the `@` symbol

If you enter an `@` symbol at the beginning of a command, it assumes you mean `go`. So you can type:

~~~~sh
dhop @docs
~~~~

This will take you to the named location 'docs'.

You can also use `@` with `push`:

~~~~sh
dhop push @docs
~~~~

Which will take you to the location `docs`, but will first push the current
directory onto the stack.

### Auto-interpretation of paths

If the command isn't recognized, but refers to an actual filesystem location,
`dhop` will assume that you want to go there, so typing:

~~~~sh
dhop ~
~~~~

will take you to your home directory--well, on *nix, *BSD, and Mac OS X, at least.

> **Note**: If you use `dhop` on Windows, you may want to go to where your "home" is and type:
>
>     dhop set ~
>
> then, just as you would on Linux, you can use `dhop ~` to get home. Neat, eh?

### Copying and moving files

Using `dhop cp` or `dhop mv` will allow you to move files from the current
directory to a named location or path. You can copy or move either a single
file or a group of files specified with a file-glob. For example:

~~~~sh
dhop mv *.md @notes
~~~~

moves all of the files ending with `.md` to the location marked by the name "notes".


## Installing

1. You must have [Python][] on your system. I've tested this with Python 2.7.5.

2. Get the sources. You can either use git:

        git clone https://github.com/Abstrys/dhop.git

    or download the .zip: <https://github.com/Abstrys/dhop/archive/master.zip>

3. Run either `install.sh` or `install.bat` depending on your platform. Here's
    an example run using `install.sh` on Mac OS X:

        ./install.sh
        Installing dhop.py...

        Install directory already exists: /Users/eronh/bin

        Copying files:
        dhop.py -> /Users/eronh/bin/dhop.py
        dhop.sh -> /Users/eronh/bin/dhop.sh

        Be sure to add the following line to your .profile, .bashrc, or .bash_profile:

        alias dhop="source /Users/eronh/bin/dhop.sh"

        Feel free to cut-and-paste the above line, since it refers to the actual
        install location. Then, you can simply type 'dhop' on the command-line
        for help.

4. If you used `install.sh` (Linux, Mac, BSD, etc.), you'll also need to add
    a line to your profile (either `~/.bashrc`, `~/.bash_profile`, or
    `~/.profile` depending on your system), such as:

        alias dhop="source /Users/eronh/bin/dhop.sh"

    Invoking `dhop` with `source` is necessary to allow `dhop` to change your
    working directory in your shell session.

5. Once installed, test it out by typing `dhop help`.

## License

This software is provided with a free distribution license under the terms of
the BSD "3 clause" public license. For complete info, refer to LICENSE.txt
(provided with the source code), or go to
<http://opensource.org/licenses/BSD-3-Clause>.

## Problems?

You know that this software comes with *no warranty*, right? Refer to the
[license](#license) if you have any concerns about this.

Well, given that--there are avenues available to alert me of any problems with `dhop`:

* You can log an issue on GitHub: <https://github.com/Abstrys/dhop/issues>
* You can email me at: <eron@abstrys.com>

[python]: http://www.python.org/
