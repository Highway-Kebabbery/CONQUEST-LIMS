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

check_and_prompt_install docker \
"curl -fsSL https://get.docker.com -o get-docker.sh && \
sh get-docker.sh && \
rm get-docker.sh && \
sudo usermod -aG docker \$USER && \
echo -e 'Docker installed. Restart your terminal and then rerun ./setup.sh.\n \
NOTE: '\''exec \$SHELL'\'' is not guaranteed to work for this operation on WSL.' && \
exit 0"

check_and_prompt_install jq


# Spin up containers locally using docker compose for dev not requiring Minikube
: '
# Spin up Docker containers
API_URL=$"http://localhost:5000"

check_and_prompt_install docker compose

echo "Spinning up Docker containers..."
echo "Existing volumes will be deleted for this project."
docker compose down -v
docker compose up --build -d

echo "Waiting for API to be responsive..."
for i in {1..15}; do
  if (
    curl -s "$API_URL/lists" > /dev/null &&
    curl -s "$API_URL/lots" > /dev/null &&
    curl -s "$API_URL/chemicals" > /dev/null
  ); then
    break
  else
    echo "Waiting for API... ($i/15)"
    sleep 15
  fi
done

if ! curl -s "$API_URL/" > /dev/null; then
  echo "API did not become available in time."
  exit 1
fi
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

check_and_prompt_install kubectl \
"curl -LO https://dl.k8s.io/release/\$(curl -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl && \
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
rm kubectl"

minikube start --driver=docker
eval $(minikube docker-env)
docker build -t conquest-lims-api .
kubectl apply -f k8s/

minikube_ip=$(minikube ip)

API_URL="http://$minikube_ip:30007"

echo -e "Waiting for conquest-lims-api to become available...\n\n"
echo -e "Full disclosure:\n \
Each readiness check takes 30 seconds. Expect a ~3.5-minute initialization.\n \
I do not know why the app takes so long to initialize when run in k8s. The \n \
initialization time increased by about 2.5 minutes after implementing \n \
Elasticsearch. I would love to optimize performance, but I am far beyond \n \
being out of time to do that.\n\n"

for i in {1..20}; do
  if {
    curl -s --max-time 3 "$API_URL/" > /dev/null &&
    curl -s --max-time 3 "$API_URL/lists" > /dev/null &&
    curl -s --max-time 3 "$API_URL/chemicals" > /dev/null &&
    curl -s --max-time 3 "$API_URL/lots" > /dev/null;
  }; then
    echo "Cluster is ready."
    break
  else
    echo "Waiting... ($i/20)"
    sleep 30
  fi
done

if ! curl -s "$API_URL/" > /dev/null; then
  echo "Cluster did not become available in time."
  exit 1
fi
#'

# Make scripts executable
chmod +x scripts/*.sh

# Load required and demonstration objects
echo "Loading initial database content..."
bash scripts/load_data.sh "$API_URL"

# Run smoke tests
echo "Running API smoke tests..."
bash scripts/smoke_test.sh "$API_URL"

# Donezo
echo "Setup complete. Visit or send requests to: $API_URL/"
