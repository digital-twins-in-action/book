# Grafana dashboard
This directory contains everything you need to run the Grafana dashboard example in Chapter 6. The dashboard uses the GraphQL API we created in Chapter 5, and this API in turn requires a Memgraph database server and a DynamoDB table. We will run all of these services as local Docker containers, so you do not need to use the cloud at all (although you could run all of these services in the cloud).

The DynamoDB table is loaded with data exported from my home sensors, with this data available as export files in the following directory:

`sensor-data`

## Getting started
You will need Docker installed, and you will need to create a Python virtualenv and load the requirements as described [here](../README.md).

All instructions have been tested on a Mac (Apple silicon), but should run without change on any Unix based operating system (and Windows too, although you will either need to use WSL / a terminal emulator, or transform the shell scripts to batch files).

You will need the following ports free:

- 6000 - for the GraphQL server
- 7687 - for the Memgraph server
- 8000 - for the DynamoDB server

## Running the data services
To start DynamoDB, Memgraph, and Grafana, run the following command:

`docker-compose up -d`

If it is the first time you have run the command, it will take some time for Docker to download the container images. The next time you run it, it should be faster.

## Loading the data to DynamoDB and Memgraph
You will need to load the sample sensor data (exported from my home digital twin) to DynamoDB, and the home knowledge graph (described in Chapter 5), to Memgraph. A shell script is provided for this purpose. You may need to make it executable first (with the command `chmod u+x setup.sh`). Run this data load by running the following command:

`./setup.sh`

### What this does
The data load will do the following:

1. Wait for all services to be ready
1. Load the knowledge graph to Memgraph
1. Create a DynamoDB table in the local server
1. Load the sample sensor data to the DynamoDB table

## Running the GraphQL API server
The last step before viewing the Grafana dashboard is to run the GraphQL server for Grafana to get data from. To do this, run the following command (make sure you are in your Python virtualenv and have the requirements loaded already!):

`python ../../ch05/digital_twin_api.py`

Once you see the GraphQL API server is running, you can login to Grafana at `http://localhost:3000`

## Viewing the dashboard

You should see the dashboard already created with a panel containing the refrigerator voltage. Bear in mind the data export only cntains limited data so you will need to choose a date that has data available (for example between November 21 and November 23 2025).

## How does it work?
The Grafana container is started with the [Infinity plugin](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) loaded. A datasource for the GraphQL API is defined in `provisioning/datasources`, and the dashboard itself is defined in `dashboards\digital-twin-dashboard.json`. When the Grafana container starts up, it provisions the datasource and the dashboard so it is all ready to go when you log into Grafana!