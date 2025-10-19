 
# Digital Twins in Action

## Chapter 6 - Visualizing the digital world - code samples
In this repository you will find the complete code samples from Chapter 5 of Digital Twins in Action where you learn how to build a digital model of reality.

### Preparing to run the code
The samples are all written in Python. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch06*, type the following command:

`python3 -m venv dtia_ch06`

You can then activate the virtual environment by typing the following command

`source dtia_ch06/bin/activate`

The libraries that are required to run the chapter 6 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!
#### 6.1 Example of fuzzy matching string identifiers
This is an example of how to integrate the GraphQL API that we built in - [Chapter 5](../ch05/README.md), with an HTML file, to visualize the data that has been acquired by sensors and persisted to DynamoDB. Before loading this HTML file, you should make sure you have the home digital twin graphql API running, as described in [Chapter 5](../ch05/README.md) (Section 5.5)- this in turn requires you have the local DynamoDB server running and the sensor data loaded as described in [Chapter 3](../ch03/README.md).

Once that is working, simply open the following file in Chrome or your favorite web browser (there is no need to serve the HTML file from a web server, you can just open it from your filesystem!).

`
ch06_code01_biegel.html
`

This page simply gets all sensor data, and graphs it - very simple. Look in the browser dev tools to see the network call made to the GraphQL API as shown below

![Sensor data](images/sensordata.png)

That is just the simplest example to show retrieving and rendering data (I did not want to full pages of the book with code!). When you're happy that is working, you can open the following file in the same way to get a bit more of an interactive dashboard that allows you to select spaces in my home (remember how these are related in the Knowledge Graph?), and view the data from them.

`
ch06_code01_biegel_full.html
`

You should see the view below:

![Dashboard](images/dashboard.png)

#### 6.2 Ramer-Douglas-Peucker (RDP) algorithm to decimate timeseries data 
This example shows how you can use the Ramer-Douglas-Peucker (RDP) algorithm to decimate timeseries data for effectively showing graphs of large numbers of data points.

Run it with the following command

`
python ch06_code02_biegel.py
`

You will see an image like below. Try varying the epsilon value and running again.

![RDP](images/rdp.png)

#### 6.3 Sample cube in OBJ
This example shows how you use vertices, edges, faces, and normals in a text file as OBJ format, to build a 3D object.

Go to https://3dviewer.net/ and load the file `ch06_code03_biegel.obj`


#### 6.4 Show 3D home model in three.js
This example shows how you can use the [three.js](https://threejs.org/) JavaScript library to render the OBJ file of the 3D model of my home.

Simply open the file `ch06_code04_biegel.html` in your favorite browser from the filesystem. The code uses the OBJ file that is hosted on the book site at https://3d.dtia.site/model/DigitalTwinsInAction.obj.

The page is also hosted at https://3d.dtia.site/model/home3d.html.

#### 6.5 Use CesiumJS to geolocate and render my home 3D model 
This example shows how you can use CesiumJS to render the 3D model in specific geographical location (together with 3D models from Open Street Map).

You can look at the source code in the file `ch06_code05_biegel.html`, but you will not be able to open this file from the filesystem. This is because my embedded Cesium Ion API key is restricted to specific domains. You can serve it on http://localhost:8080 (which is allowed by the token), or you can view it hosted on the book site here https://3d.dtia.site/cesium/index.html.


#### 6.6 Overlay data in Cesium scene
This example builds on the previous example, but adds spatially located data overlays to the Cesium scene. It also adds another tileset to the scene (generated from the example photogrammetry process in appendix D of the book). 

You can look at the source code in `ch06_code06_biegel.html`.

Again, you'll need to host this file locally on http://localhost:8080 if you want to view and modify it on your machine. You can view it hosted on the book site here https://3d.dtia.site/cesium/popup/index.html

#### 6.7 Sample USD file
This example contains the simplest possible USD file possible to create a cube. You can open the below file at https://imagetostl.com/view-usd-online and then experiment with extending it

`
ch06_code07_biegel.usd
`


#### 6.8 Other example files
There are some other example files from Chapter 6 as follows:

- *Graph example* - the file [here](uplotbands.html)  displays the uPlot graph example in Chapter 6.

- *Virtual reality example* - the file [here](dtia_site/vr/index.html) contains the home 3D model with VR mode enabled in Cesium that you could use with a cardboard viewer and your phone. Also available here https://3d.dtia.site/vr/index.html

- *Photogrammetry example pump* - the file [here](dtia_site/pump/index.html) contains the model of a pump created using photogrammetry, and rendered with three.js. Also available here https://3d.dtia.site/pump/index.html

- *Photogrammetry example mower* - the file [here](dtia_site/mower/index.html) contains the model of my mower created using photogrammetry, and rendered with three.js. https://3d.dtia.site/mower/index.html

- *LiDAR sandpile* - the file [here](dtia_site/sandpile/index.html) contains the model of a sandpile created using the LiDAR sensor on an iPad, and rendered with three.js. Also available here https://3d.dtia.site/sandpit/index.html

- *3D model of my home* - my home 3D model as an OBJ file and associated materials and textures can be found [here](3dmodel/) 

- *Reality scan files* - the photos taken with Reality Scan for the photogrammetry example in Appendix D can be found [here](photogrammetry/images/)