## Code
The `requirements.txt` file in this directory contains all requirements to run all Python samples in the book.

### Preparing to run the code
The samples are all written in Python. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia*, type the following command:

`python3 -m venv dtia`

You can then activate the virtual environment by typing the following command

`source dtia/bin/activate`

The libraries that are required to run the code samples (including OCR and computer vision libraries) are defined in the requirements.txt file included in the books GitHub repository. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!