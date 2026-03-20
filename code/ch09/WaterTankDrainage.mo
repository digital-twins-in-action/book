model WaterTankDrainage
  import Modelica.Constants.pi;

  // System object required for Modelica.Fluid models
  inner Modelica.Fluid.System system
    annotation (Placement(transformation(extent={{60,60},{80,80}})));

  // Tank with ONE port defined
  Modelica.Fluid.Vessels.OpenTank tank(
    redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater,
    crossArea = pi * (1.5/2)^2,     // 1.767 m²
    height = 3.0,                    // Max tank height
    level_start = 2.0,               // Initial water level
    nPorts = 1,                      // Number of ports (MUST match portsData size!)
    portsData = {Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(
                   diameter = 0.01,   // Hole diameter
                   height = 0.0)})    // Port at bottom of tank
    annotation (Placement(transformation(extent={{-20,20},{20,60}})));

  // Boundary condition (atmosphere)
  Modelica.Fluid.Sources.Boundary_pT atmosphere(
    redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater,
    nPorts = 1,
    p = 101325,                      // Atmospheric pressure (Pa)
    T = 293.15)                      // Temperature (K)
    annotation (Placement(transformation(extent={{60,-20},{40,0}})));

equation
  // Connect tank port to atmosphere
  connect(tank.ports[1], atmosphere.ports[1])
    annotation (Line(points={{0,20},{0,-10},{50,-10}}, color={0,127,255}));

end WaterTankDrainage;