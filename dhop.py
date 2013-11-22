# A command-line utility for hopping around the filesystem.
#
# Copyright (C) 2013, Abstrys / Eron Hennessey
#
# This file is released under the terms of the GNU General Public License, v3.
# For details about this license, see LICENSE.txt or go to
# <http://www.gnu.org/licenses/gpl.html>
#
# Full documentation is in this file (run yard doc to generate it) and in
# README.md
#

#
# ** DHOP COMMANDS **
#
# The user can type the names of these methods on the dhop command-line.
# Arguments typed on the command-line will be passed as arguments to the
# method. See the `run` method for details.
#
# Gives a name to a filesystem path.
#
# @param name
#   The name to assign a path to. This must be only one alpha-numeric word;
#   no whitespace or special characters are allowed. Additionally, the name
#   should not be any of the following:
#
#   * set, go, forget, mark, recall, push, pop, help
#
#   When run from the command-line, you can simply type `dhop docs` to go
#   to the location with the name 'docs'. If your name conflicts with a known
#   command, however, you'll need to add the `go` command to your
#   command-line, such as:
#
#       $ dhop go mark
#
#   This command will go to the location stored with the name 'mark', and not
#   to the location stored by the `mark` command. Because much confusion can
#   arise from this, it's recommended to simply not use any of the names used
#   by the commands.
#
# @param path
#   The path to assign to the name. If no path is given, the current
#   directory is assumed.
#

