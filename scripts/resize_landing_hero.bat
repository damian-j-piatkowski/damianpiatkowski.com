@echo off
setlocal enabledelayedexpansion
:: ===========================================
:: Landing Hero Image Resizer (Lean Version)
:: Creates 16:9, 4:5, and 2:3 hero images
:: Produces JPG + WebP, with 1x + 2x sizes
:: ===========================================

if "%~1"=="" (
    echo Usage: resize_landing_hero.bat input_directory
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
set "file_src_16x9=landing-hero_source_16x9.png"
set "file_src_4x5=landing-hero_source_4x5.jpg"
set "file_src_2x3=landing-hero_source_2x3.jpg"

:: Check for sources
for %%F in ("%file_src_16x9%" "%file_src_4x5%" "%file_src_2x3%") do (
    if not exist %%F (
        echo Error: Missing source %%~nxF
        exit /b 1
    )
)

echo Found all sources.
echo.

:: 16:9 sizes
echo Creating landing-hero_16x9_2560w.jpg / .webp
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_16x9_2560w.jpg"
magick "%file_src_16x9%" -resize 2560x^ -gravity center -crop 2560x1440+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_16x9_2560w.webp"

echo Creating landing-hero_16x9_1920w.jpg / .webp
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_16x9_1920w.jpg"
magick "%file_src_16x9%" -resize 1920x^ -gravity center -crop 1920x1080+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_16x9_1920w.webp"

:: 4:5 sizes
echo Creating landing-hero_4x5_1920w.jpg / .webp
magick "%file_src_4x5%" -resize 1920x^ -gravity center -crop 1920x2400+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_4x5_1920w.jpg"
magick "%file_src_4x5%" -resize 1920x^ -gravity center -crop 1920x2400+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_4x5_1920w.webp"

echo Creating landing-hero_4x5_960w.jpg / .webp
magick "%file_src_4x5%" -resize 960x^ -gravity center -crop 960x1200+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_4x5_960w.jpg"
magick "%file_src_4x5%" -resize 960x^ -gravity center -crop 960x1200+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_4x5_960w.webp"

:: 2:3 sizes
echo Creating landing-hero_2x3_1280w.jpg / .webp
magick "%file_src_2x3%" -resize 1280x^ -gravity center -crop 1280x1920+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_2x3_1280w.jpg"
magick "%file_src_2x3%" -resize 1280x^ -gravity center -crop 1280x1920+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_2x3_1280w.webp"

echo Creating landing-hero_2x3_640w.jpg / .webp
magick "%file_src_2x3%" -resize 640x^ -gravity center -crop 640x960+0+0 -strip -quality 92 -sharpen 0x1.0 "landing-hero_2x3_640w.jpg"
magick "%file_src_2x3%" -resize 640x^ -gravity center -crop 640x960+0+0 -strip -quality 90 -sharpen 0x1.0 "landing-hero_2x3_640w.webp"

echo.
echo Successfully created JPG + WebP images!
