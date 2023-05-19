#! /bin/bash


echo "$(dirname "$0")"
cd "$(dirname "$0")"
if command -v python3 &>/dev/null; then
    echo "Python3 is already installed"
else
    echo "Python3 is not installed. Please install Python3."
fi

# Update pip

pip install --upgrade pip >/dev/null 2>&1

# Check if virtual environment exists

if [ -d venv ]; then
    echo "Virtual environment already exists"
else
    echo "Creating virtual environment"
    python3 -m venv venv
fi

# Activate virtual environment
source ./venv/bin/activate

# Check if packages exists

if pip3 list -format=rows | grep -f requirements.txt; then
    echo "All dependencies are already installed"
else
    echo "Some dependencies are missing. Installing now..."
    pip3 install -r requirements.txt
fi

sleep 5
clear
# Run main.py
python3 main.py
