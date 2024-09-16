@echo off
setlocal

:: ===========================================
:: Batch Script for Resizing Images to Various Resolutions
::
:: Usage:
::   resize_images.bat input_directory
::
:: Parameters:
::   input_directory - The directory containing the original images.
::
:: Description:
::   This script resizes images to predefined resolutions for 4:5 and
::   16:9 aspect ratios. The resized images are saved in the same
::   directory as the original images with appropriate suffixes.
::
:: Output Resolutions:
::   Aspect Ratio 4:5:
::     - 320x400 px
::     - 640x800 px
::     - 960x1200 px
::     - 1200x1500 px
::   Aspect Ratio 16:9:
::     - 1920x1080 px
::     - 2560x1440 px
::
:: Example:
::   resize_images.bat C:\path\to\images
:: ===========================================

:: Check if the input directory is provided
if "%~1"=="" (
    echo Usage: resize_images.bat input_directory
    exit /b 1
)

:: Input directory and output directory
set "input_dir=%~1"
set "output_dir=%~1"

:: Define output resolutions for 4:5 and 16:9 aspect ratios
set resolutions_4x5=320x400 640x800 960x1200 1200x1500
set resolutions_16x9=1920x1080 2560x1440

:: Loop through 4:5 resolutions and create resized images
for %%R in (%resolutions_4x5%) do (
    for %%F in ("%input_dir%\*_4x5.*") do (
        for /f "tokens=1 delims=x" %%W in ("%%R") do (
            magick "%%F" -resize %%R -quality 85 "%output_dir%\%%~nF_%%Ww.jpg"
        )
    )
)

:: Loop through 16:9 resolutions and create resized images
for %%R in (%resolutions_16x9%) do (
    for %%F in ("%input_dir%\*_16x9.*") do (
        for /f "tokens=1 delims=x" %%W in ("%%R") do (
            magick "%%F" -resize %%R -quality 85 "%output_dir%\%%~nF_%%Ww.jpg"
        )
    )
)

endlocal
