End goal: user installs WSL + Ubuntu, then runs setup.sh to provision a full dev environment — no manual Python, MongoDB, or Docker setup needed.


May want to include in setup script something to set uLimits for MongoDB (this may also affect elasticsearch)


I'm going to need to make an updatable to check environment variable to set client depending on whether it'ss test or prod (Was I sleep deprived when I wrote this sentence?)

Need to figure out how to automatically swtich based on ENV variable (production vs testing) 


Kubernetes:
* Build and load Docker images into Minikube:
# Start Minikube
minikube start

# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build the image using the Dockerfile
docker build -t conquest-lims-api .

# Apply K8s configs
kubectl apply -f k8s/

* Test it
# Get Minikube IP
minikube_ip=$(minikube ip)

# Confirm service is up
curl http://$minikube_ip:30007/chemicals
(or open http://<minikube_ip>:30007/ in a browser)
* Run setup.sh from outside cluster once pods are up?





ES endpoints:
* Fuzzy search for chemicals by name
* Fuzzy search for lots by name
*
* Return aggregate values based on fuzzy search for chemical name?
* Return aggregate values based on fuzzy search for lot name?
*
* Find most popular chemical based on fuzzy search by name?
* (Double-check the prompt at this point now that the hard part is over)




# Where to pick up:
* Orchestrate with Minikube
* Update README and documentation to include containerization/Minikube (Project structure in specifications)
* Add ElasticSearch integration
* Update README, specifications.md, and api_reference.md to include ElasticSearch integration
* Finish README
* Proofread README.md, specification.md, and api_reference.md
    * api_reference.md needs error code returns standardized. Use testing strategy section for this.
    * Project file trees in both need final update
* Perform a clean reinstall of WSL and the project to ensure it works like the README says it does for set-up.