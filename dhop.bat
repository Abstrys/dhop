@echo off
if not exist %USERPROFILE%\bin\dhop.rb echo "dhop.rb is not in %USERPROFILE%\bin. Aborting."
ruby %USERPROFILE%\bin\dhop.rb %*
set HOME=%HOMEDRIVE%%HOMEDIR%
if exist %HOME%\.dhopcmd.bat call %HOME%\.dhopcmd.bat
@echo on
