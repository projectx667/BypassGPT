#!/bin/bash

clear

echo "======================================"
echo "   BypassGPT v2 - Setup & Launch"
echo "======================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found"
    echo "Install from: https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python $PYTHON_VERSION detected"

if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found"
    echo "Installing pip..."
    python3 -m ensurepip --default-pip
fi

echo "pip3 detected"
echo ""

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    exit 1
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt --quiet --upgrade

if [ $? -ne 0 ]; then
    echo "Installation failed"
    echo "Try manually: pip3 install -r requirements.txt"
    exit 1
fi

echo "Dependencies installed"
echo ""

if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found"
    exit 1
fi

echo "======================================"
echo "      Installation Complete"
echo "======================================"
echo ""
echo "Launching BypassGPT..."
echo ""
sleep 1

python3 main.py
