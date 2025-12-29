 
# Digital Twins in Action

## Chapter 7 - 3D visualization and spatial representation - code samples
In this repository you will find the complete code samples from Chapter 7 of Digital Twins in Action where you learn how to build 3D and spatial visualizations.

### Preparing to run the code
The samples are all written in Python or HTML/JS. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch07*, type the following command:

`python3 -m venv dtia_ch07`

You can then activate the virtual environment by typing the following command

`source dtia_ch07/bin/activate`

The libraries that are required to run the chapter 7 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!


#### 7.1 Simple OBJ file of a cube
This example is a simple OBJ file of a cube [here](ch07_code02_biegel.obj). Open it at https://3dviewer.net/.

#### 7.2 Sample cube in Three.js
This example uses Three.js to render the OBJ file created from the 3D model of my home built with SweetHome3D.

Open the file [here](ch07_code02_biegel.html) in a web browser like Chrome to view it.

#### 7.3 3D model of the home, geolocated and rendered in CesiumJS
This example shows how you can use CesiumJS to render the 3D model in specific geographical location (together with 3D models from Open Street Map).

You can look at the source code in the file `ch07_code03_biegel.html`, but you will not be able to open this file from the filesystem. This is because my embedded Cesium Ion API key is restricted to specific domains. You can serve it on http://localhost:8080 (which is allowed by the token), or you can view it hosted on the book site here https://3d.dtia.site/cesium/index.html.


#### 7.4 3D model of the home, geolocated and rendered in CesiumJS with data overlaid
This example builds on the previous example, but adds spatially located data overlays to the Cesium scene. It also adds another tileset to the scene (generated from the example photogrammetry process in appendix D of the book). 

You can look at the source code in `ch07_code04_biegel.html`.

Again, you'll need to host this file locally on http://localhost:8080 if you want to view and modify it on your machine. You can view it hosted on the book site here https://3d.dtia.site/cesium/popup/index.html

#### 7.5 A very simple USD file
This example contains the simplest possible USD file possible to create a cube. You can open the below file at https://imagetostl.com/view-usd-online and then experiment with extending it

`
ch07_code05_biegel.usd
` 

#### 7.6 Other example files
There are some other example files from Chapter 7 as follows:

- *Virtual reality example* - the file [here](dtia_site/vr/index.html) contains the home 3D model with VR mode enabled in Cesium that you could use with a cardboard viewer and your phone. Also available here https://3d.dtia.site/vr/index.html

- *Photogrammetry example pump* - the file [here](dtia_site/pump/index.html) contains the model of a pump created using photogrammetry, and rendered with three.js. Also available here https://3d.dtia.site/pump/index.html

- *Photogrammetry example mower* - the file [here](dtia_site/mower/index.html) contains the model of my mower created using photogrammetry, and rendered with three.js. https://3d.dtia.site/mower/index.html

- *LiDAR sandpile* - the file [here](dtia_site/sandpile/index.html) contains the model of a sandpile created using the LiDAR sensor on an iPad, and rendered with three.js. Also available here https://3d.dtia.site/sandpit/index.html

- *3D model of my home* - my home 3D model as an OBJ file and associated materials and textures can be found [here](3dmodel/) 

- *Reality scan files* - the photos taken with Reality Scan for the photogrammetry example in Appendix D can be found [here](photogrammetry/images/)