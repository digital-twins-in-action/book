model WaterTankDrainage
  import Modelica.Constants.pi;

  inner Modelica.Fluid.System system (1)
    annotation (Placement(transformation(extent={{60,60},{80,80}})));

  Modelica.Fluid.Vessels.OpenTank tank( (2)
    redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater,
    crossArea = pi * (1.5/2)^2,  // 1.767 m²
    height = 3.0,                // Max tank height
    level_start = 2.0,           // Initial water level
    nPorts = 1,                  // Number of ports
    portsData = {Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(
                   diameter = 0.01, // Hole diameter
                   height = 0.0)})  // Port at bottom of tank
    annotation (Placement(transformation(extent={{-20,20},{20,60}})));

  Modelica.Fluid.Sources.Boundary_pT atmosphere( (3)
    redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater,
    nPorts = 1,
    p = 101325,  // Atmospheric pressure (Pa)
    T = 293.15)  // Temperature (K)
    annotation (Placement(transformation(extent={{60,-20},{40,0}})));

equation
  connect(tank.ports[1], atmosphere.ports[1]) (4)
    annotation (Line(points={{0,20},{0,-10},{50,-10}}, color={0,127,255}));

end WaterTankDrainage;