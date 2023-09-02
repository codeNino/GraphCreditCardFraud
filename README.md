# Credit Card Fraud Detection with Graph Data Science

The goal of this project is to analyse credit card transactions and find fraudulent patterns by modelling the dataset as relational graphs leveraging the Neo4j graph database with its data visualization capabilities offered by the Bloom plug in.

The Neo4j database instance is run locally as a [Docker Image] (https://hub.docker.com/_/neo4j) and the Bloom Client is hosted on a Python ASGI web server developed with the [FastAPI framework] (https://fastapi.tiangolo.com/).


## Project directory

├── db-server/
|    └── static/
|    └── templates/
│    ├── __init__.py
|    └── .dockerignore
|    └── discovery.json
|    └── docker-compose.yml
|    └── Dockerfile
│    ├── main.py
|    ├── Makefile
│    └── requirements.txt
|  
├── data-ingestion-pipeline/
│   ├── Fraud_Analysis.ipynb
│   └── fraudTrain.csv
|   └── __init__.py
|   └──  Makefile
|   └── requirements.txt
├── README.md

db-server/: This directory contains files to spin up the neo4j database instance and application code for the web server that runs the Bloom client.

  static/: Holds static assets for the Bloom interface such as CSS, JavaScript, images, etc.
  templates/: Contains HTML template used for rendering view.
  __init__.py: Initializes the FastAPI application and other extensions.
  .dockerignore: Specify which files and directories should be excluded (ignored) from the Docker Image build context.
  discovery.json: Contains the discovery URL which the Bloom client uses to connect to the intended Neo4j database server. 
  Dockerfile: Contains instructions for building the bloom server Image.
  main.py: The entry point of the application, used to run the development server.
  requirements.txt: Lists all the Python dependencies required for the project.
  docker-compose.yml: Defines and manages all the services, networks, volumes, and other configurations required to run the set of interconnected containers for the bloom-server and neo4j database as a single application stack.
  Makefile: Automates the building and running of all application code.

data-ingestion-pipeline/: This directory contains all application code for data preprocessing and loading into the database.

  Fraud_Analysis.ipynd: Ipython (Jupyter) notebook with explanations and procedures for transforming raw dataset into relational graphs in the neo4j database.
  fraudTrain.csv: Credit Card Transaction dataset in csv format.
  __init__.py: Initializes the data-ingestion-pipeline package.
  Makefile: Automates the running of the data ingestion pipeline to extract dat from raw csv, create relational graph and load into graph database for visualization.
  pipeline.py: data ingestion script.
  util.py: module containing helper objects for data ingestion pipeline.
  

STEP 1: Python and Docker on your PC.

  ## To Install Python on windows, ubuntu or mac os

    Visit [Python Docs] (https://wiki.python.org/moin/BeginnersGuide/Download) or Read (https://kinsta.com/knowledgebase/install-python/) for installation guides.

  ## To install Docker on windows, ubuntu or mac os
    Visit the [Docker docs] (https://docs.docker.com/get-docker/) or Read up (https://www.knowledgehut.com/blog/devops/docker-installation) for installation guides.

  ## Install Docker compose
    Read the docker docs for steps on how to set up [docker compose] (https://docs.docker.com/compose/install/)



STEP 2: To Run Database Instance and also View already Loaded Data.

  ## Enter the db-server directory to start the neo4j database.


  ## Start Neo4j Database and Bloom Client Server
      use command `make run` or `sudo make run` if root permission is required.
    
    Log into the bloom interface in your browser by visiting http://localhost:8000/
    You can also interact with the neo4j database in your browser without the bloom client interface by visiting http://localhost:7474/browser/

    Sign in with 
      - username == neo4j
      - password == password

  ## Stop Neo4j Database and Bloom Client Server
      use command `make stop` or `sudo make stop` if root permission is required

  ## Remove Database image and Bloom Client Server

    use command `make clean` or `sudo make clean` if root permission is required 


STEP 3: To Load Data into Database

  ## Enter the data-ingestion-pipleine
    Store the transactions dataset in the directory:
      You can download the dataset with this link (https://drive.google.com/file/d/1YefVzG9sbi9MrrOXIZnoZQ6MJ9zJKmG8/view?usp=sharing)
    Instantiate the Class Object in the pipeline.py script to work with the name of your dataset if it differs from `fraudTrain.csv`

    e.g pipe = CCFraudPipeline({name_of_your_dataset})


  ## Run the pipeline script to populate your already runnning neo4j Database

    use command `make run` or `sudo make run` if root permission is required.

  