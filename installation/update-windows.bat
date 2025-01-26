@echo off
:: Update Script (update.bat)

:: Navigate to the project directory
cd Robustify-Design || exit /b 1

:: Pull the latest changes
echo Pulling the latest changes from the repository...
git pull

:: Update frontend dependencies
echo Updating frontend dependencies...
cd frontend\envguard-frontend || exit /b 1
npm install

:: Update pipeline dependencies
echo Updating pipeline dependencies...
cd ..\..\pipeline || exit /b 1
call envServer\Scripts\activate
pip install -r requirements.txt

:: Update backend dependencies
echo Updating backend dependencies...
cd ..\backend || exit /b 1
call envBackend\Scripts\activate
pip install -r requirements.txt

echo Update complete!
pause