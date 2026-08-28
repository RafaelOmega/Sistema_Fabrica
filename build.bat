@echo off
setlocal EnableExtensions EnableDelayedExpansion
set PYTHONDONTWRITEBYTECODE=1

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
if errorlevel 1 (
  echo ERRO: Falha ao atualizar pip/setuptools/wheel.
  pause
  exit /b 1
)

if exist "requirements.txt" (
  pip install -r requirements.txt
  if errorlevel 1 (
    echo ERRO: Falha ao instalar requirements.txt.
    pause
    exit /b 1
  )

  pip install pyinstaller
  if errorlevel 1 (
    echo ERRO: Falha ao instalar pyinstaller.
    pause
    exit /b 1
  )
) else (
  pip install pyinstaller PySide6 sqlalchemy psycopg2-binary
  if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias basicas.
    pause
    exit /b 1
  )
)

REM ----- limpa builds antigos -----
echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

REM ----- limpa __pycache__ recursivamente -----
for /d /r %%D in (__pycache__) do (
  if exist "%%D" rmdir /s /q "%%D"
)

REM ----- inclui arquivos/pastas necessarias -----
set "ADD_DATA_ARGS="
if exist "app\styles" set "ADD_DATA_ARGS=!ADD_DATA_ARGS! --add-data ""app\styles;app\styles"""
if exist "assets" set "ADD_DATA_ARGS=!ADD_DATA_ARGS! --add-data ""assets;assets"""

REM ----- icone (opcional) -----
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
  --paths "." ^
  --hidden-import="psycopg2" ^
  --hidden-import="psycopg2.extensions" ^
  --hidden-import="psycopg2.extras" ^
  --hidden-import="sqlalchemy.dialects.postgresql" ^
  --hidden-import="app.models.produto" ^
  --hidden-import="app.models.produto_table_model" ^
  --hidden-import="app.models.produto_filter_proxy_model" ^
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