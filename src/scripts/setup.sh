#!/bin/bash
# Setup script for Math Homework Solver development environment

echo "Setting up development environment..."

# Backend setup
echo "Setting up backend dependencies..."
cd src/backend
uv sync

# Frontend setup
echo "Setting up Flutter dependencies..."
cd ../frontend
flutter pub get

echo "Setup completed! Run 'docker-compose up' to start the application."