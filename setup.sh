#!/bin/bash

# errexit; exit script if any errors encountered
set -e

check_and_prompt_install() {
    local package="$1"
    local install_command="$2"

    if ! command -v "$package" &> /dev/null; then
        echo -n "$package is not installed. Install it? (Y/n): "
        read -r answer
        case "$answer" in
            [nN][oO]|[nN])
                echo "$package is required. Exiting."
                exit 1
                ;;
            *)
                echo "Installing $package..."
                if [ -n "$install_command" ]; then
                    eval "$install_command"
                else
                    sudo apt-get update
                    sudo apt-get install -y "$package"
                fi
                ;;
        esac
    else
        echo "$package is already installed."
    fi
}

echo "Checking for required tools..."

check_and_prompt_install docker
check_and_prompt_install docker compose
check_and_prompt_install jq
check_and_prompt_install minikube \
"curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb && \
sudo dpkg -i minikube_latest_amd64.deb && \
rm minikube_latest_amd64.deb"


# Spin up Docker containers
echo "Spinning up Docker containers..."
echo "Existing volumes will be deleted for this project."
docker compose down -v
docker compose up --build -d

echo "Waiting for services to stabilize..."
sleep 5

# Make scripts executable
chmod +x scripts/*.sh

# Load required and demonstration objects
echo "Loading initial database content..."
bash scripts/load_data.sh

# Run smoke tests
echo "Running smoke tests..."
bash scripts/smoke_test.sh

# Donezo
echo "Setup complete. Visit http://localhost:5000/"