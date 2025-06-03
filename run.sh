#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for required files
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Error: requirements.txt file not found" >&2
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/run.py" ]; then
    echo "Error: run.py file not found" >&2
    exit 1
fi

# Create virtual environment directory
VENV_DIR="$SCRIPT_DIR/venv"

# Check Python version
if ! python3 --version >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed" >&2
    exit 1
fi

# Ensure venv module is available
if ! python3 -c "import venv" >/dev/null 2>&1; then
    echo "Error: Python venv module is not available. Please install:" >&2
    echo "Debian/Ubuntu: sudo apt install python3-venv" >&2
    echo "Red Hat/CentOS: sudo yum install python3-virtualenv" >&2
    exit 1
fi

# Remove existing virtual environment if it's broken
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Detected broken virtual environment, removing..."
    rm -rf "$VENV_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    # Check if virtual environment was created successfully
    if [ $? -ne 0 ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo "Virtual environment creation failed" >&2
        exit 1
    fi
fi

# Safely activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment activation failed" >&2
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Check installation result
if [ $? -ne 0 ]; then
    echo "Dependency installation failed" >&2
    deactivate
    exit 1
fi

# Execute Python script
echo "Starting run.py..."
if [ $# -gt 0 ]; then
    python "$SCRIPT_DIR/run.py" "$1"
else
    python "$SCRIPT_DIR/run.py"
fi
EXIT_STATUS=$?

# Deactivate virtual environment
deactivate

echo "Script execution completed"
exit $EXIT_STATUS
