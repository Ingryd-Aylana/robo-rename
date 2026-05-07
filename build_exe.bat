@echo off
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --name RoboRename robo.py
if not exist entrada mkdir entrada
if not exist saida mkdir saida
copy /Y dist\RoboRename.exe RoboRename.exe
echo.
echo Executavel gerado: RoboRename.exe
echo Coloque os PDFs em entrada e execute RoboRename.exe
pause
