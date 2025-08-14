#!/bin/bash
# Deployment script for Math Homework Solver

echo "Starting deployment process..."

# Build and deploy backend
echo "Building backend..."
cd src/backend
docker build -t math-solver-backend .

# Build Flutter app
echo "Building Flutter app..."
cd ../frontend
flutter build apk --release

echo "Deployment completed!"