#!/bin/bash

if [[ $# -eq 1 ]]; then
  PATH_TO_INSTALL=$1
elif [[ -e "$HOME/.local/gtif/bin/" ]] then
  PATH_TO_INSTALL="$HOME/.local/bin"
else
  PATH_TO_INSTALL=$HOME/bin
fi

echo
echo Uninstalling dhop. 😾
echo

if [ -e $PATH_TO_INSTALL ]; then
   echo Install directory exists: $PATH_TO_INSTALL
   echo
   echo Removing files:
   rm -v $PATH_TO_INSTALL/abstrys-dhop 
   rm -v $PATH_TO_INSTALL/dhop

   echo
   echo Done!
else
   echo Nothing to do!
fi

