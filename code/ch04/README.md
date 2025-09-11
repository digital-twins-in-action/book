# Digital Twins in Action

## Chapter 4 - Integrating and managing data - code samples
In this repository you will find the complete code samples from Chapter 4 of Digital Twins in Action where you learn about how to integrate different data sources and store data in a digital twin.

### Preparing to run the code
Instructions on how to setup your Python environment and install dependencies is provided [here](../README.md). You will only need to do this once - all dependencies are included.s

#### 4.1 Example of querying a relational database
This example uses a simple SQLite database to demonstrate the concept of joining tables in a relational database using SQL. It loads data in the `maintenance.db` file in this directory and runs a query against it.

To run this example, execute the following command

`
python ch04_code01_biegel.py
`

#### 4.2 Example of querying spatial data to find items in close proximity
This example shows how you can use a simple Euclidian distance formula to find objects in a given proximity to a given point. By using projected UTM coordinates the maths is much simpler than would be the case with a spherical coordinate system.

To run this example, execute the following command

`
python ch04_code02_biegel.py
`

#### 4.3 Example of integrating with the SAP API
To run this sample and explore the SAP APIs, you will need to head to api.sap.com and register in order to get an API key for the free sandbox API. Its quite a simple signup process. You'll get an idea of what it is like to integrate with a common ERP system via its API.

To run this example, execute the following command

`
python ch04_code03_biegel.py
`

#### 4.4 Example of batch ingestion to a SQL database followed by querying the data with SQL
This example illustrates the batch ingestion of historical data, its staging in a local database, and then the use of SQL to analyze this data. This is a common scenario in a digital twin where past behaviour and data is sued to predict future outcomes.

To run this example, execute the following command

`
python ch04_code04_biegel.py
`


#### 4.5 Example of ingesting a stream of events related to the UK rail network and running a sliding window over them
You will need to register for an account at in order to run this example. Its a simple signup process.

To run this example, execute the following command

`
python ch04_code05_biegel.py
`

#### 4.6 An example of querying a NASA REST API to get an image of the largest man made lake on the planet
This example demonstrates integrating with a freely available REST API to retrieve geophysical data from satellite imagery.

You can adjust the bounding box coordinates to get pretty much anywhere on earth!

To run this example, execute the following command

`
python ch04_code06_biegel.py
`

An example image returned by this script is shown below

![Kariba](images/lake_kariba_2025-08-23.png)

#### 4.7 Example of using SQL to directly query data in a Parquet file using DuckDB
This example shows how you can use SQL to directly query data stored in a Parquet file without the need to load it to a staging database first. 

To run this example, execute the following command

`
python ch04_code07_biegel.py
`


#### 4.8 An example of storing an querying timeseries data from DynamoDB
This example uses a local version of DynamoDB running in a Docker container so that you can run the example without the need to connect to AWS. 

To start the local DynamoDB server run the following command:

`
 docker run -p 8000:8000 amazon/dynamodb-local
`

Once the container is running, you can load the sample data by running:

`
python populate_dynamo.py
`

Finally you can run the sample code by running:

`
python ch04_code09_biegel.py
`

## Deploying the data persistence code to AWS
The CloudFormation stack defined in the file `persistence_cfn.yml` will deploy a Lambda that consumes sensor data events from the SQS queue where they are published by the message decoder you deployed in the chapter 2 code, and create the DynamoDB table where this timeseries sensor data is persisted.

### Preparing the Lambda function code
After you have made any modifications to the Lambda function code (for example to implement a decoder function for your specific LoRaWAN sensor payload), you must zip it up with the following command

```
zip data_persistor_lambda.zip data_persistor.py
```
Then upload the `data_persistor_lambda.zip` file to your S3 bucket.

## Deploying the CloudFormation stack
To deploy the stack, in the AWS console navigate to CloudFormation -> Stacks -> Create stack and select the CloudFormation template.

## Creating a Memgraph server running on EC2 in AWS
I use a Memgraph server running on EC2 in my home digital twin to serve the graph database. The CloudFormation script in `memgraph-server.yml` will setup a publically accessible Memgraph database for you.

[!CAUTION]
The CloudFormation script makes the EC2 server publically accessible. This is just for testing, be sure to change the 'AllowedCIDR' group from 0.0.0.0/0 (global access) to your specific IP address to only allow you to connect.