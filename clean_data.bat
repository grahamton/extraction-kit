@echo off
setlocal

echo ==========================================
echo      EXTRACTION KIT DATA CLEANER
echo ==========================================
echo.
echo This will PERMANENTLY DELETE all files in:
echo   - data\scrapes\
echo   - data\media\
echo   - data\logs\
echo.
set /p "choice=Are you sure you want to proceed? (y/N): "
if /i not "%choice%"=="y" goto :eof

echo.
echo Cleaning data\scrapes...
if exist "data\scrapes" (
    rmdir /s /q "data\scrapes"
    mkdir "data\scrapes"
)

echo Cleaning data\media...
if exist "data\media" (
    rmdir /s /q "data\media"
    mkdir "data\media"
)

echo Cleaning data\logs...
if exist "data\logs" (
    rmdir /s /q "data\logs"
    mkdir "data\logs"
)

REM Optional: Clear manifest if desired, but user might want to keep history record?
REM User asked to "clear data folders", usually implies content.
REM I'll treat manifest.json as a record, maybe ask or just leave it.
REM User said "remove things quickly as I test", likely wants to reset runs.
REM I will NOT delete manifest.json by default as it tracks run IDs, but the runs themselves are gone.

echo.
echo [SUCCESS] Data folders cleared.
echo.
pause
