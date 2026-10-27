@echo off
chcp 65001 >nul
echo 正在打包 BV/AV 转换器...

python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --icon icon.ico ^
  --name bv-av-converter ^
  bv_aid_v2.py

if errorlevel 1 (
    echo.
    echo 打包失败，请确认已安装: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo 完成！产物在 dist\bv-av-converter.exe
pause
