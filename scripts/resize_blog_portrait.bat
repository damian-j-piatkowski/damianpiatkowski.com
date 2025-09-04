@echo off
:: Blog Portrait Resizer with Retina Support
:: Usage: resize_blog_portrait.bat "C:\path\to\your-photo.jpg"

if "%~1"=="" (
    echo Usage: resize_blog_portrait.bat input_image
    echo.
    echo Recommended input: Square ^(1:1^) or near-square ^(4:3, 3:4^) aspect ratio
    echo Best results: Face centered, simple background, good lighting
    exit /b 1
)

set "input_file=%~1"

if not exist "%input_file%" (
    echo Error: Image "%input_file%" does not exist.
    exit /b 1
)

:: Get the folder of the source file
for %%I in ("%input_file%") do set "input_dir=%%~dpI"

echo Creating blog portrait images from: %input_file%
echo.

:: Get image dimensions for reference
echo Analyzing source image dimensions...
for /f "tokens=1,2" %%a in ('magick identify -format "%%w %%h" "%input_file%"') do (
    set "width=%%a"
    set "height=%%b"
)
echo Source: %width%x%height% pixels

:: Aspect ratio info
if %width% GTR %height% (
    echo Aspect ratio: Landscape ^(wider than tall^)
    echo Note: Will crop from sides to create square
) else if %width% LSS %height% (
    echo Aspect ratio: Portrait ^(taller than wide^)
    echo Note: Will crop from top/bottom to create square
) else (
    echo Aspect ratio: Perfect square - no cropping needed!
)
echo.

:: === JPG versions ===
echo Creating banner_profile_400w.jpg (Desktop 1x)
magick "%input_file%" -resize 400x400^ -gravity center -crop 400x400+0+0 -strip -quality 85 -unsharp 0x0.75+0.75+0.008 "%input_dir%banner_profile_400w.jpg"

echo Creating banner_profile_800w.jpg (Desktop 2x / Retina)
magick "%input_file%" -resize 800x800^ -gravity center -crop 800x800+0+0 -strip -quality 85 -unsharp 0x0.75+0.75+0.008 "%input_dir%banner_profile_800w.jpg"

echo Creating banner_profile_300w.jpg (Mobile 1x)
magick "%input_file%" -resize 300x300^ -gravity center -crop 300x300+0+0 -strip -quality 85 -unsharp 0x0.75+0.75+0.008 "%input_dir%banner_profile_300w.jpg"

echo Creating banner_profile_600w.jpg (Mobile 2x / Retina)
magick "%input_file%" -resize 600x600^ -gravity center -crop 600x600+0+0 -strip -quality 85 -unsharp 0x0.75+0.75+0.008 "%input_dir%banner_profile_600w.jpg"

:: === WebP versions ===
echo Creating WebP versions...

magick "%input_dir%banner_profile_400w.jpg" -quality 80 "%input_dir%banner_profile_400w.webp"
magick "%input_dir%banner_profile_800w.jpg" -quality 80 "%input_dir%banner_profile_800w.webp"
magick "%input_dir%banner_profile_300w.jpg" -quality 80 "%input_dir%banner_profile_300w.webp"
magick "%input_dir%banner_profile_600w.jpg" -quality 80 "%input_dir%banner_profile_600w.webp"

echo.
echo Blog portrait images created successfully!
echo Files created in %input_dir%:
echo   banner_profile_300w.jpg / .webp  (Mobile 1x)
echo   banner_profile_600w.jpg / .webp  (Mobile 2x)
echo   banner_profile_400w.jpg / .webp  (Desktop 1x)
echo   banner_profile_800w.jpg / .webp  (Desktop 2x)
echo.
echo Tip: Use 1x for normal displays and 2x for Retina/HiDPI
