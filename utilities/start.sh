#!/bin/bash

# Set up a virtual environment and install dependencies
echo "Setting up virtual environment..."
rm -rf venv  # Remove any existing virtual environment
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies and build CSS using Gulp
echo "Installing Node.js dependencies..."
npm install

# Minify CSS files using Gulp
echo "Building and minifying CSS..."
gulp minifyBaseCss
gulp minifyIndexCss

# Restart the application (assuming a systemd service, adjust as needed)
echo "Restarting the application..."
sudo systemctl restart my_application.service

echo "Deployment complete."