#!/bin/bash

PATH_TO_INSTALL=$HOME/bin

if [[ $1 -ne "" ]]; then
  PATH_TO_INSTALL=$1
fi

echo
echo Installing dhop.py...
echo

if [ -e $PATH_TO_INSTALL ]; then
  echo Install directory already exists: $PATH_TO_INSTALL
else
  echo Creating install directory: $PATH_TO_INSTALL
  mkdir -p $PATH_TO_INSTALL
fi

echo
echo Copying files:
cp -v dhop.py $PATH_TO_INSTALL
cp -v dhop.sh $PATH_TO_INSTALL

echo
echo Be sure to add the following line to your .profile, .bashrc, or .bash_profile:
echo
echo   alias dhop=\"source $PATH_TO_INSTALL/dhop.sh\"
echo
echo Feel free to cut-and-paste the above line, since it refers to the actual
echo install location. Then, you can simply type \'dhop\' on the command-line
echo for help.
echo

