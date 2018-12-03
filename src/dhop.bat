@echo off
if not exist %USERPROFILE%\bin\dhop.py echo "dhop.py is not in %USERPROFILE%\bin. Aborting."
python %USERPROFILE%\bin\dhop.py %*
set HOME=%HOMEDRIVE%%HOMEDIR%
if exist %HOME%\.dhopcmd.bat call %HOME%\.dhopcmd.bat
@echo on
