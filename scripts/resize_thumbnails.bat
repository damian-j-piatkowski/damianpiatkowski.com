@echo off

:: ===========================================
:: Blog Thumbnail Image Resizer - 3:2 Aspect Ratio
:: Usage: resize_thumbnails.bat "C:\path\to\thumbnail-folder"
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

:: Find original image (assumed to be original.jpg or first jpg/jpeg/png)
for %%F in (*.jpg *.jpeg *.png) do (
    echo Found: %%F

    echo Creating desktop@2x.jpg ^(640x427^) Desktop Retina
    magick "%%F" -resize 640x^ -gravity center -crop 640x427+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "desktop@2x.jpg"
    magick "desktop@2x.jpg" -quality 90 "desktop@2x.webp"

    echo Creating desktop.jpg   ^(320x213^) Desktop
    magick "%%F" -resize 320x^ -gravity center -crop 320x213+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "desktop.jpg"
    magick "desktop.jpg" -quality 90 "desktop.webp"

    echo Creating tablet.jpg    ^(450x300^) Tablet
    magick "%%F" -resize 450x^ -gravity center -crop 450x300+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "tablet.jpg"
    magick "tablet.jpg" -quality 90 "tablet.webp"

    echo Creating mobile.jpg    ^(350x233^) Mobile
    magick "%%F" -resize 350x^ -gravity center -crop 350x233+0+0 -strip -quality 90 -unsharp 0x0.75+0.75+0.008 "mobile.jpg"
    magick "mobile.jpg" -quality 90 "mobile.webp"

    echo.
    echo Successfully created optimized 3:2 thumbnail images:
    echo    desktop@2x.jpg ^(640x427^) Retina
    echo    desktop.jpg    ^(320x213^) Desktop
    echo    tablet.jpg     ^(450x300^) Tablet
    echo    mobile.jpg     ^(350x233^) Mobile
    goto :done
)

echo Error: No image files found in "%input_dir%"
exit /b 1

:done
echo All done!
