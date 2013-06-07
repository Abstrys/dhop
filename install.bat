@echo off
set PATH_TO_INSTALL="%USERPROFILE%\bin"

if not exist %PATH_TO_INSTALL% mkdir %PATH_TO_INSTALL%

copy dhop.rb %PATH_TO_INSTALL%
copy dhop.bat %PATH_TO_INSTALL%

@echo on
