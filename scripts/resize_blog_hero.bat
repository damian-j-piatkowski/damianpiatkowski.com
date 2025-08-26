@echo off
setlocal enabledelayedexpansion
:: ===========================================
:: Blog Hero Image Resizer
:: Creates 16:9 hero images
:: Produces JPG + WebP, with 1x + 2x sizes
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

:: Expected source files
set "file_src_16x9=landing-hero_source_16x9.jpg"


echo Found all sources.
echo.

:: 16:9 sizes
echo Creating landing-hero_16x9_2560w.jpg / .webp
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_16x9_2560w.jpg"
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_16x9_2560w.webp"

echo Creating landing-hero_16x9_1920w.jpg / .webp
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_16x9_1920w.jpg"
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_16x9_1920w.webp"

echo Creating landing-hero_16x9_1280w.jpg / .webp
magick "%file_src_16x9%" -resize 1280x^ -gravity center -crop 1280x720+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_16x9_1280w.jpg"
magick "%file_src_16x9%" -resize 1280x^ -gravity center -crop 1280x720+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_16x9_1280w.webp"

echo.
echo Successfully created JPG + WebP images!
