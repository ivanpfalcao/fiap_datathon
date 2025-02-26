# FIAP Datathon Project - Pos Tech ML Engineering

## Overview
This repository contains the codebase and resources for the FIAP Datathon - Pos Tech ML Engineering. The project includes machine learning workflows, API scripts, containerization files, and Kubernetes deployment configurations.

## Folder Structure

```
fiap_datathon-master/
├── .gitignore                
├── containers/
│   ├── 01-build-news-recomender.sh                # Builds API dockerfile
│   ├── news-recomender.dockerfile                 # API dockerfile
├── fiap_datathon_app/                             # Main application source code
│   ├── pyproject.toml                             # Python package dependencies
│   ├── src/                                       # Application source code
│   │   ├── fiap_datathon_app/
│   │   │   ├── __init__.py                  
│   │   │   ├── api.py                             # API definition (FastAPI)
│   │   │   ├── data/                              # Data storage directory
│   │   │   │   ├── data_prep.py                   # Data preprocessing script
│   │   │   │   ├── inference_test.py              # Model inference testing
│   │   │   │   ├── massive_first_news_add.py      # First News data ingestion script
│   │   │   │   ├── massive_news_add.py            # News ingestion script
│   │   │   ├── ml/                                # Machine learning models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── recommendation.py              # Recommendation model
├── k8s/
│   ├── 01-deploy-news-recommender.sh              # Deploys news recommender and Qdrant on a k8s cluster
│   ├── news-recommender-dpl.yaml                  # News recommender and Qdrant k8s definitions
├── minikube/
│   ├── 01-enable-nvidiagpu.sh                     # Enables Nvidia GPU on a minikube cluster
│   ├── 02-minikube-start-gpu.sh                   # Creates minikube cluster with GPU enabled
├── sh/
│   ├── 00-install-api.sh                          # Install the API on a local environment
│   ├── 01-run-api.sh                              # Runs the API locally
│   ├── 20-dataprep.sh                             # Runs data preparation locally
│   ├── 21-add-massive-news.sh                     # Add news through API Massively
│   ├── 22-search-massive-news.sh                  # Massive request 
│   ├── 23-add-massive-first-news.sh               # Add first news historic Massively
│   ├── 90-docker-qdrant.sh                        # Run Qdrant locally
│   ├── inference_test.py                          # Request individual news recommendation
```

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- Docker (for containerized deployment)
- Kubernetes or Minikube

### Running locally

1. Clone the repository:
   ```sh
   git clone https://github.com/ivanpfalcao/fiap_datathon.git
   cd fiap_datathon
   ```

2. Install dependencies:
   ```sh
   bash sh/00-install-api.sh
   ```

3. Run the API locally:
   ```sh
   bash sh/01-run-api.sh
   ```

## Running on Kubernetes

1. Build the Docker container:
   ```sh
   bash containers/01-build/news-recomender.sh
   
   # Push to a repo if needed
   ```
2. Run application on Kubernetes:
   ```sh
   bash k8s/01-deploy-news-recommender.sh
   ```

## Results

- Good recommendations: 77,4% (168/217)
- Medium recommendations: 4,1% (9/217)
- Wrong recommendations: 18,5% (40/217)

## License
This project is licensed under the MIT License.