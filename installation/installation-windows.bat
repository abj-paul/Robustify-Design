@echo off
:: Installation Script (install.bat)

:: Clone the repository
echo Cloning the repository...
git clone https://github.com/abj-paul/Robustify-Design.git
cd Robustify-Design || exit /b 1

:: Set up the frontend
echo Setting up the frontend...
cd frontend\envguard-frontend || exit /b 1
npm install

:: Set up the pipeline
echo Setting up the pipeline...
cd ..\..\pipeline || exit /b 1
python -m venv envServer
call envServer\Scripts\activate
pip install -r requirements.txt
pip install uvicorn fastapi pygraphviz reportlab numpy networkx scipy scikit-learn python-dotenv google-generativeai python-multipart

:: Set up the backend
echo Setting up the backend...
cd ..\backend || exit /b 1
python -m venv envBackend
call envBackend\Scripts\activate
pip install -r requirements.txt

:: Create .env file if it doesn't exist
cd ..\pipeline || exit /b 1
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please update it with your configuration.
)

echo Installation complete!
pause