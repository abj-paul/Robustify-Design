#!/bin/sh

# Ports to be used
FRONTEND_PORT=4200
DOCS_PORT=4201
PIPELINE_PORT=8000
BACKEND_PORT=3000

# Kill any processes using these ports
echo "Killing processes on ports $FRONTEND_PORT, $PIPELINE_PORT, $BACKEND_PORT, $DOCS_PORT..."
fuser -k $FRONTEND_PORT/tcp || echo "Port $FRONTEND_PORT is free."
fuser -k $PIPELINE_PORT/tcp || echo "Port $PIPELINE_PORT is free."
fuser -k $BACKEND_PORT/tcp || echo "Port $BACKEND_PORT is free."
fuser -k $DOCS_PORT/tcp || echo "Port $DOCS_PORT is free."

# Clone the repository
git clone https://github.com/abj-paul/Robustify-Design.git
cd Robustify-Design || exit 1
git pull

# Set up and run the frontend
cd frontend/envguard-frontend || exit 1
npm install
ng serve --port $FRONTEND_PORT & # Run Angular server in the background

# Set up and run the pipeline
cd ../../pipeline || exit 1
python3 -m venv envServer
. envServer/bin/activate
pip install -r requirements.txt
pip install uvicorn fastapi
pip install pygraphviz reportlab numpy networkx scipy scikit-learn python-dotenv google-generativeai python-multipart
echo $"Trying to run server:app from pipeline"
uvicorn server:app --workers 4 --host 0.0.0.0 --port $PIPELINE_PORT &
# Keep virtual environment active for parallel execution

# Set up and run the backend
cd ../backend || exit 1
python3 -m venv envBackend
# Activate the virtual environment and run the FastAPI server
. envBackend/bin/activate
pip install -r requirements.txt
uvicorn main:app --workers 4 --host 0.0.0.0 --port $BACKEND_PORT &
# Keep virtual environment active for parallel execution

# Serve documentation
cd ../docs || exit 1
http-server --port $DOCS_PORT &

cd ..
if [ ! -f pipeline/.env ]; then
    cp pipeline/.env.example pipeline/.env
    echo "Created .env file. Please update it with your configuration."
fi
