#!/bin/bash

# See: https://stackoverflow.com/questions/630372/determine-the-path-of-the-executing-bash-script
DHOPDIR="$(dirname -- "${BASH_SOURCE[0]}")"
DHOPDIR="$(cd -- "$DHOPDIR" && pwd)"

# This is constant.
DHOP_CMD_FILE=$HOME/.dhopcmd

# Run the dhop binary, passing it all of the command-line arguments.
$DHOPDIR/abstrys-dhop $@

# Once execution is finished, see if dhop wrote a location to cd to...
if [ -e $DHOP_CMD_FILE ]; then
   source $DHOP_CMD_FILE
   rm $DHOP_CMD_FILE
fi
