@echo off
setlocal enabledelayedexpansion
set TOOLS=%~dp0tools
set SOURCE=%~dp0
set GIT=C:\Program Files\Git\bin

echo.
echo. [ Checking for new versions ]
echo.
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^> > %~dp0addons.xml
echo ^<addons^> >> %~dp0addons.xml
for /f %%f in ('dir /b /a:d') do if exist %%f\addon.xml (
    del /q /s %%f\*.pyo >nul 2>&1>nul 2>&1
    del /q /s %%f\*.pyc >nul 2>&1
	rd /S /Q %%f\.git >nul 2>&1
    set add=
    for /f "delims=" %%a in (%%f\addon.xml) do (
        set line=%%a
        if "!line:~0,6!"=="<addon" set add=1
        if not "!line!"=="!line:version=!" if "!add!"=="1" (
            set new=!line:version=ß!
            for /f "delims=ß tokens=2" %%n in ("!new!") do set new=%%n
            for /f "delims=^= " %%n in ("!new!") do set new=%%n
            set version=!new:^"=!
        )
        if "!line:~-1!"==">" set add=
        if not "!line:~0,5!"=="<?xml" echo %%a >> %~dp0addons.xml
    )
    if not exist %%f\%%f-!version!.zip (
        echo. 
		echo.
		echo NEUE VERSION von %%f !		
		if exist "%%f\%%f*.zip" (
		echo Erstelle Backups bisheriger Releases
		IF not exist temp mkdir temp	
		IF not exist temp\%%f mkdir temp\%%f
		IF not exist temp\%%f\oldreleases mkdir temp\%%f\oldreleases
		move "%%f\%%f*.zip" temp\%%f\oldreleases >nul 2>&1
		)
		echo Packe %%f-!version!.zip
		%TOOLS%\7za a %%f\%%f-!version!.zip %%f -tzip -ax!%%f*.zip> nul
		echo %%f-!version!.zip Prozess fertig.
		echo. 
    ) else (
        echo.
		echo %%f-!version!.zip bereits aktuell
    )
)
echo ^</addons^> >> %~dp0addons.xml
for /f "delims= " %%a in ('%TOOLS%\fciv -md5 %~dp0addons.xml') do echo %%a > %~dp0addons.xml.md5
echo.
echo. [ Addons updated ]
echo.
goto :choice

:choice
set /P c=Should I update the repo? (Y/N)
if /I "%c%" EQU "Y" goto :repoupdate
if /I "%c%" EQU "N" goto :exitspot
goto :choice

:repoupdate
echo.
echo. [ Committer ]
echo.
"%GIT%\git.exe" config --global push.default simple
"%GIT%\git.exe" add *
"%GIT%\git.exe" commit -a -m update
"%GIT%\git.exe" push
echo.
echo. [ Done ]
echo.
pause
exit

:exitspot
echo "You selected NO, exiting ..."
pause 
exit