@echo off
cd /d "%~dp0"
echo === Instalando bibliotecas ===
py -m pip install --upgrade pip
py -m pip install PySide6 mutagen pyinstaller yt-dlp imageio-ffmpeg
if errorlevel 1 goto erro
echo.
echo === Testando se o app abre (feche a janela para continuar) ===
py MigsMusic.py
echo.
echo === Gerando o .exe ===
py -m PyInstaller --noconsole --onefile --clean --collect-submodules yt_dlp --collect-all imageio_ffmpeg --name MigsMusic MigsMusic.py
if errorlevel 1 goto erro
echo.
echo PRONTO! O arquivo esta em: dist\MigsMusic.exe
pause
exit /b 0
:erro
echo.
echo DEU ERRO. Tire um print desta janela e me envie.
pause
exit /b 1
