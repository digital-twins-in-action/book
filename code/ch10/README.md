 
# Digital Twins in Action

## Chapter 10 - Digital Twins in Production
In this repository you will find the complete code samples from Chapter 10 of Digital Twins in Action where you learn how to run a digital twin in production.

### Preparing to run the code
The samples are all written in Python. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch10*, type the following command:

`python3 -m venv dtia_ch10`

You can then activate the virtual environment by typing the following command

`source dtia_ch10/bin/activate`

The libraries that are required to run the chapter 10 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!


#### 10.1 Define authorization policies using Cedar
This example shows how to use Cedar to define authorization policies and use the PermitIO implementation of the Cedar auth server (https://github.com/permitio/cedar-agent) to make an authorization decision. First of all run the server using Docker with

`docker run -p 8180:8180 permitio/cedar-agent`

Then run the code with the command

`python ch10_code01_biegel.py`

#### 10.2 Use OpenTelemetry for logging, metrics, and tracing
This example uses OpenTelemetry (https://opentelemetry.io/) to log, print metrics, and method traces.

Run the code with the command

`python ch10_code02_biegel.py`

#### 10.3 Use Evidently to report on data drift
This example shows how you can use Evidently (https://github.com/evidentlyai/evidently) to detect data drift.


Run the code with the command

`python ch10_code03_biegel.py`

An example of the output is available here https://3d.dtia.site/evidently/power_drift_report.html.
