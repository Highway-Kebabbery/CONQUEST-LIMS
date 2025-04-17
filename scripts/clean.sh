#!/bin/bash
set -e


echo "Stopping and removing all Docker containers and volumes for this project..."
docker compose down -v

echo "Pruning dangling Docker images and containers..."
docker system prune -f

echo -n "Remove all Minikube resources and all persistent volume claims? (y/N)"
read -r answer
case "$answer" in
    [yY][eE][sS]|[yY])
        echo "Removing Minikube resourced and pvc..."
        kubectl delete all --all
        kubectl delete pvc --all
        ;;
    *)
        echo "Skipping Minikube resource and pvc cleanup."
        ;;
esac

echo -n "Delete Minikube cluster, all resources, and reset Docker env? (y/N)"
read -r answer
case "$answer" in
    [yY][eE][sS]|[yY])
        echo "Unsetting Docker env and deleting Minikube cluster..."
        eval $(minikube docker-env --unset)
        minikube delete --all --purge
        ;;
    *)
        echo "Skipping Minikube cleanup."
        ;;
esac

echo "Clean-up complete. System can now be re-deployed from scratch."