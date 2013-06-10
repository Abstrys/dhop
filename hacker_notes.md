# Notes for Dhop Hackers!

If you're working on the code, you might appreciate these tips:

## The `README.md` File

If you modify the README, you will likely also want to update dhop's `help` text. To do this, see the info about [the
\_\_END\_\_ block](#the-__end__-block).

## The `dhop.rb` File

### The `__END__` block

The text after the `__END__` statement, which is printed when someone types `dhop help` or simply `dhop` (with no
arguments) is mostly what you get when you run [pandoc][] with the following options:

    pandoc -f markdown -t plain -o dhop_info.txt README.md

If you make changes to the code that affect its interface or usage, make changes to `README.md`, and then use the
preceding command to generate the `__END__` block text.

After pasting the `__END__` block test, snip out the information about installing dhop. Obviously, if they have the
program running they've installed it. :P

## The `dhop.sh` and `dhop.bat` files

These files, that invoke `dhop.rb`, are necessary because dhop runs in its own process space: any changes it makes to
the current working directory are made only within dhop's own context, and not the user's. However, it *can* write
a file (a memory), and an external process (the .sh file) can read that file (remembering the deceased process' desire
of what to do). This is essentially what's happening here:

* Dhop.rb writes the location to `cd` to in the .dhopcmd file.
* Dhop.sh, which was invoked with `source` (on Linux/Unix/BSD/Mac OS X) changes the current working directory in the
user's terminal session to the one read from .dhopcmd.

On Windows, the process is similar, but slightly different:

* Dhop.rb writes the entire `cd` command, including the location to move to, in the .dhopcmd.bat file.
* Dhop.bat `call`s that batchfile, executing it in the user's cmd session.

[pandoc]: http://johnmacfarlane.net/pandoc/index.html

