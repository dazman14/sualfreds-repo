@echo off
setlocal enabledelayedexpansion
set tools_dir=%~dp0tools

echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^> > %~dp0addons.xml
echo ^<addons^> >> %~dp0addons.xml

if exist plugin.video.amazon\resources\cache rd /s /q plugin.video.amazon\resources\cache >nul 2>&1

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
		%tools_dir%\7za a %%f\%%f-!version!.zip %%f -tzip -ax!%%f*.zip> nul
		echo %%f-!version!.zip Prozess fertig.
		echo. 
    ) else (
        echo.
		echo %%f-!version!.zip bereits aktuell
    )
)
echo ^</addons^> >> %~dp0addons.xml
for /f "delims= " %%a in ('%tools_dir%\fciv -md5 %~dp0addons.xml') do echo %%a > %~dp0addons.xml.md5
echo.
echo. [ Addons updated ]
echo.
pause
echo.
echo. [ Committer ]
echo.
set SOURCE=%~dp0
set SVN=C:\Program Files\TortoiseGit\bin
set GIT=C:\Program Files\Git\bin
rem "%SVN%\TortoiseGitProc.exe" /command:commit /path:"%SOURCE%" /closeonend:3
"%GIT%\git.exe" config --global push.default simple
"%GIT%\git.exe" add *
"%GIT%\git.exe" commit -a -m update
"%GIT%\git.exe" push
echo.
echo. [ Done ]
echo.
pause
