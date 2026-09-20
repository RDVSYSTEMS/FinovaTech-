@echo off
title FinovaTech v9 - Servidor
cd /d "%~dp0"

rem ---- Verifica que el entorno virtual exista -------------------------
if not exist ".venv\Scripts\python.exe" goto novenv

rem ---- Verifica que MySQL (XAMPP) escuche en el puerto 3306 -----------
echo [FinovaTech] Comprobando MySQL (XAMPP)...
netstat -ano > "%TEMP%\finovatech_net.txt"
findstr ":3306" "%TEMP%\finovatech_net.txt" > nul
if errorlevel 1 goto sinmysql

:iniciar
echo.
echo [FinovaTech] Arrancando servidor en:  http://localhost:5000
echo [FinovaTech] Presiona Ctrl+C para detenerlo.
echo.
start "" /b cmd /c "ping -n 5 127.0.0.1 >nul & start http://localhost:5000"
".venv\Scripts\python.exe" run.py
pause
exit /b 0

:novenv
echo [ERROR] No se encontro el entorno virtual.
echo Para instalarlo:
echo   py -m venv .venv
echo   .venv\Scripts\pip install -r requirements.txt
echo.
pause
exit /b 1

:sinmysql
echo [AVISO] No se detecto MySQL en el puerto 3306.
echo Inicialo desde el panel de XAMPP (boton Start de MySQL).
set /p opcion=Continuar de todos modos s/n
if /i not "%opcion%"=="s" exit /b 1
goto iniciar