@echo off
set PATH_TO_INSTALL="%USERPROFILE%\bin"
if not exist %PATH_TO_INSTALL% mkdir %PATH_TO_INSTALL%
copy src\\dhop\\dhop.py %PATH_TO_INSTALL%
copy src\\dhop.bat %PATH_TO_INSTALL%
@echo on
