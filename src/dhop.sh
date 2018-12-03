#!/bin/bash
DHOPDIR=$HOME/bin
DHOP_CMD_FILE=$HOME/.dhopcmd

# Run the dhop script, passing it all of the command-line arguments.
python3 $DHOPDIR/dhop.py $@

# Once execution is finished, see if dhop wrote a location to cd to...
if [ -e $DHOP_CMD_FILE ]; then
  source $DHOP_CMD_FILE
  rm $DHOP_CMD_FILE
fi
