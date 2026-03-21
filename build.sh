#!/bin/bash

set -e

echo "Building PokerTracker..."

cd "$(dirname "$0")"

if [ -d "build" ]; then
    echo "Cleaning previous build..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "Cleaning dist..."
    rm -rf dist
fi

echo "Running PyInstaller..."
pyinstaller PokerTracker.spec

if [ -f "dist/PokerTracker/PokerTracker.exe" ]; then
    echo ""
    echo "Build successful!"
    echo "Output: dist/PokerTracker/PokerTracker.exe"
    echo ""
    echo "File size: $(du -h dist/PokerTracker/PokerTracker.exe | cut -f1)"
else
    echo "Build failed!"
    exit 1
fi
