@echo off

:: ===========================================
:: Blog Hero Image Resizer - 16:9 Aspect Ratio
:: Usage: resize_images.bat "C:\path\to\image-folder"
:: ===========================================

if "%~1"=="" (
    echo Usage: resize_images.bat input_directory
    exit /b 1
)

set "input_dir=%~1"

if not exist "%input_dir%" (
    echo Error: Directory "%input_dir%" does not exist.
    exit /b 1
)

cd /d "%input_dir%"
echo Changed to directory: %input_dir%

:: Only process first image found
for %%F in (*.jpg *.jpeg *.png) do (
    echo Found: %%F

    echo Creating xl.jpg      ^(1600x900^) Extra Large Desktop
    magick "%%F" -resize 1600x900^ -gravity center -crop 1600x900+0+0 -quality 85 "xl.jpg"

    echo Creating large.jpg   ^(1200x675^) Large Desktop
    magick "%%F" -resize 1200x675^ -gravity center -crop 1200x675+0+0 -quality 85 "large.jpg"

    echo Creating medium.jpg  ^(800x450^) Tablet/Small Laptop
    magick "%%F" -resize 800x450^ -gravity center -crop 800x450+0+0 -quality 85 "medium.jpg"

    echo Creating small.jpg   ^(600x338^) Large Phone/Small Tablet
    magick "%%F" -resize 600x338^ -gravity center -crop 600x338+0+0 -quality 85 "small.jpg"

    echo Creating xs.jpg      ^(480x270^) Mobile Phone
    magick "%%F" -resize 480x270^ -gravity center -crop 480x270+0+0 -quality 85 "xs.jpg"

    echo.
    echo Successfully created 16:9 hero images:
    echo    xl.jpg           ^(1600x900^) Extra Large Desktop
    echo    large.jpg        ^(1200x675^) Large Desktop
    echo    medium.jpg       ^(800x450^) Tablet/Small Laptop
    echo    small.jpg        ^(600x338^) Large Phone/Small Tablet
    echo    xs.jpg           ^(480x270^) Mobile Phone
    goto :done
)

echo Error: No image files found in "%input_dir%"
exit /b 1

:done
echo All done!

