# Notes for Dhop Hackers!

If you're working on the code, you might appreciate these tips:

## The `README.md` File

If you modify the README, you will likely also want to update dhop's `help` text. To do this, see the info about [the \_\_END\_\_ block](#the-__end__-block).

## The `dhop.rb` File

### The `__END__` block

The text after the `__END__` statement, which is printed when someone types `dhop help` or simply `dhop` (with no
arguments) is exactly what you get when you run [pandoc][] with the following options:

    pandoc -f markdown -t plain -o dhop_info.txt README.md

If you make changes to the code that affect its interface or usage, make changes to README.md, and then use the
preceding command to generate the `__END__` block text.

[pandoc]: http://johnmacfarlane.net/pandoc/index.html

