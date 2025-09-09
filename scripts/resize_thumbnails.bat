@echo off
setlocal enabledelayedexpansion
:: ===========================================
:: Blog Thumbnail Image Resizer
:: -------------------------------------------
:: Purpose:
::   Creates responsive 3:2 thumbnail images
::   from a single source image. Produces both
::   JPG and WebP versions optimized for
::   desktop, tablet, and mobile.
::
:: Requirements:
::   - ImageMagick installed and available in PATH
::
:: Usage:
::   resize_thumbnails.bat <input_directory>
::
:: In the folder:
::   post-thumbnail-original.jpg
::
:: Will output:
::   desktop@2x.jpg (640x427) + desktop@2x.webp
::   desktop.jpg   (320x213) + desktop.webp
::   tablet.jpg    (450x300) + tablet.webp
::   mobile.jpg    (350x233) + mobile.webp
:: ===========================================

if "%~1"=="" (
    echo Usage: resize_thumbnails.bat input_directory
    exit /b 1
)

set "input_dir=%~1"

if not exist "%input_dir%" (
    echo Error: Directory "%input_dir%" does not exist.
    exit /b 1
)

cd /d "%input_dir%"
echo Changed to directory: %input_dir%

:: Automatically detect the first JPG/JPEG/PNG file in the folder
set "file_src="
for %%F in (*.jpg *.jpeg *.png) do (
    set "file_src=%%F"
    goto found
)

:found
if "%file_src%"=="" (
    echo Error: No image files found in "%input_dir%"
    exit /b 1
)

echo Found source: %file_src%
echo.

echo Creating desktop@2x.jpg (640x427) Retina
magick "%file_src%" -resize 640x^ -gravity center -crop 640x427+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "desktop@2x.jpg"
magick "desktop@2x.jpg" -quality 90 "desktop@2x.webp"

echo Creating desktop.jpg (320x213) Desktop
magick "%file_src%" -resize 320x^ -gravity center -crop 320x213+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "desktop.jpg"
magick "desktop.jpg" -quality 90 "desktop.webp"

echo Creating tablet.jpg (450x300) Tablet
magick "%file_src%" -resize 450x^ -gravity center -crop 450x300+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "tablet.jpg"
magick "tablet.jpg" -quality 90 "tablet.webp"

echo Creating mobile.jpg (350x233) Mobile
magick "%file_src%" -resize 350x^ -gravity center -crop 350x233+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "mobile.jpg"
magick "mobile.jpg" -quality 90 "mobile.webp"

echo.
echo Successfully created optimized 3:2 thumbnail images!
echo    desktop@2x.jpg / .webp (640x427 Retina)
echo    desktop.jpg    / .webp (320x213 Desktop)
echo    tablet.jpg     / .webp (450x300 Tablet)
echo    mobile.jpg     / .webp (350x233 Mobile)

echo.
echo All done!