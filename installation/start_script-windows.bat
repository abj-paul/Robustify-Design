@echo off
:: Start Script (start.bat)

:: Ports to be used
set FRONTEND_PORT=4200
set DOCS_PORT=4201
set PIPELINE_PORT=8000
set BACKEND_PORT=3000

:: Kill any processes using these ports
echo Killing processes on ports %FRONTEND_PORT%, %PIPELINE_PORT%, %BACKEND_PORT%, %DOCS_PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%FRONTEND_PORT%') do taskkill /f /pid %%a
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PIPELINE_PORT%') do taskkill /f /pid %%a
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%BACKEND_PORT%') do taskkill /f /pid %%a
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%DOCS_PORT%') do taskkill /f /pid %%a

:: Navigate to the project directory
cd Robustify-Design || exit /b 1

:: Start the frontend
echo Starting the frontend...
cd frontend\envguard-frontend || exit /b 1
start "Frontend" cmd /c "ng serve --port %FRONTEND_PORT%"

:: Start the pipeline
echo Starting the pipeline...
cd ..\..\pipeline || exit /b 1
call envServer\Scripts\activate
start "Pipeline" cmd /c "uvicorn server:app --workers 4 --host 0.0.0.0 --port %PIPELINE_PORT%"

:: Start the backend
echo Starting the backend...
cd ..\backend || exit /b 1
call envBackend\Scripts\activate
start "Backend" cmd /c "uvicorn main:app --workers 4 --host 0.0.0.0 --port %BACKEND_PORT%"

:: Serve documentation
echo Serving documentation...
cd ..\docs || exit /b 1
start "Documentation" cmd /c "http-server --port %DOCS_PORT%"

echo All services started!
pause