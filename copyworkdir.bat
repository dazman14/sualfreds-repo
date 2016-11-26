@echo off
set ftvkrypton=E:\github\skin.fTVfred-krypton
set target=skin.fTVfred-krypton
set htpc=\\NUCFRED\Kodi\portable_data\addons\skin.fTVfred-krypton
echo. 
echo Copying files
echo. 
XCOPY %ftvkrypton% %target% /E /C /Q /I /Y
del /q /s %target%\*.pyo 
del /q /s %target%\*.pyc 
del /q /s %target%\*.psd 
rd /S /Q %target%\.git
XCOPY %target% %htpc% /E /C /Q /I /Y


pause