within ;
model workshop_pt_1_overrides_sensors
  Modelica.Blocks.Math.Sin sin1
    annotation (Placement(transformation(extent={{-24,30},{-4,50}})));
  Modelica.Blocks.Sources.Constant const(k=1)
    annotation (Placement(transformation(extent={{-116,30},{-96,50}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite overwrite(u(
      min=0,
      max=7,
      unit="1"))
    annotation (Placement(transformation(extent={{-62,30},{-42,50}})));
  Buildings.Utilities.IO.SignalExchange.Read read(y(
      min=0,
      max=1,
      unit="1"), KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
    annotation (Placement(transformation(extent={{24,30},{44,50}})));
equation
  connect(const.y, overwrite.u)
    annotation (Line(points={{-95,40},{-64,40}}, color={0,0,127}));
  connect(sin1.u, overwrite.y)
    annotation (Line(points={{-26,40},{-41,40}}, color={0,0,127}));
  connect(sin1.y, read.u)
    annotation (Line(points={{-3,40},{22,40}}, color={0,0,127}));
  annotation (uses(Modelica(version="3.2.3"), Buildings(version="8.0.0")));
end workshop_pt_1_overrides_sensors;
