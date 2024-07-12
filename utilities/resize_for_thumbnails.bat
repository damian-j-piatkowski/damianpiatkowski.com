@echo off
setlocal

:: ===========================================
:: Batch Script for Resizing Images for Thumbnails
::
:: Usage:
::   resize_for_thumbnails.bat "input_file_path" "folder_name"
::
:: Parameters:
::   input_file_path - The path to the original image file.
::   folder_name     - The folder name where the resized images will be saved.
::
:: Description:
::   This script resizes the input image to predefined dimensions for mobile,
::   tablet, and desktop views. The resized images are saved in the
::   directory specified by the BASE_THUMBNAIL_PATH environment variable
::   and the folder_name parameter.
::
:: Output Resolutions:
::   Mobile:  382x215 px
::   Tablet:  480x270 px
::   Desktop: 330x186 px
::
:: Example:
::   resize_for_thumbnails.bat "C:\path\to\image.jpg" "01"
:: ===========================================

:: Check if the input file path and folder name are provided
if "%~1"=="" (
    echo Usage: resize_for_thumbnails.bat "input_file_path" "folder_name"
    exit /b 1
)
if "%~2"=="" (
    echo Usage: resize_for_thumbnails.bat "input_file_path" "folder_name"
    exit /b 1
)

:: Input file path and folder name
set "input_file_path=%~1"
set "folder_name=%~2"

:: Get the base path for thumbnails from the environment variable
if "%BASE_THUMBNAIL_PATH%"=="" (
    echo BASE_THUMBNAIL_PATH environment variable is not set.
    exit /b 1
)

:: Define the output directory
set "output_dir=%BASE_THUMBNAIL_PATH%\%folder_name%"

:: Create the output directory if it doesn't exist
if not exist "%output_dir%" (
    mkdir "%output_dir%"
)

:: Define output resolutions for mobile, tablet, and desktop
set resolutions_mobile=382x215
set resolutions_tablet=480x270
set resolutions_desktop=330x186

:: Debug: Print the input file path, output directory, and resolutions
echo Input File Path: %input_file_path%
echo Output Directory: %output_dir%
echo Mobile Resolution: %resolutions_mobile%
echo Tablet Resolution: %resolutions_tablet%
echo Desktop Resolution: %resolutions_desktop%

:: Process the input file
echo Processing file: %input_file_path%

magick "%input_file_path%" -resize %resolutions_mobile% -quality 85 "%output_dir%\%folder_name%_mobile.jpg"
if errorlevel 1 (
    echo Error processing file: %input_file_path% for mobile resolution
) else (
    echo Processed %input_file_path% for mobile resolution successfully
)

magick "%input_file_path%" -resize %resolutions_tablet% -quality 85 "%output_dir%\%folder_name%_tablet.jpg"
if errorlevel 1 (
    echo Error processing file: %input_file_path% for tablet resolution
) else (
    echo Processed %input_file_path% for tablet resolution successfully
)

magick "%input_file_path%" -resize %resolutions_desktop% -quality 85 "%output_dir%\%folder_name%_desktop.jpg"
if errorlevel 1 (
    echo Error processing file: %input_file_path% for desktop resolution
) else (
    echo Processed %input_file_path% for desktop resolution successfully
)

endlocal
