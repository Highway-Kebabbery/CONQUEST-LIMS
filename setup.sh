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
check_and_prompt_install jq


# Spin up containers locally using docker compose for dev not requiring Minikube
: '
# Spin up Docker containers
check_and_prompt_install docker compose

echo "Spinning up Docker containers..."
echo "Existing volumes will be deleted for this project."
docker compose down -v
docker compose up --build -d

echo "Waiting for services to stabilize..."
sleep 5
'

# Check for and start Minikube
## Only use when testing orchestration. Too much overhead for app dev.

## Basic flow (notes to self):
##   * Start Minikube. Set driver for consistency on WSL (spins up k8s cluster 
##   inside a Docker container on local machine).
##   * Set local `docker` commands to point to Minikube's Docker daemon.
##   * Send local directory as context to build a containger image inside 
##   Minikube. This is a docker command, so the image mut be `-t` tagged for 
##   later reference by k8s.
##  * Apply all manifests in k8s/ to the currently-active cluster.
##  * Test/get Minikube ip address
##  * Confirm service is up

#: '
check_and_prompt_install minikube \
"curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb && \
sudo dpkg -i minikube_latest_amd64.deb && \
rm minikube_latest_amd64.deb"

minikube start --driver=docker
eval $(minikube docker-env)
docker build -t conquest-lims-api .
kubectl apply -f k8s/

minikube_ip=$(minikube ip)

echo "Waiting for conquest-lims-api to become available..."

for i in {1..10}; do
  if (
    curl -s --max-time 3 "http://$minikube_ip:30007/" > /dev/null &&
    curl -s --max-time 3 "http://$minikube_ip:30007/lists" > /dev/null &&
    curl -s --max-time 3 "http://$minikube_ip:30007/chemicals" > /dev/null &&
    curl -s --max-time 3 "http://$minikube_ip:30007/lots" > /dev/null); then
    echo "Cluster is ready."
    break
  else
    echo "Waiting... ($i/10)"
    sleep 3
  fi
done

if ! curl -s "http://$minikube_ip:30007/" > /dev/null; then
  echo "Cluster did not become available in time."
  exit 1
fi
#'

# Make scripts executable
chmod +x scripts/*.sh

# Load required and demonstration objects
echo "Loading initial database content..."
bash scripts/load_data.sh "$minikube_ip"

# Run smoke tests
echo "Running API smoke tests..."
bash scripts/smoke_test.sh "$minikube_ip"

# Donezo
echo "Setup complete. Visit or send requests to: http://$minikube_ip:30007/"