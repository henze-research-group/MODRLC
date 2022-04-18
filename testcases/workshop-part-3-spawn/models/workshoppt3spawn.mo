within ;
model workshoppt3spawn
  Buildings.Utilities.IO.SignalExchange.Overwrite overwrite(u(
      min=0,
      max=1,
      unit="1"))
    annotation (Placement(transformation(extent={{-66,-22},{-46,-2}})));
  Buildings.Utilities.IO.SignalExchange.Read read(KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
      y(
      min=273.15,
      max=303.15,
      unit="K"))
    annotation (Placement(transformation(extent={{100,20},{120,40}})));
  inner Buildings.ThermalZones.EnergyPlus.Building building(idfName=
        Modelica.Utilities.Files.loadResource(
        "/SpawnResources/workshop-part-3-spawn/1ZoneUncontrolled.idf"), weaName
      =Modelica.Utilities.Files.loadResource(
        "/SpawnResources/workshop-part-3-spawn/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos"))
    annotation (Placement(transformation(extent={{-76,22},{-56,42}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone zon(
    zoneName="ZONE ONE",
    redeclare package Medium = Buildings.Media.Air,
    nPorts=2) annotation (Placement(transformation(extent={{38,-76},{78,-36}})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u hea(
    redeclare package Medium = Buildings.Media.Air,
    m_flow_nominal=1,
    dp_nominal=50,
    Q_flow_nominal=500)
    annotation (Placement(transformation(extent={{-2,-76},{18,-56}})));
  Buildings.Fluid.Movers.FlowControlled_m_flow fan(redeclare package Medium =
        Buildings.Media.Air, m_flow_nominal=1)
    annotation (Placement(transformation(extent={{-52,-74},{-32,-54}})));
  Modelica.Blocks.Sources.Constant const(k=0.5)
    annotation (Placement(transformation(extent={{-126,-48},{-106,-28}})));
  Modelica.Blocks.Sources.Constant const1(k=0)
    annotation (Placement(transformation(extent={{-4,42},{16,62}})));
  Modelica.Blocks.Sources.Constant const2(k=0)
    annotation (Placement(transformation(extent={{-4,16},{16,36}})));
  Modelica.Blocks.Sources.Constant const3(k=0)
    annotation (Placement(transformation(extent={{-4,-10},{16,10}})));
  Modelica.Blocks.Routing.Multiplex3 multiplex3_1
    annotation (Placement(transformation(extent={{32,16},{52,36}})));
  Modelica.Blocks.Sources.Constant const4(k=0)
    annotation (Placement(transformation(extent={{-98,-22},{-78,-2}})));
equation
  connect(zon.TAir, read.u) annotation (Line(points={{79,-38},{84,-38},{84,30},
          {98,30}}, color={0,0,127}));
  connect(const.y, fan.m_flow_in) annotation (Line(points={{-105,-38},{-42,-38},
          {-42,-52}}, color={0,0,127}));
  connect(fan.port_b, hea.port_a) annotation (Line(points={{-32,-64},{-16,-64},
          {-16,-66},{-2,-66}}, color={0,127,255}));
  connect(hea.port_b, zon.ports[1]) annotation (Line(points={{18,-66},{30,-66},
          {30,-80},{56,-80},{56,-75.1}}, color={0,127,255}));
  connect(fan.port_a, zon.ports[2]) annotation (Line(points={{-52,-64},{-54,-64},
          {-54,-88},{60,-88},{60,-75.1}}, color={0,127,255}));
  connect(const1.y, multiplex3_1.u1[1]) annotation (Line(points={{17,52},{24,52},
          {24,33},{30,33}}, color={0,0,127}));
  connect(const2.y, multiplex3_1.u2[1]) annotation (Line(points={{17,26},{24,26},
          {24,26},{30,26}}, color={0,0,127}));
  connect(const3.y, multiplex3_1.u3[1]) annotation (Line(points={{17,0},{17,10},
          {30,10},{30,19}}, color={0,0,127}));
  connect(multiplex3_1.y, zon.qGai_flow) annotation (Line(points={{53,26},{60,
          26},{60,-14},{26,-14},{26,-46},{36,-46}}, color={0,0,127}));
  connect(const4.y, overwrite.u)
    annotation (Line(points={{-77,-12},{-68,-12}}, color={0,0,127}));
  connect(overwrite.y, hea.u) annotation (Line(points={{-45,-12},{-32,-12},{-32,
          -22},{-4,-22},{-4,-60}}, color={0,0,127}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    uses(Buildings(version="8.0.0"), Modelica(version="3.2.3")));
end workshoppt3spawn;
