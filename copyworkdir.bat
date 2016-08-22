@echo off
set ftvkrypton=E:\github\skin.fTVfred-krypton
echo. 
echo Copying files
echo. 
XCOPY %ftvkrypton% skin.fTVfred-krypton /E /C /Q /I /Y
pause