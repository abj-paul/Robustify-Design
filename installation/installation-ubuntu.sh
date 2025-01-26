#!/bin/sh

# Installation Script (install.sh)

# Clone the repository
echo "Cloning the repository..."
git clone https://github.com/abj-paul/Robustify-Design.git
cd Robustify-Design || exit 1

# Set up the frontend
echo "Setting up the frontend..."
cd frontend/envguard-frontend || exit 1
npm install

# Set up the pipeline
echo "Setting up the pipeline..."
cd ../../pipeline || exit 1
python3 -m venv envServer
. envServer/bin/activate
pip install -r requirements.txt
pip install uvicorn fastapi pygraphviz reportlab numpy networkx scipy scikit-learn python-dotenv google-generativeai python-multipart

# Set up the backend
echo "Setting up the backend..."
cd ../backend || exit 1
python3 -m venv envBackend
. envBackend/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
cd ../pipeline || exit 1
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your configuration."
fi

echo "Installation complete!"