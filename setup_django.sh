#!/bin/bash

# Django Setup Script for macOS and Windows (Git Bash/WSL)
# This script checks and installs Python, pip, Django and other dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WINDIR" ]]; then
        OS="windows"
        log_info "Detected Windows"
    else
        log_error "Unsupported operating system. This script supports macOS and Windows only."
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew on macOS
install_homebrew() {
    if ! command_exists brew; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for current session
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        log_success "Homebrew installed successfully"
    else
        log_info "Homebrew is already installed"
    fi
}

# Install Python
install_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_info "Python $PYTHON_VERSION is already installed"
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            log_info "Python $PYTHON_VERSION is already installed"
            PYTHON_CMD="python"
        else
            log_warning "Python 2.x detected. Python 3.x is required for Django."
            install_python3
        fi
    else
        log_info "Python not found. Installing Python 3..."
        install_python3
    fi
}

install_python3() {
    if [[ "$OS" == "macos" ]]; then
        install_homebrew
        brew install python3
        PYTHON_CMD="python3"
    elif [[ "$OS" == "windows" ]]; then
        log_info "Please install Python 3 from https://www.python.org/downloads/"
        log_info "Make sure to check 'Add Python to PATH' during installation"
        log_error "Please install Python manually and run this script again"
        exit 1
    fi
    
    log_success "Python 3 installed successfully"
}

# Check and install pip
install_pip() {
    if command_exists pip3; then
        PIP_CMD="pip3"
        log_info "pip3 is already installed"
    elif command_exists pip; then
        PIP_CMD="pip"
        log_info "pip is already installed"
    else
        log_info "pip not found. Installing pip..."
        if [[ "$OS" == "macos" ]]; then
            $PYTHON_CMD -m ensurepip --upgrade
        elif [[ "$OS" == "windows" ]]; then
            $PYTHON_CMD -m ensurepip --upgrade
        fi
        PIP_CMD="pip3"
        log_success "pip installed successfully"
    fi
    
    # Upgrade pip to latest version
    log_info "Upgrading pip to latest version..."
    $PYTHON_CMD -m pip install --upgrade pip
}

# Create virtual environment
create_virtual_environment() {
    VENV_NAME="django_env"
    
    if [[ -d "$VENV_NAME" ]]; then
        log_info "Virtual environment '$VENV_NAME' already exists"
    else
        log_info "Creating virtual environment '$VENV_NAME'..."
        $PYTHON_CMD -m venv $VENV_NAME
        log_success "Virtual environment created successfully"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    if [[ "$OS" == "windows" ]]; then
        source $VENV_NAME/Scripts/activate
    else
        source $VENV_NAME/bin/activate
    fi
    
    log_success "Virtual environment activated"
}

# Install Django and dependencies
install_django() {
    log_info "Installing Django and common dependencies..."
    
    # Create requirements.txt if it doesn't exist
    if [[ ! -f "requirements.txt" ]]; then
        log_info "Creating requirements.txt with common Django dependencies..."
        cat > requirements.txt << EOF
Django>=4.2,<5.0
psycopg2-binary
pillow
python-decouple
djangorestframework
django-cors-headers
celery
redis
EOF
        log_success "requirements.txt created"
    fi
    
    # Install from requirements.txt
    pip install -r requirements.txt
    
    log_success "Django and dependencies installed successfully"
}

# Verify installation
verify_installation() {
    log_info "Verifying installations..."
    
    # Check Python
    if command_exists python3 || command_exists python; then
        PYTHON_VER=$($PYTHON_CMD --version)
        log_success "Python: $PYTHON_VER"
    else
        log_error "Python verification failed"
        return 1
    fi
    
    # Check pip
    if command_exists pip3 || command_exists pip; then
        PIP_VER=$(pip --version | cut -d' ' -f1-2)
        log_success "Pip: $PIP_VER"
    else
        log_error "Pip verification failed"
        return 1
    fi
    
    # Check Django
    if $PYTHON_CMD -c "import django; print(f'Django: {django.get_version()}')" 2>/dev/null; then
        DJANGO_VER=$($PYTHON_CMD -c "import django; print(django.get_version())")
        log_success "Django: $DJANGO_VER"
    else
        log_error "Django verification failed"
        return 1
    fi
    
    log_success "All verifications passed!"
}

# Display next steps
show_next_steps() {
    echo ""
    log_info "Setup completed successfully! Next steps:"
    echo ""
    echo "1. Activate your virtual environment:"
    if [[ "$OS" == "windows" ]]; then
        echo "   source django_env/Scripts/activate"
    else
        echo "   source django_env/bin/activate"
    fi
    echo ""
    echo "2. Create a new Django project:"
    echo "   django-admin startproject myproject"
    echo ""
    echo "3. Navigate to your project and run the development server:"
    echo "   cd myproject"
    echo "   python manage.py migrate"
    echo "   python manage.py runserver"
    echo ""
    log_success "Happy coding with Django!"
}

# Main execution
main() {
    log_info "Starting Django setup script..."
    echo ""
    
    detect_os
    install_python
    install_pip
    create_virtual_environment
    install_django
    verify_installation
    show_next_steps
}

# Run main function
main