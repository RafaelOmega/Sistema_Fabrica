@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ========= AJUSTE AQUI =========
set "APP_NAME=ControleFabrica"
set "ENTRY_POINT=main.py"
set "VENV_DIR=.venv"
set "ICON_FILE="
REM =================================

cd /d "%~dp0"

if not exist "%ENTRY_POINT%" (
  echo ERRO: Nao encontrei "%ENTRY_POINT%" em %cd%
  pause
  exit /b 1
)

REM ----- cria/ativa venv -----
if not exist "%VENV_DIR%\Scripts\python.exe" (
  py -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo ERRO: Falha ao criar venv.
    pause
    exit /b 1
  )
)
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
  echo ERRO: Falha ao ativar venv.
  pause
  exit /b 1
)

REM ----- instala deps -----
python -m pip install --upgrade pip setuptools wheel

if exist "requirements.txt" (
  pip install -r requirements.txt
) else (
  pip install pyinstaller PySide6 sqlalchemy psycopg2-binary
)

REM ----- limpa builds antigos (pasta, spec e dist) -----
echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

REM ----- limpa cache __pycache__ das pastas do projeto -----
for /d %%D in (app) do (
  if exist "%%D" (
    for /d %%P in ("%%D\*") do (
      if exist "%%P\__pycache__" rmdir /s /q "%%P\__pycache__"
    )
    if exist "%%D\__pycache__" rmdir /s /q "%%D\__pycache__"
  )
)

REM ----- inclui arquivos/pastas necessárias -----
set "ADD_DATA_ARGS="
if exist "app\styles" set "ADD_DATA_ARGS=!ADD_DATA_ARGS! --add-data ""app\styles;app\styles"""
if exist "assets" set "ADD_DATA_ARGS=!ADD_DATA_ARGS! --add-data ""assets;assets"""

REM ----- ícone (opcional) -----
set "ICON_ARG="
if not "%ICON_FILE%"=="" (
  if exist "%ICON_FILE%" (
    set "ICON_ARG=--icon ""%ICON_FILE%"""
  )
)

REM ----- build -----
echo Iniciando build...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --windowed ^
  --name "%APP_NAME%" ^
  %ICON_ARG% ^
  %ADD_DATA_ARGS% ^
  --hidden-import="psycopg2" ^
  --hidden-import="app.models.produto" ^
  --paths "." ^
  "%ENTRY_POINT%"

if errorlevel 1 (
  echo.
  echo ERRO: Build falhou.
  pause
  exit /b 1
)

echo.
echo OK: Build concluido.
echo Saida: %cd%\dist\%APP_NAME%\
pause
exit /b 0