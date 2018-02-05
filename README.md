# Beer Details
This service provides _details_ about a single or collection of beers.

* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Development](#development)
* [Deployment](#deployment)


## <a name="prerequisites"></a>Prerequisites:
* [Docker](https://www.docker.com) installed and running
* [Docker Compose](https://www.docker.com/products/docker-compose) installed
* [Google Cloud Platform](https://cloud.google.com/) project created
* [Google Cloud Platform SDK](https://cloud.google.com/sdk/) installed and configured 
* [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/) cluster created 


## <a name="setup"></a>Setup:
Set your **PROJECT_ID** environment variable

        export PROJECT_ID="$(gcloud config get-value project -q)"

Set your **CLUSTER_NAME** environment variable

        export CLUSTER_NAME=beers-cluster

Set the credentials for the GKE cluster

        gcloud container clusters get-credentials $CLUSTER_NAME


## <a name="development"></a>Development:
Build and run the development environment as a Docker application locally. Make changes accordingly.

        TAG=dev make dev


## <a name="deployment"></a>Deployment:
Define the version number as the _TAG_ environment variable and build the image.

        export TAG=<VERSION NUMBER>
        make

Tag and push the new image for GCR 

         docker tag <IMAGE ID> gcr.io/${PROJECT_ID}/beer-details-api:${TAG}
         gcloud docker -- push gcr.io/${PROJECT_ID}/beer-details-api:${TAG}


### Deployment Updates:
Update the container image name/version for an existing deployment

        kubectl set image deployment/details-api details-api=gcr.io/${PROJECT_ID}/beer-details-api:${TAG}


## To-Do
* automated builds
