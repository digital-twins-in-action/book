 
# Digital Twins in Action

## Chapter 9
In this repository you will find the complete code samples from Chapter 9 of Digital Twins in Action where you learn to add intelligence to your digital twin with AI/ML.

### Preparing to run the code
The samples are all written in Python or HTML/JS. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system. 

:warning: **WARNING:** Unlike the other chapters in the book that all use Python **3.13**, I needed to use Python **3.11** with AutoGluon in Chapter 9. Please install Python 3.11 and use that to create the virtual environment for the Chapter 9 code samples. Instructions on how to do this are provided below.

Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch06*, type the following command:

`python3.11 -m venv dtia_ch09`

You can then activate the virtual environment by typing the following command

`source dtia_ch09/bin/activate`

To install AutoGluon, run the following commands:

```
pip install -U pip
pip install -U setuptools wheel
pip install autogluon --extra-index-url https://download.pytorch.org/whl/cpu 
```

The libraries that are required to run the chapter 6 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!

#### 9.0 Running the data pipeline
The data pipeline described in figure 9.1 in chapter 9 is implemented in the file [here](datapipeline/pipeline.py). To run the pipeline, execute the following command from within the datapipeline directory:

`
python pipeline.py
`

The pipeline will output a CSV file (that you can read with a spreadsheet viewer like Excel), and a Parquet file that is used by later AI/ML models. You will find both of these files checked in to GitHub too.

#### 9.1 Resample PowerPal electricity consumption data to hourly
This example demonstrates how I resample the data from my PowerPal electricity consumption data to be hourly, to align with other features. The PowerPal data can be found in the `data` directory.

Run it with the following command

`
python ch09_code01_biegel.py
`

#### 9.2 Cyclically encode time
This example demonstrates cyclically encoding time to convert it to features where times that are temporally close become numerically close.

Run it with the following command

`
python ch09_code02_biegel.py
`

#### 9.3 Calculate lagged features for indoor temperature
This example demonstrates calculating 1,2, and 3 hour lagged features for indoor temperature data.

Run it with the following command

`
python ch09_code03_biegel.py
`

#### 9.4 Calculate Z-score for indoor air quality of my home for November 2025
This example demonstrates calculating the Z-score to find anomalies in my indoor air quality for November 2025.

Run it with the following command

`
python ch09_code04_biegel.py
`

#### 9.5 Create an isolation forest ML model to detect anomalies in power and voltage consumption by my refrigerator
This example demonstrates using SciKit Learn to create an Isolation Forest model to detect anomalies in voltage and power consumption by my refrigerator 

Run it with the following command

`
python ch09_code05_biegel.py
`

#### 9.6 Create a histogram gradient boosting regressor ML model to predict indoor temperatures
This example demonstrates using SciKit Learn to create a histogram gradient boosting regressor ML model to predict indoor temperatures.

Run it with the following command

`
python ch09_code06_biegel.py
`

#### 9.7 Create an AutoML Timseries predictor with AutoGluon to predict net energy usage in my home
This example demonstrates using AutoGluon to create a Timeseries predictor model to predict net energy usage in my home. 

To train the model, run the following command

`
python ch09_code07_biegel.py
`

To create a visualization of its prediction over 48 hours, versus actual values, run the following command

`
python ch09_code07_biegel_visualize.py
`

#### 9.8 Create an image classifier to determine if my garage is open or shut with AutoGluon's MultiModal predictor
This example demonstrates using AutoGluon to create a MultiModal predictor model to determine if my garage door is open or shut.

To train the model, run the following command

`
python ch09_code08_biegel_train.py
`

To run a prediction with the model, run the following command

`
python ch09_code08_biegel_predict.py
`

#### 9.9 Perform retrieval augmented generation using a vector store of embeddings of my appliance manuals
This example creates a vector store of embeddings, and then uses this in a LangChain RAG pipeline to answer questions about my home appliances. It uses the Anthropic API, so you will need a valid API token configured before running the code with the following command

`
python ch09_code09_biegel.py
`

#### 9.10 A Strands SDK tool example
This example creates a tool using the Strands SDK that a Strands agent can use to get solar PV data from my Fronius Symo inverter. It cannot be run alone, but is used by the agent in 9.11.

#### 9.11 A Strands agent example
This example creates an AI agent using the Strands SDK that uses a number of tools to get PV production data, and climate data before following its system prompt to optimize the internal environment. It is configured to use Amazon Bedrock by default so you will need AWS credentials configured, with a role with the correct permissions to Bedrock, before attempting to run the agent with this command

`
python ch09_code11_biegel.py
`

 https://archive-api.open-meteo.com/v1/archive?latitude=-31.9522&longitude=115.8614&start_date=2025-01-01&end_date=2025-12-17&hourly=cloud_cover,temperature_2m,relative_humidity_2m,rain,direct_radiation_instant

