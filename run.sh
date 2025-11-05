#!/bin/bash
# Quick start script for Discordo Python

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_info "Using Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Install dependencies
print_info "Installing dependencies..."
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Copy default config if it doesn't exist
CONFIG_DIR="$HOME/.config/discordo"
CONFIG_FILE="$CONFIG_DIR/config.toml"

if [ ! -f "$CONFIG_FILE" ]; then
    print_info "Setting up configuration..."
    mkdir -p "$CONFIG_DIR"
    cp config.toml "$CONFIG_FILE"
    print_success "Configuration created at $CONFIG_FILE"
fi

# Run the application
print_info "Starting Discordo..."
python3 main.py "$@"
