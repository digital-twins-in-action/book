 
# Digital Twins in Action

## Chapter 8 - Predicting outcomes with simulation
In this repository you will find the complete code samples from Chapter 8 of Digital Twins in Action where you learn how to use simulation to predict outcomes.

### Preparing to run the code
The samples are all written in Python. Some of the sample code uses example data also found in this repository. 
To run the code, you will need a version of Python 3 installed on your system - the code has been tested with the latest release at the time of writing (3.13.7). Installers for Python are available from the Python website at https://www.python.org/. 

I recommend using the *virtualenv* tool to create an isolated Python environment in which to run the code and isolate dependencies from your main Python installation. Since Python 3.3 a subset of virtualenv, known as *venv* has been integrated into the standard library.

To create a virtual environment named *dtia_ch08*, type the following command:

`python3 -m venv dtia_ch08`

You can then activate the virtual environment by typing the following command

`source dtia_ch08/bin/activate`

The libraries that are required to run the chapter 8 code samples are defined in the requirements.txt file in this directory. To install the required libraries in your virtual environment, run the following command

`pip install -r requirements.txt`

You are now ready to run the code samples and adapt them to your own use case!


#### 8.1 Solve an ordinary differential equation with Python
This example shows how you can use Python to sole an ordinary differential equation that represents how fast fluid flows out of an opening (Torecelli's law).

Run it with the following command

`
python ch08_code01_biegel.py
`


#### 8.2 Modeling tank drainage in OpenModelica
In this example we model tank drainage again, but this time using OpenModelica for acausal modeling. The source for the OpenModelica model is available in the file:

`ch08_code01_biegel.om`

The easiest way to run this example is to use Docker to run the OpenModelica GUI. As a pre-requisite you will need an X-server running for the GUI to be able to open on your local machine. I use a Mac, and [XQuartz](https://www.xquartz.org/) for this, making sure to first whitelist my local address with the following command:

`xhost + 127.0.0.1`

Then I can run the OpenModelica GUI with the following Docker command

```
docker run -it --rm \
    -v "$HOME:$HOME" \
    -e "HOME=$HOME" \
    -w "$PWD" \
    -e "DISPLAY=host.docker.internal:0" \
    --user $UID \
    openmodelica/openmodelica:v1.25.7-gui \
    OMEdit
```

Once the OpenModelica GUI opens, load the file above, and press the Simulate button to setup a simulation:

![simulate](images/simulate.png)

#### 8.3 Run a simulation using an FMU created from the OpenModelica model
In this example, you use [FMPy](https://fmpy.readthedocs.io/) to run a simulation in Python, using the FMU created from the OpenModelica tank drainage model.

To create the FMU, you can follow the instructions in the book in section 8.3.3. I build the FMU on a 64-bit x86 Linux instance (on an AWS EC2 instance), since I had issues in being able to build it on my Mac which has an Apple silicon processor. The built FMU is included in this repository [here](./WaterTankDrainage.fmu), and you can execute it on the same platform it was built for (but not other platforms such as Windows or Mac). It is possible to build the FMU for other platforms, and is a useful exercise, I just took the path of least resistance!

To run the example, run the following command

`
python ch08_code01_biegel.py
`

#### 8.4 Integrating sensor data with continuous simulation
This example contains all the code to run the example of a simulation that incorporates sensor data (known as _data assimilation_). The code contains a simple FMU (implemented as a Python method although an exercise is to replace this with a call to a real FMU file via FMPy), and uses an unscented Kalman filter (via the [FilterPy](https://filterpy.readthedocs.io/) library) to fuse sensor data and simulated predictions together.

To run the example, run the following command

`
python ch08_code04_biegel.py
`

#### 8.5 Python generator function
This example shows a simple Python generator function that represents a traffic light and introduces the concept of yielding events that is at the core of the SimPy framework. To 

To run the example, run the following command

`
python ch08_code05_biegel.py
`

#### 8.6 Discrete event simulation of home power consumption
This example uses [SimPy](https://simpy.readthedocs.io/) to create a simple DES of charging home appliances, with a maximum power consumption constraint. 

To run the example, run the following command

`
python ch08_code06_biegel.py
`

To run multiple simulation runs as a Monte Carlo simulation, run the following command

`
python ch08_code06_biegel_montecarlo.py
`

#### 8.7 Example of FEM using FreeFEM
This example uses the [FreeFEM](https://freefem.org/) high level multiphysics finite element software to demonstrate the concept of meshing and solving a finite set of partial differential equations to simulate the transfer of heat across a metal plate. 

You can either install FreeFEM, or use a docker container to execute the example code with the following command

```
docker run --rm \
    -v "$(pwd):/data" freefem/freefem FreeFem++ \
    -nw /data/ch08_code07_biegel.edp    
```


#### 8.8 CFD example using JAX to simulate the movement of cool air from an air conditioner, through a room
This example demonstrates how a computational fluid dynamics based simulation can be used to understand how the placement of a wall mounted air conditioner unit impacts the flow of cold air through a hot room. It uses JAX (Just  After eXecution), an open source Python library for high performance numerical computing that can run on GPUs.

The example uses JAX and the projection method to solve Navier-Stokes equations that describe how fluid moves.

To run the example, run the following command

`
python ch08_code08_biegel.py
`

The projection method works as follows:

1. The Predictor Step (Advection + Diffusion)
Code function: advection_term + laplacianFirst, we ignore pressure entirely. We calculate an intermediate velocity field (often called $u^*$) based on two forces:
- Advection: The inertia of the fluid. If the air was moving right, it wants to keep moving right.
- Diffusion: The viscosity. Fast-moving air drags slower air along with it, smoothing out the flow.The Problem: The result ($u^*$) is physically impossible. It might "squeeze" air into a corner, violating the rule that air is incompressible.

2. The Pressure Step (Poisson Equation)Code function: pressure_poissonWe measure exactly how "broken" our intermediate field is by calculating its Divergence.
- Positive Divergence: Air is being created out of nothing (impossible).

- Negative Divergence: Air is being destroyed (impossible).We then solve a mathematical puzzle (the Poisson equation): "What pressure field $P$ would push the air just enough to cancel out this divergence?"

3. The Corrector Step (Projection)Code function: `u_new = u_star - DT * dpdx`
Finally, we use that pressure field to correct our velocity.High pressure pushes air away; low pressure sucks it in.Subtracting the pressure gradient from our predictor field removes the divergence perfectly.

Result: A physically valid velocity field ($u^{n+1}$) that moves the fluid correctly and respects mass conservation.

![cooling](images/ac_cooling_animation.gif)

#### 8.9 A simple linear regression based reduced order model (ROM)
This example shows the use of a linear regression model trained on a full order model simulation (in this example a simplified FMU implemented as a Python method), to create a reduced order model that simulates the temperature of a room given what power a sdpace heater is set at, the ambient, and external temperatures.

To run the example, run the following command

`
python ch08_code09_biegel.py
`

### Useful links

https://www.leapaust.com.au/blog/fea/simulation-enabled-digital-twin/