# Digital Twins in Action

## Chapter 4 - Integrating and managing data - code samples
In this repository you will find the complete code samples from Chapter 4 of Digital Twins in Action where you learn about how to integrate different data sources and store data in a digital twin.

### Preparing to run the code
The samples are all written in Python. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch04*, type the following command:

`python3 -m venv dtia_ch04`

You can then activate the virtual environment by typing the following command

`source dtia_ch04/bin/activate`

The libraries that are required to run the chapter 4 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!

#### 4.1 Example of querying spatial data to find items in close proximity
This example shows how you can use a simple Euclidian distance formula to find objects in a given proximity to a given point in local coordinate space (although you could project these local coordinates to UTM and use the same principle).

To run this example, execute the following command

`
python ch04_code01_biegel.py
`

#### 4.2 Example of integrating with the SAP API
To run this sample and explore the SAP APIs, you will need to head to https://api.sap.com and register in order to get an API key for the free sandbox API. Its quite a simple signup process. You'll get an idea of what it is like to integrate with a common ERP system via its API.

To run this example, execute the following command

`
python ch04_code02_biegel.py
`

#### 4.3 Example of querying a relational database
This example uses a simple SQLite database to demonstrate the concept of joining tables in a relational database using SQL. It loads data in the `maintenance.db` file in this directory and runs a query against it. SQLite is a fantastic tool to have in your toolbox.

To run this example, execute the following command

`
python ch04_code03_biegel.py
`

#### 4.4 Example of batch ingestion to a SQL database followed by querying the data with SQL
This example illustrates the batch ingestion of historical data, its staging in a local database, and then the use of SQL to analyze this data. This is a common scenario in a digital twin where past behaviour and data is used to predict future outcomes.

To run this example, execute the following command

`
python ch04_code04_biegel.py
`


#### 4.5 Example of ingesting a stream of events related to the UK rail network and running a sliding window over them
You will need to register for an account [here](https://publicdatafeeds.networkrail.co.uk/) in order to run this example. Its a simple signup process. How late are thr trains running today?

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

An example image returned by this script is shown below. I can get this same image daily and track changes in the lake over time.

![Kariba](images/lake_kariba_2025-08-23.png)

#### 4.7 Using Apache Spark to summarize power consumption data
This example shows the use of Apache Spark to summarize data from my PowerPal optical power sensor. If you do not have PySpark and Spark installed, you can use Docker to run the code. 

To build the Docker container from the included Dockerfile run

`
docker build -t pyspark-interactive .
`


To start the Docker container run:

`
docker run -it -v $(pwd):/app pyspark-interactive 
`

This will take you into a shell in the running container. You can then run the following command to execute the Spark job (it will use the PowerPal CSV data in this directory):

`
python ch04_code07_biegel.py
`

#### 4.8 Example of using SQL to directly query data in a Parquet file using DuckDB
This example shows how you can use SQL to directly query data stored in a Parquet file without the need to load it to a staging database first. SQL directly against Parquet? Very cool!

To run this example, execute the following command

`
python ch04_code08_biegel.py
`

#### 4.9 Example of using delta tables to enable ACID transactions over Parquet files
This example shows how delta tables can be used to both evolve a schema over a Parquet file (add a column), as well as to upsert new data to a table defined on a Parquet file.

To run this example, execute the following command

`
python ch04_code09_biegel.py
`

#### 4.10 An example of storing an querying timeseries data from DynamoDB
This example uses a local version of DynamoDB running in a Docker container so that you can run the example without the need to connect to AWS. 

To start the local DynamoDB server run the following command:

`
 docker run -p 8000:8000 amazon/dynamodb-local
`

<!-- `
dynamodump -m backup -r us-east-1 -s sensor-data 
` -->
I have exported some of the sensor data from my home digital twin's DynamoDB table using the DynamoDump tool (https://github.com/bchew/dynamodump). 
Once the container is running, you can load this sensor data to the local DynamoDB server by following these steps:

First of all, create the `sensor-data` table:

`
aws dynamodb create-table --table-name sensor-data \
    --attribute-definitions AttributeName=partKey,AttributeType=S AttributeName=sortKey,AttributeType=N \
    --key-schema AttributeName=partKey,KeyType=HASH AttributeName=sortKey,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST --endpoint-url http://127.0.0.1:8000 --region us-east-1
`

Then run the DynamoDump restore command

`
dynamodump -m restore -r local -s sensor-data --host 127.0.0.1 --port 8000  --region us-east-1 --dataOnly
`
Finally, check that the data has been imported successfully by checking how many records are in the table (there should be over 16,000)

`
aws dynamodb scan \
    --table-name sensor-data \
    --select COUNT --endpoint-url http://127.0.0.1:8000 --region us-east-1
`

Finally you can run the sample code by running:

`
python ch04_code10_biegel.py
`

## Deploying the data persistence code to AWS
The CloudFormation stack defined in the file `persistence_cfn.yml` will deploy a Lambda that consumes sensor data events from the SQS queue where they are published by the message decoder you deployed in the chapter 3 code, and create the DynamoDB table where this timeseries sensor data is persisted.

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