@echo off
setlocal enabledelayedexpansion
:: ===========================================
:: Blog Hero Image Resizer
:: -------------------------------------------
:: Purpose:
::   Creates responsive 16:9 hero images from
::   a single source JPG. Produces both JPG
::   and WebP versions in multiple sizes.
::
:: Requirements:
::   - ImageMagick installed and available in PATH
::
:: Usage:
::   resize_blog_hero.bat <input_directory>
::
:: In the folder:
::   road-to-my-website-16x9-original.jpg
::
:: Will output:
::   hero_16x9_2560w.jpg
::   hero_16x9_2560w.webp
::   hero_16x9_1920w.jpg
::   hero_16x9_1920w.webp
::   hero_16x9_1280w.jpg
::   hero_16x9_1280w.webp
::   hero_16x9_640w.jpg
::   hero_16x9_640w.webp
:: ===========================================

if "%~1"=="" (
    echo Usage: resize_blog_hero.bat input_directory
    exit /b 1
)

set "input_dir=%~1"

if not exist "%input_dir%" (
    echo Error: Directory "%input_dir%" does not exist.
    exit /b 1
)

cd /d "%input_dir%"
echo Changed to directory: %input_dir%

:: Automatically detect the first JPG file in the folder
set "file_src_16x9="
for %%f in (*.jpg *.jpeg) do (
    set "file_src_16x9=%%f"
    goto found
)

:found
if "%file_src_16x9%"=="" (
    echo Error: No JPG source file found in "%input_dir%".
    exit /b 1
)

echo Found source: %file_src_16x9%
echo.

echo Creating hero_16x9_2560w.jpg / .webp
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 92 -sharpen 0x1.0 "hero_16x9_2560w.jpg"
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 90 -sharpen 0x1.0 "hero_16x9_2560w.webp"

echo Creating hero_16x9_1920w.jpg / .webp
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 92 -sharpen 0x1.0 "hero_16x9_1920w.jpg"
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 90 -sharpen 0x1.0 "hero_16x9_1920w.webp"

echo Creating hero_16x9_1280w.jpg / .webp
magick "%file_src_16x9%" -resize 1280x^ -gravity center -crop 1280x720+0+0 -strip -quality 92 -sharpen 0x1.0 "hero_16x9_1280w.jpg"
magick "%file_src_16x9%" -resize 1280x^ -gravity center -crop 1280x720+0+0 -strip -quality 90 -sharpen 0x1.0 "hero_16x9_1280w.webp"

echo Creating hero_16x9_640w.jpg / .webp
magick "%file_src_16x9%" -resize 640x^ -gravity center -crop 640x360+0+0 -strip -quality 92 -sharpen 0x1.0 "hero_16x9_640w.jpg"
magick "%file_src_16x9%" -resize 640x^ -gravity center -crop 640x360+0+0 -strip -quality 90 -sharpen 0x1.0 "hero_16x9_640w.webp"

echo.
echo Successfully created JPG + WebP hero images!
