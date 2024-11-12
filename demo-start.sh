#!/bin/bash

echo "Starting Text to Video Generator Demo..."
echo

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running!"
    echo "Please start Docker Desktop and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Docker is running!"
echo
echo "Starting the application..."
docker-compose up --build
