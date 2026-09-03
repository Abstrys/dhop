#!/bin/bash

if [[ $# -eq 1 ]]; then
  PATH_TO_INSTALL=$1
elif [[ -e "$HOME/.local/bin/" ]] then
  PATH_TO_INSTALL="$HOME/.local/bin"
else
  PATH_TO_INSTALL=$HOME/bin
fi

echo
echo Installing dhop! 😸
echo

if [ -e $PATH_TO_INSTALL ]; then
  echo Install directory already exists: $PATH_TO_INSTALL
else
  echo Creating install directory: $PATH_TO_INSTALL
  mkdir -p $PATH_TO_INSTALL
fi

echo
echo Copying files:
cp -rv bin/* $PATH_TO_INSTALL/

echo
echo Be sure to add the following line to your .profile, .bashrc, or .bash_profile:
echo
echo   alias dhop=\"source $PATH_TO_INSTALL/dhop.sh\"
echo
echo Feel free to cut-and-paste the above line, since it refers to the actual
echo install location. Then, you can simply type \'dhop --help\' on the command-line
echo for help.
echo
