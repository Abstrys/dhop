.. Copyright © 2018, Eron Hennessey

##########
Using Dhop
##########

.. only:: html

   .. contents::
      :local:

   A guide to running :command:`dhop` commands.

Usage
=====

There are two basic ways to use :command:`dhop`:

* :ref:`usage-location`
* :ref:`usage-command`


.. _usage-location:

Go to a named location
----------------------

To return to any location that you've :option:`set`, run:

.. parsed-literal::

   dhop <\ :samp:`{location_name}`\ >

You can optionally add path elements after the location name so, for example, you can easily specify
sub-directories of the location::

    dhop location1/some/subdir

Additionally, you can also use :command:`dhop` just like :command:`cd`::

    dhop some/path/somewhere


.. _usage-command:

Run dhop commands
-----------------

Commands are used to manipulate :command:`dhop`\ 's locations, and are run as:

.. parsed-literal::

    dhop <\ :ref:`command <dhop-commands>`\ > [\ :samp:`{command_args}`\ ]

Where *command* is one of the supported :ref:`commands <dhop-commands>`. Any further arguments on
the command-line are considered parameters for the given *command*.

.. _dhop-commands:

Commands
========

.. option:: cp <from> <to>

   Copies the file(s) specified by *from* to the location specified by *to*. File-globs can be used
   in the first argument. If *to* represents a directory, then the file is copied to the directory,
   retaining its name. Otherwise, the file is renamed to the name specified in *to*.

.. option:: mv <from>, <to>

   Moves the file(s) specified by *from* to the location specified by *to*. File-globs can be used
   in the first argument. If *to* represents a directory, then the file is moved to the directory,
   retaining its name. Otherwise, the file is renamed to the name specified in *to*.

.. option:: set <name> [path]

   Sets a name for a specified directory path. If no path is provided, then the name is set for the
   current directory.

.. option:: forget <name>

   Forgets (deletes) a named location that was previously :option:`set`.

.. option:: mark [path]

   Marks the provided path so you can later :option:`recall` it to return. If the location isn't
   provided, the current directory is assumed. *This also overwrites any previous marks.*

.. option:: recall

   Goes to the directory that was last marked.

.. option:: path <location_or_path>

   Prints the path of the given :option:`set` location.

.. option:: push <path>

   Pushes the current working directory to the directory stack, then goes to the location referenced
   by *path*.

.. option:: pop [option]

   Pops the last pushed location from the stack, and then transports you to that location.  You can
   set the following option:

   .. option:: all

      Pops all of the pushed locations from the stack, then transports you to the final location
      popped from the stack.

.. option:: help [command]

   Prints help. You can supply an optional command argument (ex: "pop", "recall", etc.) to get help
   for that command.

Examples
========

Setting and returning to a named location
-----------------------------------------

::

 dhop set docs ~/Documents

Then you can either use::

 dhop docs

or::

 dhop go docs

to go to ~/Documents.


Marking and recalling a location
--------------------------------

::

 dhop mark

marks the current directory (overwriting any previous *mark*)

::

 dhop recall

takes you back to the marked location.


Pushing and popping locations
-----------------------------

::

 dhop push

pushes the current directory on the stack.

::

 dhop pop

pops the last pushed directory from the stack and transports you there.


Special Conveniences
====================

I've added these special conveniences because I use them.  ;)


Auto-interpretation of paths
----------------------------

If the command isn't recognized, isn't the name of a :option:`set` location, but refers to an actual
filesystem location, `dhop` will assume that you want to go there, so typing::

 dhop ~

which will take you to your home directory—well, on \*nix, \*BSD, and Mac OS X, at least.

.. note:: If you use `dhop` on Windows, you may want to go to where your "home" is and type::

        dhop set ~

    then, just as you would on Linux, you can use `dhop ~` to get home. Neat, eh?


Copying and moving files
------------------------

Using ``dhop cp`` or ``dhop mv`` will allow you to move files from the current directory to a named
location or path. You can copy or move either a single file or a group of files specified with a
file-glob. For example::

 dhop mv *.md notes

moves all of the files ending with ``.md`` to the location marked by the name "notes".

