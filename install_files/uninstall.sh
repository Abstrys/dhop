#!/bin/bash

PATH_TO_INSTALL=$HOME/bin

if [[ $1 -ne "" ]]; then
  PATH_TO_INSTALL=$1
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

