#!/bin/bash
set -e

echo "Stopping and removing all Docker containers and volumes for this project..."
docker compose down -v

echo "Pruning dangling Docker images and containers..."
docker system prune -f

echo "Clean-up complete. System can now be re-deployed from scratch."
