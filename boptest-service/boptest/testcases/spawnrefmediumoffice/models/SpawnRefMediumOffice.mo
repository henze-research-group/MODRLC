within ;
model SpawnRefMediumOffice
  "Spawn of EnergyPlus replica of the DOE Reference Medium Office Building
  VAV-Reheat based on Buildings.Examples.VAVReheat.Guideline36
  IDF: DOE Reference Medium Office Building"

  package Medium = Buildings.Media.Air;

  inner Buildings.ThermalZones.EnergyPlus.Building building(
    idfName=Modelica.Utilities.Files.loadResource(
        "Ressources/RefBldgMediumOfficeNew2004_v1.4_7.2_5B_USA_CO_BOULDER.idf"),
    weaName=Modelica.Utilities.Files.loadResource(
        "Ressources/USA_CO_Boulder.724699_TMY2.mos"),
    usePrecompiledFMU=false,
    logLevel=Buildings.ThermalZones.EnergyPlus.Types.LogLevels.Debug,
    showWeatherData=true,
    computeWetBulbTemperature=true,
    printUnits=true,
    generatePortableFMU=true)
    annotation (Placement(transformation(extent={{-86,62},{-66,82}})));

  Buildings.ThermalZones.EnergyPlus.ThermalZone corZon(
    zoneName="Core_ZN",
    redeclare final package Medium = Medium,
    nPorts=2)   "\"Core zone\""
    annotation (Placement(transformation(extent={{160,208},{200,248}})));
  PackagedMZVAVReheat packagedMZVAVReheat
    annotation (Placement(transformation(extent={{-48,-36},{92,28}})));
  Buildings.Fluid.Sources.Outside out(redeclare package Medium =
        Buildings.Media.Air, nPorts=12)
    annotation (Placement(transformation(extent={{-112,-18},{-92,2}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y=273.15)
    annotation (Placement(transformation(extent={{-102,20},{-82,40}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y=293.15)
    annotation (Placement(transformation(extent={{-102,38},{-82,58}})));
equation
  connect(out.ports[1], packagedMZVAVReheat.vavOAoutlet) annotation (Line(
        points={{-92,-4.33333},{-72,-4.33333},{-72,-18.4},{-48.2059,-18.4}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavOAinlet, out.ports[2]) annotation (Line(points=
         {{-48,-29.6},{-60,-29.6},{-60,-30},{-86,-30},{-86,-5},{-92,-5}}, color=
         {0,127,255}));
  connect(building.weaBus, out.weaBus) annotation (Line(
      points={{-66,72},{-120,72},{-120,-7.8},{-112,-7.8}},
      color={255,204,51},
      thickness=0.5));
  connect(packagedMZVAVReheat.vavReturnCore, out.ports[3]) annotation (Line(
        points={{13.5588,3.4},{-39.2206,3.4},{-39.2206,-5.66667},{-92,-5.66667}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavCoreOut, out.ports[4]) annotation (Line(points=
         {{23.2353,-4},{-34,-4},{-34,-6.33333},{-92,-6.33333}}, color={0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter1, out.ports[5]) annotation (
      Line(points={{34.7647,3.2},{-28.6177,3.2},{-28.6177,-7},{-92,-7}}, color={
          0,127,255}));
  connect(packagedMZVAVReheat.vavPerimeter1Out, out.ports[6]) annotation (Line(
        points={{41.1471,-4},{-25.4264,-4},{-25.4264,-7.66667},{-92,-7.66667}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter2, out.ports[7]) annotation (
      Line(points={{51.8529,3.4},{-20.0736,3.4},{-20.0736,-8.33333},{-92,
          -8.33333}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavPerimeter2Out, out.ports[8]) annotation (Line(
        points={{57.6176,-4},{-18,-4},{-18,-9},{-92,-9}}, color={0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter3, out.ports[9]) annotation (
      Line(points={{66.8824,3.4},{-12.5588,3.4},{-12.5588,-9.66667},{-92,
          -9.66667}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavPerimeter3Out, out.ports[10]) annotation (Line(
        points={{72.2353,-4},{-10,-4},{-10,-10.3333},{-92,-10.3333}}, color={0,127,
          255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter4, out.ports[11]) annotation (
      Line(points={{82.7353,3.4},{-4.63235,3.4},{-4.63235,-11},{-92,-11}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavPerimeter4Out, out.ports[12]) annotation (Line(
        points={{87.0588,-3.8},{-2.4706,-3.8},{-2.4706,-11.6667},{-92,-11.6667}},
        color={0,127,255}));
  connect(realExpression1.y, packagedMZVAVReheat.senTemRoom) annotation (Line(
        points={{-81,48},{-66,48},{-66,27.2},{-50.4706,27.2}}, color={0,0,127}));
  connect(realExpression.y, packagedMZVAVReheat.senTOut) annotation (Line(
        points={{-81,30},{-66,30},{-66,23.4},{-50.2647,23.4}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    uses(Buildings(version="8.0.0"), Modelica(version="3.2.3")));
end SpawnRefMediumOffice;
