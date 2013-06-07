@echo off

set HOME="%HOMEDRIVE%%HOMEDIR%"

if not exist %USERPROFILE%\bin\dhop.rb echo "dhop.rb is not in %USERPROFILE%\bin. Aborting."

ruby %USERPROFILE%\bin\dhop.rb %*

REM if exist %HOME%\.dhopcmd call %HOME%\.dhopcmd
@echo on
