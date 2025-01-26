#!/bin/sh

# Update Script (update.sh)

# Navigate to the project directory
cd Robustify-Design || exit 1

# Pull the latest changes
echo "Pulling the latest changes from the repository..."
git pull

# Update frontend dependencies
echo "Updating frontend dependencies..."
cd frontend/envguard-frontend || exit 1
npm install

# Update pipeline dependencies
echo "Updating pipeline dependencies..."
cd ../../pipeline || exit 1
. envServer/bin/activate
pip install -r requirements.txt

# Update backend dependencies
echo "Updating backend dependencies..."
cd ../backend || exit 1
. envBackend/bin/activate
pip install -r requirements.txt

echo "Update complete!"