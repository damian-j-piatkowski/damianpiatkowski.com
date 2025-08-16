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

    echo Creating retina.jpg   ^(850x567^) Retina
    magick "%%F" -resize 850x^ -gravity center -crop 850x567+0+0 -strip -quality 92 -sharpen 0x1.0 "retina.jpg"

    echo Creating desktop.jpg  ^(640x426^) Desktop
    magick "%%F" -resize 640x^ -gravity center -crop 640x426+0+0 -strip -quality 92 -sharpen 0x1.0 "desktop.jpg"

    echo Creating tablet.jpg   ^(480x320^) Tablet
    magick "%%F" -resize 480x^ -gravity center -crop 480x320+0+0 -strip -quality 92 -sharpen 0x1.0 "tablet.jpg"

    echo Creating mobile.jpg   ^(320x213^) Mobile
    magick "%%F" -resize 320x^ -gravity center -crop 320x213+0+0 -strip -quality 92 -sharpen 0x1.0 "mobile.jpg"

    echo.
    echo Successfully created 3:2 thumbnail images:
    echo    retina.jpg    ^(850x567^) Retina
    echo    desktop.jpg   ^(640x426^) Desktop
    echo    tablet.jpg    ^(480x320^) Tablet
    echo    mobile.jpg    ^(320x213^) Mobile
    goto :done
)

echo Error: No image files found in "%input_dir%"
exit /b 1

:done
echo All done!
