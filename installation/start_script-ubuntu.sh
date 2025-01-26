#!/bin/sh

# Start Script (start.sh)

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

# Navigate to the project directory
cd Robustify-Design || exit 1

# Start the frontend
echo "Starting the frontend..."
cd frontend/envguard-frontend || exit 1
ng serve --port $FRONTEND_PORT &

# Start the pipeline
echo "Starting the pipeline..."
cd ../../pipeline || exit 1
. envServer/bin/activate
uvicorn server:app --workers 4 --host 0.0.0.0 --port $PIPELINE_PORT &

# Start the backend
echo "Starting the backend..."
cd ../backend || exit 1
. envBackend/bin/activate
uvicorn main:app --workers 4 --host 0.0.0.0 --port $BACKEND_PORT &

# Serve documentation
echo "Serving documentation..."
cd ../docs || exit 1
http-server --port $DOCS_PORT &

echo "All services started!"