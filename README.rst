###########################
Dhop - it takes you places!
###########################

[ Usage_ | Commands_ | Examples_ | `Special conveniences`_ | Installing_ | License_ | Issues_ ]

.. code:: sh

   DHOP='Dhop helps organize paths'

Dhop (command name: **`dhop`**) is a command-line utility that provides a number of ways to get
around your filesystem quickly:

* **set** named directory locations and then **go** to them by name.

* **push** and **pop** locations from a stack.

* **marking** and **recalling** a single, unnamed location.

Each of these states is *persistent* and can be used even after your terminal session has finished,
your computer rebooted, etc.


Usage
=====

.. code:: console

   dhop <cmd_or_location_or_path> [command_args]

Where `<cmd_or_location>` represents either a named location (recorded with **`set`**) or one of the
known commands. Any further arguments on the command-line are considered parameters for the given
command.


Commands
========

set
---

.. code:: sh

   set <name> [path]

Sets a name for a specified directory path. If no path is provided, then the name is set for the
current directory.


go
--

.. code:: sh

   dhop go <name>

Go to a specified named location that was previously **`set`**.


forget
------

.. code:: sh

   dhop forget <name>

Forgets (deletes) a named location that was previously **`set`**.


mark
----

.. code:: sh

   dhop mark [path]

Marks the provided path so you can later **recall** it to return. If the location isn't provided,
the current directory is assumed. *This also overwrites any previous marks.*


recall
------

.. code:: sh

   dhop recall [--peek]

Goes to the directory that was last marked. You can use ``--peek`` to look at the value without
going there.


push
----

.. code:: sh

   dhop push <path>

Pushes the current working directory to the directory stack, then goes to the location referenced by
`<path>`.


pop
---

.. code:: sh

   dhop pop [--all] [--peek]

Pops the last pushed location from the stack, and then transports you to that location. You can use
the following flags to modify its behavior:

* `--all` - Pops all of the pushed locations from the stack, then transports you to the final location
  popped from the stack, unless `--peek` is used.

* `--peek` - Print the last value (or first, if ``--all`` is used) on the stack. Does not pop any
  values from the stack, nor does it transport you anywhere.


shell-complete
--------------

.. code:: sh

   dhop shell-complete [--shell <shell_name>] [--dir <dir_path>]

Generates a shell completion script. By default, the script will be generated for the current shell
and placed in ``~/.local/share/dhop/`` if a ``.local/share/`` directory exists, or within the
current directory if it doesn't. The script will be named ``dhop.<shell_name>`` (for example,
``dhop.bash`` for the bash shell).

Alternatively, the ``--shell`` and ``--dir`` flags can be used to set the shell name and directory
name, respectively.

The currently-supported shells are: ``bash``, ``elvish``, ``fish``, ``powershell``, and ``zsh``.


help
----

.. code:: sh

   dhop help

Prints help.


Examples
========

Example 1: Setting and returning to a named location
----------------------------------------------------

.. code:: sh

   dhop set docs ~/Documents

Then you can either use:

.. code:: sh

   dhop docs

or:

.. code:: sh

   dhop go docs

to go to `~/Documents`.


Example 2: Marking and recalling a location
-------------------------------------------

.. code:: sh

   dhop mark

Marks the current directory (overwriting any previous *mark*).

.. code:: sh

   dhop recall

Takes you back to the marked location.


Example 3: Pushing and popping locations
----------------------------------------

.. code:: sh

   dhop push

Pushes the current directory on the stack.

.. code:: sh

   dhop pop

Pops the last pushed directory from the stack and transports you there.


Special conveniences
====================

I've added these special conveniences because I use them.  ;)

Auto-interpretation of paths
----------------------------

If the command isn't recognized, but refers to an actual filesystem location, `dhop` will assume
that you want to go there, so typing:

.. code:: sh

   dhop ~

which will take you to your home directory--well, on \*nix, \*BSD, and Mac OS X, at least.

.. note:: If you use `dhop` on Windows, you may want to go to where your "home" is and type:

   .. code:: sh

      dhop set ~

   then, just as you would on Linux, you can use `dhop ~` to get home. Neat, eh?


Installing
==========

.. _install-from-archive:

Using an official archive
-------------------------

#. Unpack the archive, then run the ``install.sh`` script within it:

   .. code:: sh

      tar xzvf abstrys-dhop-linux.tar.gz
      cd abstrys-dhop-linux
      ./install.sh

   By default, it will install ``dhop`` in ``~/.local/bin/`` if it exists. If it doesn't, then it'll
   use ``~/bin/`` (and will create that directory if it doesn't exist yet).

   You can also specify an install directory of your own (it should be in your ``PATH``) by passing
   it as an argument to ``install.sh``:

   .. code:: sh

      ./install.sh /my/custom/bin/

#. The install script will let you know what to do next::

      Be sure to add the following line to your .profile, .bashrc, or .bash_profile:

      alias dhop="source /home/eron/bin/dhop.sh"

      Feel free to cut-and-paste the above line, since it refers to the actual
      install location. Then, you can simply type 'dhop --help' on the command-line
      for help.

   Add that line to your shell startup script or if you just want to test it
   out, directly into your current terminal session:

   .. code:: sh

      alias dhop="source /home/eron/bin/dhop.sh"

#. To confirm installation, try running:

   .. code:: sh

      dhop help


.. _install-from-source:

Building from source
--------------------

If you want to build ``dhop`` yourself, you'll need both ``cargo`` and
``rustc``. If you are already set up for Rust development, then:

#. Download the source from GitHub:

   .. code:: sh

      git clone https://github.com/Abstrys/dhop.git

#. Run the ``package.sh`` script within the package root:

   .. code:: sh

      cd dhop
      ./package.sh

#. Go into the ``dist/abstrys-dhop-linux`` directory, and run the ``install.sh``
   script there:

   .. code:: sh

      cd dist/abstrys-dhop-linux/
      ./install.sh

#. The same details apply at this point as when `installing from an archive
   <install-from-archive_>`_.


License
=======

This software is provided with a free distribution license under the terms of the BSD "3 clause"
public license. For complete info, refer to ``LICENSE.txt`` (provided with the source code), or go
to http://opensource.org/licenses/BSD-3-Clause.


Issues
======

You know that this software comes with *no warranty*, right? Refer to the license if you have any
concerns about this.

Well, given that—there are avenues available to alert me of any problems with **dhop**:

* You can log an issue on GitHub: https://github.com/Abstrys/dhop/issues
* You can email me at: eron@abstrys.com

