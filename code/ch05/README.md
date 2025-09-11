# Digital Twins in Action

## Chapter 5 - Modelling reality - code samples
In this repository you will find the complete code samples from Chapter 5 of Digital Twins in Action where you learn how to build a digital model of reality.

### Preparing to run the code
Instructions on how to setup your Python environment and install dependencies is provided [here](../README.md). You will only need to do this once - all dependencies are included.

#### 5.1 Example of fuzzy matching string identifiers
This example uses the [fuzzwuzz](https://github.com/seatgeek/thefuzz) library to fuzzily match identifiers. Matching identifiers between data sets is a commonly used mechanism for data contextualization.

To run this example, execute the following command

`
python ch05_code01_biegel.py
`

#### 5.2 Example DTDL file
This example contains a very simple JSON-LD file DTDL file to gove you a sense of the Digital Twin Definition Language.

#### 5.3 Example of building a simple knowledge graph in Memgraph
This example shows how you can build the simple knowledge graph of the thermostat in the hotel room shown in the book using [Memgraph](https://memgraph.com/).

Before running the code, ensure you are running Memgraph locally by running the following command:

`
docker run -p 7687:7687 -p 7444:7444 --name memgraph memgraph/memgraph-mage
`

You can run the Memgraph Lab container if you want to connect to your graph database and run queries and view the output visually with this command. This will create the graph as shown in the book, and run a traversal to get the battery percentage of the thermostat.
`
docker run -d -p 3000:3000 --name lab memgraph/lab
`

To run this example, execute the following command

`
python ch05_code03_biegel.py
`

#### 5.4 Run a simple home thermal physics model
This example shows a simple example of using a mathematical equation to model the thermal properties of a room in the house. It plots the output of the temperature change over time.

To run this example, execute the following command

`
python ch05_code04_biegel.py
`


#### 5.5 Run a simple GraphQL API
This example runs the simple GraphQL API shown in the book that orchestrates calls to a geocoding API and the Open Meteo API to retrieve a 7 day weather forecast for a given city.

To run this example, execute the following command

`
python ch05_code05_biegel.py
`

This will start the API. You can then run queries on the API using the cURL command (or any mechanism that can send a POST request).

Here is a sample command to get the weather forecast for Perth:

```
curl -X POST http://127.0.0.1:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ weather(city 'Perth') { time rain surfaceTemperature } }"
  }
```

The full GraphQL API that I have created for my home digital twin is available in the following file:-

`
digital_twin_api.py
`

This API orchestrates calls to the knowledge graph running in Memgraph, and then onto my timeseries data store in DynamoDB. You can run all this locally.

To create the knowledge graph of my house as described in the book, you can run the Cypher queries in the following file against the Memgraph database you have running locally (from 5.3):

`
home.cypher
`

You can also run DynamoDB locally as you learnt how to do in Chapter 4 in example 4.9 (or in AWS, whatever you prefer!).

Once you have the home API running, you can query it by POSTing data to the endpoint - an example query is shown below:

```
curl -X POST http://127.0.0.1:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ spaces(space: \"10 North St.\", startDate: \"2025-09-01T00:00:00Z\", endDate: \"2025-09-02T00:00:00Z\") { name measurements {name values {timestamp value}}} }"
  }'

```

#### 5.6 Asset administration shell
Running the following file will retrieve and print all available Asset Administration Shells from the API discussed in the book:

`
python ch05_code06_biegel.py
`