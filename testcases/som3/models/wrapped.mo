within ;
model wrapped "Wrapped model"
model SOM3 "Spawn replica of the Reference Small Office Building"

  // User input //
  String idfPat = "RefBldgSmallOfficeNew2004.idf";         // insert .idf file path
  String weaPat = "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw";         // insert  .mos file path

  //Parameters//
  Real OAInfCore = 0.36 / 3600 "OA infiltration in the core zone (air changes per second, ACS)";
  Real OAInfP1 = 0.265 / 3600 "OA infiltration in the perimeter zone 1, ACS";
  Real OAInfP2 = 0.298 / 3600 "OA infiltration in the perimeter zone 2, ACS";
  Real OAInfP3 = 0.265 / 3600 "OA infiltration in the perimeter zone 3, ACS";
  Real OAInfP4 = 0.298 / 3600 "OA infiltration in the perimeter zone 4, ACS";

  package Medium = Buildings.Media.Air "Moist Air"; // Moist air

  //Spawn//

  inner Buildings.ThermalZones.EnergyPlus.Building building(
    idfName=Modelica.Utilities.Files.loadResource(
        "modelica://Buildings/Resources/Data/ThermalZones/EnergyPlus/Validation/RefBldgSmallOffice/RefBldgSmallOfficeNew2004_Chicago.idf"),
    weaName=Modelica.Utilities.Files.loadResource(
        "modelica://Buildings/Resources/weatherdata/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos"),
    usePrecompiledFMU=false,
    verbosity=Buildings.ThermalZones.EnergyPlus.Types.Verbosity.Verbose,
    showWeatherData=true,
    computeWetBulbTemperature=true,
    printUnits=true,
    generatePortableFMU=true)
    annotation (Placement(transformation(extent={{-274,72},{-254,92}})));

  Buildings.ThermalZones.EnergyPlus.ThermalZone corZon(
    zoneName="Core_ZN",                                redeclare final package
        Medium =                                                                        Medium,
      nPorts=4) "\"Core zone\""
    annotation (Placement(transformation(extent={{54,64},{94,104}})));

    // Fluids - non HVAC //
  Buildings.Fluid.Sources.Outside Outside(redeclare final package Medium = Medium,
      nPorts=20)
    "Outside environment boundary condition that uses the weather data from Spawn"
    annotation (Placement(transformation(extent={{-204,-2},{-184,18}})));

    // Fluids - HVAC //
    model ASHRAESystem3 "PZS-AC Constant Air Volume Packaged Single Zone Rooftop Unit"

      //Parameters - Fluids//
      parameter Modelica.SIunits.MassFlowRate mass_flow_nominal = 0.5 "Nominal Mass Flow Rate (kg/s)";
      parameter Modelica.SIunits.Pressure dp_nominal = 10 "Nominal Pressure Drop (Pa)";
      parameter Modelica.SIunits.Power heaNomPow = 100 "Gas Heater Nominal Power (W)";
      parameter Modelica.SIunits.Power CCNomPow = 100 "Cooling coil Nominal Power (W)";

      model System3RBControls "Rule-Based controls replicating those of the DOE Ref. Small Office Building"
        //Parameters //
        //Schedule//

        Real day "Day of the week (1: Mon, 7:Sun)";
        Real hou "Hour of the day (24-hour format)";
        parameter Real staOcc = 5 "Start of day (24-hour)";
        parameter Real stoOcc = 21 "End of day (24-hour)";    // staOcc and stoOcc are currently fixed (the RefBldgSmallOffice case has a simple schedule)
        parameter Real stoOccSat = 17 "End of day (24-hour)";
          //Setpoints//

        parameter Real heaOccSet = 273.15 + 21 "Heating setpoint for occupied mode";
        parameter Real heaNonOccSet = 273.15 + 15.6 "Heating setpoint for non occupied mode";
        parameter Real maxRH = 0.5 "Relative Humidity setpoint";
        parameter Real minOACCOpeTemp = 273.15 "Minimum outside air temperature for cooling coil operation";

        parameter Real cooOccSet = 273.15 + 24 "Cooling setpoint for occupied mode";
        parameter Real cooNonOccSet = 273.15 + 26.7 "Cooling setpoint for non occupied mode";

        parameter Real fanOccSet = 0.44 "Fan volumetric flow rate when operating (m3/s)";
        parameter Real fanMinVFR = 0.01 "Fan minimum volumetic flow rate (m3/s)";

        parameter Real damSetOcc = 0.3 "Mixing box OA volumetric flow rate - occupied mode (m3/s)";
        parameter Real damSetNonOcc = 0.08 "Minimum OA volumetric flow rate (m3/s)";
        parameter Real minOAHVACOn = 0.2 "Minimum OA fraction (% total airflow), HVAC on (Ashrae 60.1)";
        parameter Real minOAHVACOff = 0.08 "Minimum OA fraction (m3/s), HVAC off (Ashrae 60.1)";
        Real OAset = 0.08 "Current OA setpoint";

          //Controls//



        //parameter Real timShoCyc = 600 "Time constant for short cycling control (seconds)";
        //Boolean timRes "timer reset";

        // Inputs/Outputs//

        Modelica.Blocks.Interfaces.RealInput senTemRet annotation (Placement(
              transformation(extent={{-660,268},{-620,308}}),
                                                            iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-628,78})));
        Modelica.Blocks.Interfaces.RealOutput outDamSet annotation (Placement(
              transformation(extent={{662,124},{700,162}}),
                                                          iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={713,-41})));
        Modelica.Blocks.Interfaces.RealOutput outHeaSet annotation (Placement(
              transformation(extent={{660,278},{698,316}}),
                                                          iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={713,111})));

        // Control components //

        //Buildings.Controls.OBC.CDL.Logical.TimerAccumulating timerShortCycling(t=timShoCyc)
        //  annotation (Placement(transformation(extent={{32,4},{52,24}})));

        Modelica.Blocks.Interfaces.RealOutput outCCSet annotation (Placement(
              transformation(extent={{660,174},{698,212}}),
                                                          iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={713,63})));
        Modelica.Blocks.Interfaces.RealInput senFanVFR annotation (Placement(
              transformation(extent={{-652,-260},{-612,-220}}),
                                                              iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-630,-46})));
        Modelica.Blocks.Interfaces.RealOutput outFanSet
                                                       annotation (Placement(
              transformation(extent={{660,232},{698,270}}),
                                                          iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={713,15})));
        Modelica.Blocks.Interfaces.RealInput senDamVFR annotation (Placement(
              transformation(extent={{-652,-212},{-612,-172}}),iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-628,-166})));
        Modelica.Blocks.Interfaces.RealInput senTemOut annotation (Placement(
              transformation(extent={{-662,302},{-622,342}}),
                                                            iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-634,306})));

        //Modelica.Blocks.Sources.BooleanExpression boo1(y=timRes)
        //  annotation (Placement(transformation(extent={{-80,4},{-60,24}})));

        Modelica.Blocks.Interfaces.RealInput senHRRet annotation (Placement(
              transformation(extent={{-836,4},{-796,44}}),
              iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-630,-274})));
        Modelica.Blocks.Interfaces.RealInput senTemSup "\"Supply air temperature\""
          annotation (Placement(transformation(extent={{-840,138},{-800,178}}),
              iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-628,196})));
        Modelica.Blocks.Sources.RealExpression houIn(y=hou) "hour" annotation (
            Placement(transformation(extent={{-582,256},{-562,276}})));
        Modelica.Blocks.Sources.RealExpression dayIn(y=day) "day" annotation (
            Placement(transformation(extent={{-582,242},{-562,262}})));
        Modelica.Blocks.Sources.RealExpression coolingSetpointOccupied(y=
              cooOccSet) annotation (Placement(transformation(extent={{-294,218},
                  {-274,238}})));
        Modelica.Blocks.Sources.RealExpression coolingSetpointNonOccupied(y=
              cooNonOccSet) annotation (Placement(transformation(extent={{-296,
                  174},{-276,194}})));
        Modelica.Blocks.Sources.RealExpression fanSetpointOccupied(y=fanOccSet)
          annotation (Placement(transformation(extent={{-282,126},{-262,146}})));
        Modelica.Blocks.Sources.RealExpression fanSetpointNonOccupied(y=
              fanMinVFR) annotation (Placement(transformation(extent={{-282,110},
                  {-262,130}})));
        Modelica.Blocks.Sources.RealExpression occStart(y=staOcc) annotation (
            Placement(transformation(extent={{-582,220},{-562,240}})));
        Modelica.Blocks.Sources.RealExpression occStop(y=stoOcc) annotation (
            Placement(transformation(extent={{-582,192},{-562,212}})));
        Modelica.Blocks.Sources.RealExpression occStopSat(y=stoOccSat)
          annotation (Placement(transformation(extent={{-582,162},{-562,182}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater staOccGre annotation (
            Placement(transformation(extent={{-492,228},{-472,248}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater stoOccGre annotation (
            Placement(transformation(extent={{-518,200},{-498,220}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater stoOccSatGre annotation (
            Placement(transformation(extent={{-518,170},{-498,190}})));
        Buildings.Controls.OBC.CDL.Logical.Not not1
          annotation (Placement(transformation(extent={{-490,200},{-470,220}})));
        Buildings.Controls.OBC.CDL.Logical.Not not2
          annotation (Placement(transformation(extent={{-490,170},{-470,190}})));
        Buildings.Controls.OBC.CDL.Logical.And houOccWeekdays annotation (
            Placement(transformation(extent={{-452,228},{-432,248}})));
        Buildings.Controls.OBC.CDL.Logical.And houOccSaturday annotation (
            Placement(transformation(extent={{-454,200},{-434,220}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater weekend annotation (
            Placement(transformation(extent={{-518,140},{-498,160}})));
        Modelica.Blocks.Sources.RealExpression fri(y=5) annotation (Placement(
              transformation(extent={{-582,132},{-562,152}})));
        Modelica.Blocks.Sources.RealExpression sat(y=6) annotation (Placement(
              transformation(extent={{-582,104},{-562,124}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater sunday annotation (
            Placement(transformation(extent={{-518,112},{-498,132}})));
        Buildings.Controls.OBC.CDL.Logical.And saturday annotation (Placement(
              transformation(extent={{-460,140},{-440,160}})));
        Buildings.Controls.OBC.CDL.Logical.Not not3
          annotation (Placement(transformation(extent={{-490,112},{-470,132}})));
        Buildings.Controls.OBC.CDL.Logical.Not not4
          annotation (Placement(transformation(extent={{-426,140},{-406,160}})));
        Buildings.Controls.OBC.CDL.Logical.And weekdays annotation (Placement(
              transformation(extent={{-400,120},{-380,140}})));
        Buildings.Controls.OBC.CDL.Logical.Switch cooSetpoint annotation (
            Placement(transformation(extent={{-184,192},{-164,212}})));
        Buildings.Controls.OBC.CDL.Logical.Switch fanSetpoint annotation (
            Placement(transformation(extent={{-250,118},{-230,138}})));
        Buildings.Controls.OBC.CDL.Logical.And occSaturday annotation (
            Placement(transformation(extent={{-370,200},{-350,220}})));
        Buildings.Controls.OBC.CDL.Logical.And occWeekday annotation (Placement(
              transformation(extent={{-370,228},{-350,248}})));
        Buildings.Controls.OBC.CDL.Logical.Or or2
          annotation (Placement(transformation(extent={{-340,208},{-320,228}})));
        Buildings.Controls.SetPoints.Table heaSetTab(table=[heaOccSet - 3,1;
              heaOccSet + 0.5,0])
          annotation (Placement(transformation(extent={{14,278},{34,298}})));
        Buildings.Controls.SetPoints.Table heaSetTabNonOcc(table=[heaNonOccSet
               - 1.5,1; heaNonOccSet + 1.5,0])
          annotation (Placement(transformation(extent={{14,246},{34,266}})));
        Buildings.Controls.OBC.CDL.Logical.Switch heaSetLinear
                                                              annotation (
            Placement(transformation(extent={{56,262},{76,282}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater neeCool(h=1.5)
          annotation (Placement(transformation(extent={{8,132},{28,152}})));
        Buildings.Controls.OBC.CDL.Logical.Timer tim(t=1800)
          annotation (Placement(transformation(extent={{84,80},{104,100}})));
        Buildings.Controls.OBC.CDL.Logical.Latch lat
          annotation (Placement(transformation(extent={{118,72},{138,92}})));
        Buildings.Controls.OBC.CDL.Logical.Not ccTurnedOff
          annotation (Placement(transformation(extent={{60,42},{80,62}})));
        Buildings.Controls.OBC.CDL.Logical.And and2
          annotation (Placement(transformation(extent={{152,132},{172,152}})));
        Buildings.Controls.OBC.CDL.Logical.Edge risEdgCC
          annotation (Placement(transformation(extent={{90,42},{110,62}})));
        Buildings.Controls.OBC.CDL.Logical.Not ccTurnedOff1 annotation (Placement(
              transformation(
              extent={{-10,-10},{10,10}},
              rotation=180,
              origin={162,118})));
        Buildings.Controls.OBC.CDL.Logical.Switch damSetLinear
          annotation (Placement(transformation(extent={{130,-74},{150,-54}})));
        Buildings.Controls.SetPoints.Table damSetTabHea(table=[cooOccSet - 1.5,0;
            cooOccSet,1])
          annotation (Placement(transformation(extent={{90,-58},{110,-38}})));
        Buildings.Controls.SetPoints.Table damSetTabHeaNonOcc(table=[
            cooNonOccSet - 1.5,0; cooNonOccSet,1])
          annotation (Placement(transformation(extent={{90,-90},{110,-70}})));
        Buildings.Controls.OBC.CDL.Logical.Switch damSetLinear1
          annotation (Placement(transformation(extent={{162,-112},{182,-92}})));
        Buildings.Controls.OBC.CDL.Logical.Switch damSetLinear2
          annotation (Placement(transformation(extent={{130,-154},{150,-134}})));
        Buildings.Controls.SetPoints.Table damSetTabCoo(table=[heaOccSet,1; heaOccSet +
              1.5,0])
          annotation (Placement(transformation(extent={{92,-136},{112,-116}})));
        Buildings.Controls.SetPoints.Table damSetTabCooNonOcc(table=[heaNonOccSet,1;
              heaNonOccSet + 1.5,0])
          annotation (Placement(transformation(extent={{92,-168},{112,-148}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater ecoHea(h=0.5)
          annotation (Placement(transformation(extent={{16,-112},{36,-92}})));
        Buildings.Controls.OBC.CDL.Logical.Or or1
          annotation (Placement(transformation(extent={{324,152},{344,172}})));
        Buildings.Controls.OBC.CDL.Logical.Switch fanSetLinear
          annotation (Placement(transformation(extent={{394,108},{414,128}})));
        Modelica.Blocks.Sources.RealExpression fanSetpointOccupied1(y=fanOccSet)
          annotation (Placement(transformation(extent={{362,116},{382,136}})));
        Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea
          annotation (Placement(transformation(extent={{184,-6},{204,14}})));
        Buildings.Controls.OBC.CDL.Continuous.Feedback feedback
          annotation (Placement(transformation(extent={{440,108},{460,128}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai(k=10)
          annotation (Placement(transformation(extent={{478,108},{498,128}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add2
          annotation (Placement(transformation(extent={{516,114},{536,134}})));
        Buildings.Controls.OBC.CDL.Logical.Pre pre
          annotation (Placement(transformation(extent={{-10,-10},{10,10}},
              rotation=180,
              origin={122,118})));
        Buildings.Controls.OBC.CDL.Continuous.GreaterThreshold greThr(t=0.01, h=
             0.01)
          annotation (Placement(transformation(extent={{282,164},{302,184}})));
        Buildings.Controls.OBC.CDL.Logical.And and1
          annotation (Placement(transformation(extent={{54,132},{74,152}})));
        Buildings.Controls.OBC.CDL.Continuous.Greater cooOAChk(h=3)
          annotation (Placement(transformation(extent={{26,102},{46,122}})));
        Modelica.Blocks.Sources.RealExpression cooMinOATem(y=273.15 + 24)
        annotation (Placement(transformation(extent={{0,88},{20,108}})));
        Buildings.Controls.OBC.CDL.Logical.Switch OASetpoint
          annotation (Placement(transformation(extent={{128,-202},{148,-182}})));
        Modelica.Blocks.Sources.RealExpression fanSetpointNonOccupied1(y=minOAHVACOn*
              fanOccSet) annotation (Placement(transformation(extent={{94,-212},{114,-192}})));
        Modelica.Blocks.Sources.RealExpression fanSetpointOccupied2(y=minOAHVACOff)
          annotation (Placement(transformation(extent={{94,-194},{114,-174}})));
        Buildings.Controls.OBC.CDL.Logical.Pre pre1
          annotation (Placement(transformation(extent={{50,-202},{70,-182}})));
        Buildings.Controls.OBC.CDL.Continuous.Max max1
          annotation (Placement(transformation(extent={{394,-146},{414,-126}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add1
          annotation (Placement(transformation(extent={{258,-196},{278,-176}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai1(k=0.1)
          annotation (Placement(transformation(extent={{220,-202},{240,-182}})));
        Buildings.Controls.OBC.CDL.Continuous.Feedback feedback1
          annotation (Placement(transformation(extent={{182,-202},{202,-182}})));
        Buildings.Controls.OBC.CDL.Continuous.Limiter lim(uMax=1, uMin=0)
          annotation (Placement(transformation(extent={{300,-196},{320,-176}})));
        Buildings.Utilities.IO.SignalExchange.Overwrite oveRBCCooOccSet(u(
            unit="K",
            min=273.15,
            max=313.15), description="Cooling setpoint override")
          "\"BOPTEST override for the RBC cooling setpoint, occupied\""
          annotation (Placement(transformation(extent={{-240,218},{-220,238}})));
        Buildings.Utilities.IO.SignalExchange.Overwrite oveRBCHeaSetOcc(u(
            unit="K",
            min=273.15,
            max=313.15), description="Heating setpoint override")
          "\"BOPTEST override for the RBC heating etpoint\"" annotation (
            Placement(transformation(extent={{-152,422},{-132,442}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add4
          annotation (Placement(transformation(extent={{-132,186},{-112,206}})));
        Modelica.Blocks.Sources.RealExpression hyst(y=-1.5)
                                                          annotation (Placement(
              transformation(extent={{-178,158},{-158,178}})));
        Modelica.Blocks.Sources.RealExpression heaSetpointOccupied(y=heaOccSet)
          annotation (Placement(transformation(extent={{-194,422},{-174,442}})));
        Buildings.Utilities.IO.SignalExchange.Overwrite oveRBCHeaSetNonOcc(u(
            unit="K",
            min=273.15,
            max=313.15), description="Heating setpoint override")
          "\"BOPTEST override for the RBC heating etpoint\"" annotation (
            Placement(transformation(extent={{-156,364},{-136,384}})));
        Modelica.Blocks.Sources.RealExpression heaSetpointNonOccupied(y=heaNonOccSet)
          annotation (Placement(transformation(extent={{-194,364},{-174,384}})));
        Buildings.Utilities.IO.SignalExchange.Overwrite oveRBCCooNonOccSet(u(
            unit="K",
            min=273.15,
            max=313.15), description="Cooling setpoint override")
          "\"BOPTEST override for the RBC cooling setpoint, non occupied\""
          annotation (Placement(transformation(extent={{-248,174},{-228,194}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add3
          annotation (Placement(transformation(extent={{-96,358},{-76,378}})));
        Modelica.Blocks.Sources.RealExpression heaSetpointNonOccupied1(y=-
              heaNonOccSet)
          annotation (Placement(transformation(extent={{-134,334},{-114,354}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add5
          annotation (Placement(transformation(extent={{-24,246},{-4,266}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add6
          annotation (Placement(transformation(extent={{-24,278},{-4,298}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add7
          annotation (Placement(transformation(extent={{-96,416},{-76,436}})));
        Modelica.Blocks.Sources.RealExpression heaSetpointOccupied2(y=-heaOccSet)
          annotation (Placement(transformation(extent={{-134,392},{-114,412}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai2(k=-1)
          annotation (Placement(transformation(extent={{-64,416},{-44,436}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai3(k=-1)
          annotation (Placement(transformation(extent={{-64,358},{-44,378}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add8
          annotation (Placement(transformation(extent={{-22,-136},{-2,-116}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add9
          annotation (Placement(transformation(extent={{-22,-168},{-2,-148}})));
        Modelica.Blocks.Sources.RealExpression cooSetpointOccupied2(y=-
              cooOccSet) annotation (Placement(transformation(extent={{-200,-58},
                  {-180,-38}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add10
          annotation (Placement(transformation(extent={{-160,-52},{-140,-32}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai4(k=-1)
          annotation (Placement(transformation(extent={{-128,-52},{-108,-32}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add11
          annotation (Placement(transformation(extent={{-24,-90},{-4,-70}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add12
          annotation (Placement(transformation(extent={{-26,-58},{-6,-38}})));
        Buildings.Controls.OBC.CDL.Continuous.Gain gai5(k=-1)
          annotation (Placement(transformation(extent={{-182,-94},{-162,-74}})));
        Buildings.Controls.OBC.CDL.Continuous.Add add13
          annotation (Placement(transformation(extent={{-214,-94},{-194,-74}})));
        Modelica.Blocks.Sources.RealExpression cooSetpointNonOccupied1(y=-
              cooNonOccSet) annotation (Placement(transformation(extent={{-254,
                  -100},{-234,-80}})));
      equation
        //Setpoints - General//


        //connect(boo1.y, timerShortCycling.u)
        //  annotation (Line(points={{-59,14},{30,14}}, color={255,0,255}));
        connect(occStop.y, stoOccGre.u2)
          annotation (Line(points={{-561,202},{-520,202}},   color={0,0,127}));
        connect(occStopSat.y, stoOccSatGre.u2)
          annotation (Line(points={{-561,172},{-520,172}},   color={0,0,127}));
        connect(stoOccGre.y, not1.u) annotation (Line(points={{-496,210},{-492,210}},
                        color={255,0,255}));
        connect(stoOccSatGre.y, not2.u) annotation (Line(points={{-496,180},{-492,180}},
                             color={255,0,255}));
        connect(staOccGre.y, houOccWeekdays.u1) annotation (Line(points={{-470,238},{-454,
                238}},              color={255,0,255}));
        connect(not1.y, houOccWeekdays.u2) annotation (Line(points={{-468,210},{-466,210},
                {-466,230},{-454,230}},               color={255,0,255}));
        connect(stoOccGre.u1, houIn.y) annotation (Line(points={{-520,210},{-532,210},
                {-532,266},{-561,266}},              color={0,0,127}));
        connect(stoOccSatGre.u1, houIn.y) annotation (Line(points={{-520,180},{-532,180},
                {-532,266},{-561,266}},               color={0,0,127}));
        connect(occStart.y, staOccGre.u2)
          annotation (Line(points={{-561,230},{-494,230}},   color={0,0,127}));
        connect(staOccGre.u1, houIn.y) annotation (Line(points={{-494,238},{-532,238},
                {-532,266},{-561,266}},              color={0,0,127}));
        connect(houOccSaturday.u1, houOccWeekdays.u1) annotation (Line(points={{-456,210},
                {-460,210},{-460,238},{-454,238}},                color={255,0,
                255}));
        connect(not2.y, houOccSaturday.u2) annotation (Line(points={{-468,180},{-464,180},
                {-464,202},{-456,202}},               color={255,0,255}));
        connect(weekend.u1, dayIn.y) annotation (Line(points={{-520,150},{-542,150},{-542,
                252},{-561,252}},               color={0,0,127}));
        connect(sunday.u1, dayIn.y) annotation (Line(points={{-520,122},{-542,122},{-542,
                252},{-561,252}},               color={0,0,127}));
        connect(weekend.u2, fri.y)
          annotation (Line(points={{-520,142},{-561,142}},   color={0,0,127}));
        connect(sunday.u2, sat.y)
          annotation (Line(points={{-520,114},{-561,114}},   color={0,0,127}));
        connect(weekend.y, saturday.u1) annotation (Line(points={{-496,150},{-462,150}},
                             color={255,0,255}));
        connect(sunday.y, not3.u) annotation (Line(points={{-496,122},{-492,122}},
                        color={255,0,255}));
        connect(not3.y, saturday.u2) annotation (Line(points={{-468,122},{-464,122},{-464,
                142},{-462,142}},               color={255,0,255}));
        connect(saturday.y, not4.u) annotation (Line(points={{-438,150},{-428,150}},
                        color={255,0,255}));
        connect(not4.y, weekdays.u1) annotation (Line(points={{-404,150},{-404,130},{-402,
                130}},              color={255,0,255}));
        connect(weekdays.u2, saturday.u2) annotation (Line(points={{-402,122},{-464,122},
                {-464,142},{-462,142}},               color={255,0,255}));
        connect(houOccSaturday.y, occSaturday.u1) annotation (Line(points={{-432,210},
                {-372,210}},             color={255,0,255}));
        connect(houOccWeekdays.y, occWeekday.u1) annotation (Line(points={{-430,238},{
                -372,238}},         color={255,0,255}));
        connect(occWeekday.u2, weekdays.y) annotation (Line(points={{-372,230},{-376,230},
                {-376,130},{-378,130}},               color={255,0,255}));
        connect(occSaturday.u2, not4.u) annotation (Line(points={{-372,202},{-432,202},
                {-432,150},{-428,150}},              color={255,0,255}));
        connect(occWeekday.y, or2.u1) annotation (Line(points={{-348,238},{-346,238},{
                -346,218},{-342,218}},               color={255,0,255}));
        connect(occSaturday.y, or2.u2) annotation (Line(points={{-348,210},{-342,210}},
                             color={255,0,255}));
        connect(or2.y, cooSetpoint.u2) annotation (Line(points={{-318,218},{-286,
                218},{-286,202},{-186,202}},         color={255,0,255}));
        connect(or2.y, fanSetpoint.u2) annotation (Line(points={{-318,218},{
                -308,218},{-308,128},{-252,128}},    color={255,0,255}));
        connect(fanSetpoint.u1, fanSetpointOccupied.y)
          annotation (Line(points={{-252,136},{-256,136},{-261,136}},
                                                             color={0,0,127}));
        connect(fanSetpoint.u3, fanSetpointNonOccupied.y)
          annotation (Line(points={{-252,120},{-256,120},{-261,120}},
                                                             color={0,0,127}));
        connect(heaSetTab.y, heaSetLinear.u1) annotation (Line(points={{35,288},{46,288},
                {46,280},{54,280}},             color={0,0,127}));
        connect(heaSetTabNonOcc.y, heaSetLinear.u3) annotation (Line(points={{35,256},
                {46,256},{46,264},{54,264}},          color={0,0,127}));
        connect(heaSetLinear.u2, fanSetpoint.u2) annotation (Line(points={{54,272},
                {-308,272},{-308,128},{-252,128}},    color={255,0,255}));
        connect(neeCool.u1, senTemRet) annotation (Line(points={{6,142},{-46,142},{-46,
                288},{-640,288}},         color={0,0,127}));
        connect(risEdgCC.y, lat.clr) annotation (Line(points={{112,52},{112,76},
              {116,76}},           color={255,0,255}));
        connect(lat.y, and2.u2) annotation (Line(points={{140,82},{144,82},{144,134},{
                150,134}},   color={255,0,255}));
        connect(and2.y, ccTurnedOff1.u) annotation (Line(points={{174,142},{178,142},{
                178,118},{174,118}},
                                 color={255,0,255}));
        connect(ccTurnedOff.y, risEdgCC.u)
          annotation (Line(points={{82,52},{88,52}},        color={255,0,255}));
        connect(tim.passed, lat.u)
          annotation (Line(points={{106,82},{116,82}},     color={255,0,255}));
        connect(damSetTabHea.y, damSetLinear.u1) annotation (Line(points={{111,-48},{120,
                -48},{120,-56},{128,-56}},        color={0,0,127}));
        connect(damSetTabHeaNonOcc.y, damSetLinear.u3) annotation (Line(points={{111,-80},
                {119.5,-80},{119.5,-72},{128,-72}},    color={0,0,127}));
        connect(damSetTabCoo.y, damSetLinear2.u1) annotation (Line(points={{113,-126},
                {122,-126},{122,-136},{128,-136}}, color={0,0,127}));
        connect(damSetTabCooNonOcc.y, damSetLinear2.u3) annotation (Line(points={{113,
                -158},{121.5,-158},{121.5,-152},{128,-152}}, color={0,0,127}));
        connect(damSetLinear.u2, fanSetpoint.u2) annotation (Line(points={{128,-64},
                {-308,-64},{-308,128},{-252,128}},   color={255,0,255}));
        connect(damSetLinear2.u2, fanSetpoint.u2) annotation (Line(points={{128,
                -144},{-308,-144},{-308,128},{-252,128}},
                                                      color={255,0,255}));
        connect(ecoHea.u1, senTemRet) annotation (Line(points={{14,-102},{-46,-102},{-46,
                288},{-640,288}},         color={0,0,127}));
        connect(ecoHea.u2, senTemOut)
          annotation (Line(points={{14,-110},{-60,-110},{-60,322},{-642,322}},
                                                             color={0,0,127}));
        connect(damSetLinear.y, damSetLinear1.u1) annotation (Line(points={{152,-64},{
                154,-64},{154,-94},{160,-94}},     color={0,0,127}));
        connect(damSetLinear2.y, damSetLinear1.u3) annotation (Line(points={{152,-144},
                {156,-144},{156,-110},{160,-110}}, color={0,0,127}));
        connect(or1.u2, and2.y) annotation (Line(points={{322,154},{240,154},{240,142},
                {174,142}},color={255,0,255}));
        connect(or1.y, fanSetLinear.u2) annotation (Line(points={{346,162},{354,162},{
                354,118},{392,118}},    color={255,0,255}));
        connect(fanSetpoint.y, fanSetLinear.u3) annotation (Line(points={{-228,
                128},{-196,128},{-196,-24},{258,-24},{258,110},{392,110}},
                                                                        color={0,0,127}));
        connect(fanSetpointOccupied1.y, fanSetLinear.u1) annotation (Line(points={{383,126},
                {392,126}},                                  color={0,0,127}));
        connect(booToRea.u, and2.y) annotation (Line(points={{182,4},{174,4},{174,90},
                {190,90},{190,142},{174,142}}, color={255,0,255}));
        connect(booToRea.y, outCCSet) annotation (Line(points={{206,4},{592,4},{592,193},
                {679,193}},        color={0,0,127}));
        connect(fanSetLinear.y, feedback.u1)
          annotation (Line(points={{416,118},{438,118}},   color={0,0,127}));
        connect(feedback.y, gai.u)
          annotation (Line(points={{462,118},{476,118}},   color={0,0,127}));
        connect(gai.y, add2.u2)
          annotation (Line(points={{500,118},{514,118}},   color={0,0,127}));
        connect(add2.u1, feedback.u1) annotation (Line(points={{514,130},{500,130},{500,
                144},{430,144},{430,118},{438,118}},         color={0,0,127}));
        connect(add2.y, outFanSet) annotation (Line(points={{538,124},{578,124},{578,251},
                {679,251}},        color={0,0,127}));
        connect(feedback.u2, senFanVFR) annotation (Line(points={{450,106},{450,-240},
                {-632,-240}}, color={0,0,127}));
        connect(ccTurnedOff1.y, pre.u)
          annotation (Line(points={{150,118},{134,118}}, color={255,0,255}));
        connect(pre.y, tim.u) annotation (Line(points={{110,118},{72,118},{72,
                90},{82,90}}, color={255,0,255}));
        connect(or1.u1, greThr.y) annotation (Line(points={{322,162},{314,162},
                {314,174},{304,174}}, color={255,0,255}));
        connect(greThr.u, heaSetLinear.y) annotation (Line(points={{280,174},{
                232,174},{232,272},{78,272}}, color={0,0,127}));
        connect(outHeaSet, heaSetLinear.y) annotation (Line(points={{679,297},{
                232,297},{232,272},{78,272}}, color={0,0,127}));
      connect(neeCool.y, and1.u1)
        annotation (Line(points={{30,142},{52,142}}, color={255,0,255}));
      connect(and1.y, and2.u1)
        annotation (Line(points={{76,142},{150,142}}, color={255,0,255}));
      connect(ccTurnedOff.u, and2.u1) annotation (Line(points={{58,52},{56,52},{
              56,82},{68,82},{68,130},{80,130},{80,142},{150,142}}, color={255,0,
              255}));
      connect(cooMinOATem.y, cooOAChk.u2) annotation (Line(points={{21,98},{22,98},
              {22,104},{24,104}}, color={0,0,127}));
      connect(cooOAChk.u1, senTemOut) annotation (Line(points={{24,112},{-60,112},
              {-60,322},{-642,322}}, color={0,0,127}));
      connect(cooOAChk.y, and1.u2) annotation (Line(points={{48,112},{52,112},{52,
              134},{52,134}}, color={255,0,255}));
        connect(ecoHea.y, damSetLinear1.u2)
          annotation (Line(points={{38,-102},{160,-102}}, color={255,0,255}));
        connect(OASetpoint.u1, fanSetpointOccupied2.y)
          annotation (Line(points={{126,-184},{115,-184}}, color={0,0,127}));
        connect(OASetpoint.u3, fanSetpointNonOccupied1.y) annotation (Line(points={{126,
                -200},{120,-200},{120,-202},{115,-202}}, color={0,0,127}));
      connect(pre1.y, OASetpoint.u2)
        annotation (Line(points={{72,-192},{126,-192}}, color={255,0,255}));
      connect(pre1.u, fanSetLinear.u2) annotation (Line(points={{48,-192},{46,-192},
              {46,-178},{354,-178},{354,118},{392,118}}, color={255,0,255}));
      connect(max1.u1, damSetLinear1.y) annotation (Line(points={{392,-130},{240,-130},
                {240,-102},{184,-102}},     color={0,0,127}));
      connect(max1.y, outDamSet) annotation (Line(points={{416,-136},{618,-136},{618,143},
                {681,143}},         color={0,0,127}));
        connect(feedback1.y, gai1.u)
          annotation (Line(points={{204,-192},{218,-192}}, color={0,0,127}));
        connect(gai1.y, add1.u2)
          annotation (Line(points={{242,-192},{256,-192}}, color={0,0,127}));
        connect(OASetpoint.y, feedback1.u1)
          annotation (Line(points={{150,-192},{180,-192}}, color={0,0,127}));
        connect(add1.u1, feedback1.u1) annotation (Line(points={{256,-180},{164,-180},
                {164,-192},{180,-192}}, color={0,0,127}));
        connect(feedback1.u2, senDamVFR) annotation (Line(points={{192,-204},{-220,-204},
                {-220,-192},{-632,-192}}, color={0,0,127}));
        connect(add1.y, lim.u)
          annotation (Line(points={{280,-186},{298,-186}}, color={0,0,127}));
        connect(lim.y, max1.u2) annotation (Line(points={{322,-186},{358,-186},{358,-142},
                {392,-142}}, color={0,0,127}));
        connect(add4.y, neeCool.u2) annotation (Line(points={{-110,196},{-98,196},
                {-98,134},{6,134}}, color={0,0,127}));
        connect(add4.u2, hyst.y) annotation (Line(points={{-134,190},{-150,190},
                {-150,168},{-157,168}}, color={0,0,127}));


        connect(cooSetpoint.y, add4.u1)
          annotation (Line(points={{-162,202},{-134,202}}, color={0,0,127}));
        connect(cooSetpoint.u3, oveRBCCooNonOccSet.y) annotation (Line(points={{-186,
                194},{-212,194},{-212,184},{-227,184}},      color={0,0,127}));
        connect(coolingSetpointNonOccupied.y, oveRBCCooNonOccSet.u) annotation (
           Line(points={{-275,184},{-250,184}},                       color={0,0,
                127}));
        connect(cooSetpoint.u1, oveRBCCooOccSet.y) annotation (Line(points={{-186,
                210},{-200,210},{-200,228},{-219,228}}, color={0,0,127}));
        connect(coolingSetpointOccupied.y, oveRBCCooOccSet.u) annotation (Line(
              points={{-273,228},{-242,228}},                       color={0,0,127}));
        connect(heaSetpointOccupied.y, oveRBCHeaSetOcc.u)
          annotation (Line(points={{-173,432},{-154,432}}, color={0,0,127}));
        connect(heaSetpointNonOccupied.y, oveRBCHeaSetNonOcc.u)
          annotation (Line(points={{-173,374},{-158,374}}, color={0,0,127}));
        connect(oveRBCHeaSetNonOcc.y, add3.u1)
          annotation (Line(points={{-135,374},{-98,374}}, color={0,0,127}));
        connect(heaSetpointNonOccupied1.y, add3.u2) annotation (Line(points={{-113,344},
                {-104,344},{-104,362},{-98,362}}, color={0,0,127}));
        connect(heaSetTabNonOcc.u, add5.y)
          annotation (Line(points={{12,256},{-2,256}}, color={0,0,127}));
        connect(add5.u2, senTemRet) annotation (Line(points={{-26,250},{-46,250},{-46,
                288},{-640,288}}, color={0,0,127}));
        connect(heaSetTab.u, add6.y)
          annotation (Line(points={{12,288},{-2,288}}, color={0,0,127}));
        connect(add6.u2, senTemRet) annotation (Line(points={{-26,282},{-46,282},{-46,
                288},{-640,288}}, color={0,0,127}));
        connect(oveRBCHeaSetOcc.y, add7.u1)
          annotation (Line(points={{-131,432},{-98,432}}, color={0,0,127}));
        connect(add7.u2, heaSetpointOccupied2.y) annotation (Line(points={{-98,420},{-106,
                420},{-106,402},{-113,402}}, color={0,0,127}));
        connect(add7.y, gai2.u)
          annotation (Line(points={{-74,426},{-66,426}}, color={0,0,127}));
        connect(add3.y, gai3.u)
          annotation (Line(points={{-74,368},{-66,368}}, color={0,0,127}));
        connect(gai2.y, add6.u1) annotation (Line(points={{-42,426},{-34,426},{
                -34,294},{-26,294}}, color={0,0,127}));
        connect(gai3.y, add5.u1) annotation (Line(points={{-42,368},{-38,368},{
                -38,262},{-26,262}}, color={0,0,127}));
        connect(add8.y, damSetTabCoo.u)
          annotation (Line(points={{0,-126},{90,-126}}, color={0,0,127}));
        connect(add9.y, damSetTabCooNonOcc.u)
          annotation (Line(points={{0,-158},{90,-158}}, color={0,0,127}));
        connect(add8.u1, add6.u1) annotation (Line(points={{-24,-120},{-34,-120},
                {-34,294},{-26,294}}, color={0,0,127}));
        connect(add9.u1, add5.u1) annotation (Line(points={{-24,-152},{-38,-152},
                {-38,262},{-26,262}}, color={0,0,127}));
        connect(add10.u2, cooSetpointOccupied2.y)
          annotation (Line(points={{-162,-48},{-179,-48}}, color={0,0,127}));
        connect(add10.y, gai4.u)
          annotation (Line(points={{-138,-42},{-130,-42}}, color={0,0,127}));
        connect(add10.u1, oveRBCCooOccSet.y) annotation (Line(points={{-162,-36},
                {-190,-36},{-190,210},{-200,210},{-200,228},{-219,228}}, color=
                {0,0,127}));
        connect(add12.y, damSetTabHea.u)
          annotation (Line(points={{-4,-48},{88,-48}}, color={0,0,127}));
        connect(add11.y, damSetTabHeaNonOcc.u)
          annotation (Line(points={{-2,-80},{88,-80}}, color={0,0,127}));
        connect(add11.u2, senTemRet) annotation (Line(points={{-26,-86},{-46,
                -86},{-46,288},{-640,288}}, color={0,0,127}));
        connect(add12.u2, senTemRet) annotation (Line(points={{-28,-54},{-46,
                -54},{-46,288},{-640,288}}, color={0,0,127}));
        connect(add9.u2, senTemRet) annotation (Line(points={{-24,-164},{-46,
                -164},{-46,288},{-640,288}}, color={0,0,127}));
        connect(add8.u2, senTemRet) annotation (Line(points={{-24,-132},{-46,
                -132},{-46,288},{-640,288}}, color={0,0,127}));
        connect(add12.u1, gai4.y)
          annotation (Line(points={{-28,-42},{-106,-42}}, color={0,0,127}));
        connect(add13.y, gai5.u)
          annotation (Line(points={{-192,-84},{-184,-84}}, color={0,0,127}));
        connect(add13.u2, cooSetpointNonOccupied1.y)
          annotation (Line(points={{-216,-90},{-233,-90}}, color={0,0,127}));
        connect(gai5.y, add11.u1) annotation (Line(points={{-160,-84},{-66,-84},
                {-66,-74},{-26,-74}}, color={0,0,127}));
        connect(add13.u1, oveRBCCooNonOccSet.y) annotation (Line(points={{-216,
                -78},{-222,-78},{-222,184},{-227,184}}, color={0,0,127}));
        annotation (Icon(coordinateSystem(extent={{-600,-300},{640,360}}),
                         graphics={Rectangle(extent={{-600,364},{642,-300}},
                  lineColor={28,108,200})}),Inline=true,GenerateEvents=true,
          Diagram(coordinateSystem(extent={{-600,-300},{640,360}}),
                  graphics={
              Rectangle(extent={{2,358},{212,182}},      lineColor={28,108,200}),
              Text(
                extent={{12,230},{112,184}},
                lineColor={28,108,200},
                textString="Heating"),
              Text(
                extent={{18,36},{118,-10}},
                lineColor={28,108,200},
                textString="Cooling"),
              Rectangle(extent={{2,170},{212,-16}},      lineColor={28,108,200}),
              Text(
                extent={{286,98},{386,52}},
                lineColor={28,108,200},
                textString="CV Fan controls"),
              Rectangle(extent={{274,194},{566,44}},    lineColor={28,108,200}),
              Text(
                extent={{-214,126},{-110,98}},
                lineColor={28,108,200},
                textString="Schedule"),
              Rectangle(extent={{-590,276},{-108,96}},    lineColor={28,108,200}),
              Text(
                extent={{8,-200},{108,-246}},
                lineColor={28,108,200},
                textString="Economizer"),
              Rectangle(extent={{4,-30},{212,-236}},     lineColor={28,108,200})}),
          experiment(
            StopTime=31449600,
            Interval=360,
            __Dymola_Algorithm="Dassl"));
      end System3RBControls;

      //HVAC Components//

      Buildings.Fluid.Actuators.Dampers.MixingBox mixDam(
      use_inputFilter=false,
      redeclare final package Medium = Medium,
      from_dp=true,
      allowFlowReversal=true,
      mOut_flow_nominal=mass_flow_nominal,
      mRec_flow_nominal=mass_flow_nominal,
      mExh_flow_nominal=mass_flow_nominal,
      dpDamExh_nominal=dp_nominal,
      dpDamOut_nominal=dp_nominal,
      dpDamRec_nominal=dp_nominal) "Economizer: mixing box with damper"
      annotation (Placement(transformation(extent={{-274,-250},{-212,-188}})));

      Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.SingleSpeed sinSpeDX(
        redeclare final package Medium = Medium,
        dxCoo(wetCoi(TADP(start=280.0, nominal = 280.0, min = 1.0), appDewPt(TADP(start=280.0, min=0.0)))),
        datCoi(
          nSta=1,
          minSpeRat=0.2,
          sta={
              Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.Stage(
              spe=1800/60,
              nomVal=
                Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.NominalValues(
                Q_flow_nominal=CCNomPow,
                COP_nominal=3.67,
                SHR_nominal=0.79,
                m_flow_nominal=0.53,
                TEvaIn_nominal=273.15 + 17.74,
                TConIn_nominal=308.15,
                phiIn_nominal=0.48,
                tWet=1200),
              perCur=
                Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.PerformanceCurve(
                capFunT={0.9712123,-0.015275502,0.0014434524,-0.00039321,-0.0000068364,
                  -0.0002905956},
                capFunFF={1,0,0},
                EIRFunT={0.28687133,0.023902164,-0.000810648,0.013458546,0.0003389364,
                  -0.0004870044},
                EIRFunFF={1,0,0},
                TConInMin=291.15,
                TConInMax=319.26111,
                TEvaInMin=285.92778,
                TEvaInMax=297.03889,
                ffMin=0.5,
                ffMax=1.5))}),
        allowFlowReversal=true,
        m_flow_small=1E-3,
        from_dp=false,
        dp_nominal=dp_nominal,
        T_start=288.65) "Single Speed DX cooling coil"
        annotation (Placement(transformation(extent={{-98,-114},{-40,-56}})));

      Buildings.Fluid.HeatExchangers.HeaterCooler_u hea(
        redeclare final package Medium = Medium,
        allowFlowReversal=true,
        m_flow_nominal=mass_flow_nominal,
        dp_nominal=dp_nominal,
        T_start=288.65,
        Q_flow_nominal=heaNomPow)
        annotation (Placement(transformation(extent={{80,-106},{118,-64}})));

      // TO DO: replace fan characteristics values by variable parameters//

      Buildings.Fluid.Movers.FlowControlled_m_flow fan(
        redeclare final package Medium = Medium,
        T_start=288.65,
        allowFlowReversal=true,
        m_flow_nominal=mass_flow_nominal,
        redeclare parameter Buildings.Fluid.Movers.Data.Generic per(
          pressure(V_flow={0.439,0.44}, dp={623,622}),
          use_powerCharacteristic=false,
          hydraulicEfficiency(V_flow={0.44}, eta={0.65}),
          motorEfficiency(V_flow={0.44}, eta={0.825})),
        dp_nominal=622)
        annotation (Placement(transformation(extent={{240,-106},{282,-64}})));

      // Ports //

     Modelica.Blocks.Interfaces.RealInput day annotation (Placement(transformation(
              extent={{-440,90},{-400,130}}), iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=0,
            origin={-396,-140})));
      Modelica.Blocks.Interfaces.RealInput hour annotation (Placement(
            transformation(extent={{-440,130},{-400,170}}), iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=0,
            origin={-396,-214})));

      Modelica.Fluid.Interfaces.FluidPort_a OAInlPor(redeclare final package
          Medium =
          Medium) "Port to the outside air source" annotation (Placement(
          transformation(extent={{-410,-210},{-390,-190}}),
                                                        iconTransformation(
            extent={{-420,280},{-400,300}})));

      Modelica.Fluid.Interfaces.FluidPort_b OAOutPor(redeclare final package
          Medium =
          Medium) "Port to the outside air sink" annotation (Placement(
          transformation(extent={{-410,-248},{-390,-228}}),
                                                         iconTransformation(
            extent={{-420,18},{-400,38}})));

      Modelica.Fluid.Interfaces.FluidPort_b zonSupPort(redeclare final package
          Medium =
          Medium) "Outlet to the zone air supply" annotation (Placement(
          transformation(extent={{436,-168},{456,-148}}),
                                                      iconTransformation(extent=
             {{600,280},{620,300}})));

      Modelica.Fluid.Interfaces.FluidPort_a zonRetPor(redeclare final package
          Medium =
          Medium) "Inlet for the zone return air" annotation (Placement(
          transformation(extent={{442,-248},{462,-228}}),
                                                       iconTransformation(
            extent={{602,20},{622,40}})));

     //Controls//

      Buildings.Fluid.Sensors.VolumeFlowRate volSenSup(
        redeclare final package Medium = Medium,
        m_flow_nominal=0.5,
        T_start=288.65) "Volumetric flow rate sensor, supply side"
        annotation (Placement(transformation(extent={{346,-94},{366,-74}})));

      Buildings.Fluid.Sensors.VolumeFlowRate volSenOA(
        redeclare final package Medium = Medium,
        m_flow_nominal=0.5,
        T_start=288.65) "Volumetric flow rate sensor, outside air"
        annotation (Placement(transformation(extent={{-316,-210},{-296,-190}})));

      //Output //

      Modelica.Blocks.Interfaces.RealOutput fanPowDem "Fan power demand"
       annotation (Placement(transformation(extent={{442,-28},{486,16}}),
          iconTransformation(
          extent={{-22,-22},{22,22}},
          rotation=270,
          origin={236,-284})));

      Modelica.Blocks.Interfaces.RealOutput heaPowDem
      "Heating coil power demand" annotation (Placement(transformation(extent={{442,38},
                {486,82}}),         iconTransformation(
          extent={{-22,-22},{22,22}},
          rotation=270,
          origin={332,-284})));

      Modelica.Blocks.Interfaces.RealOutput cooPowDem
      "Cooling coil power demand" annotation (Placement(transformation(extent={{442,100},
                {486,144}}),        iconTransformation(
          extent={{-22,-22},{22,22}},
          rotation=270,
          origin={438,-284})));

      // Signal Exchange blocks - BOPTEST //

      Buildings.Utilities.IO.SignalExchange.Overwrite oveHCSet(u(
          unit="1",
          min=0,
          max=1), description="Heating Coil setpoint override")
        "\"BOPTEST override for the HC control\""
        annotation (Placement(transformation(extent={{-226,42},{-206,62}})));
      Buildings.Utilities.IO.SignalExchange.Overwrite oveCCSet(u(
          unit="1",
          min=0,
          max=1), description="Cooling Coil setpoint override")
        "\"BOPTEST override for the CC control"
        annotation (Placement(transformation(extent={{-226,10},{-206,30}})));
      Buildings.Utilities.IO.SignalExchange.Overwrite oveFanSet(u(
          unit="1",
          min=0,
          max=2), description="Fan setpoint override")
        "\"BOPTEST override for the fan control"
        annotation (Placement(transformation(extent={{-226,-26},{-206,-6}})));
      Buildings.Utilities.IO.SignalExchange.Overwrite oveDamSet(u(
          unit="1",
          min=0,
          max=2), description="Damper setpoint override")
        "\"BOPTEST override for the mixing box control"
        annotation (Placement(transformation(extent={{-226,-62},{-206,-42}})));

      Modelica.Blocks.Interfaces.RealInput senTemOA annotation (Placement(
            transformation(extent={{-434,-96},{-394,-56}}), iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=0,
            origin={-398,-52})));
      Modelica.Blocks.Math.RealToBoolean reaToBooCC
        annotation (Placement(transformation(extent={{-186,10},{-166,30}})));

    Buildings.Utilities.IO.SignalExchange.Read senTemRoo(y(min=260.0, max=310.0, unit="K"), description=
          "Room return temperature", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature)
      annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={-406,6})));
      Modelica.Blocks.Interfaces.RealInput temSenRet
                                                    annotation (Placement(
            transformation(extent={{-434,-138},{-394,-98}}),iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=180,
            origin={578,358})));
      Buildings.Fluid.Sensors.RelativeHumidityTwoPort senRelHum(redeclare
          final package Medium =                                                               Medium,
        allowFlowReversal=true,
          m_flow_nominal=0.5,
        m_flow_small=0.0001)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}},
            rotation=180,
            origin={90,-238})));
    Buildings.Utilities.IO.SignalExchange.Read senRelHumOut(description="Room HR",
          KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.RelativeHumidity, y(min=0.0, max=1.0, unit="1"))
        annotation (Placement(transformation(
            extent={{-10,-10},{10,10}},
            rotation=180,
            origin={38,-132})));
    Buildings.Utilities.IO.SignalExchange.Read senVolOA(description="OA VFR",
          KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None, y(min=0.0, max=2.0, unit="m3/s"))
        "\"OA volumetric flowrate sensor\"" annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=180,
            origin={-336,-174})));
    Buildings.Utilities.IO.SignalExchange.Read senVolSup(description="Supply VFR",
          KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None, y(min=0.0, max=2.0, unit="m3/s"))
        "\"Supply volumetric flowrate sensor\"" annotation (Placement(
            transformation(
            extent={{-10,-10},{10,10}},
            rotation=180,
            origin={-274,-156})));
      Buildings.Fluid.Sensors.TemperatureTwoPort senTSup(
        redeclare final package Medium = Medium,
        allowFlowReversal=true,
        m_flow_nominal=0.5,
        T_start=288.75) "\"Supply air temperature\""
        annotation (Placement(transformation(extent={{384,-94},{404,-74}})));
    Buildings.Utilities.IO.SignalExchange.Read senTemSup(
        y(min=275.0,
          max=340.0,
          unit="K"),
        description="Supply air temperature",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
        "\"Supply air temperature\"" annotation (Placement(transformation(
            extent={{-10,-10},{10,10}},
            rotation=0,
            origin={-406,40})));
      System3RBControls controls(
        day=day,
        hou=hour,
        minOACCOpeTemp=280)                                    "CAV controller"
      annotation (Placement(transformation(extent={{-316,4},{-290,52}})));
    equation

    connect(mixDam.port_Sup, sinSpeDX.port_a) annotation (Line(points={{-212,-200.4},
              {-200,-200.4},{-200,-85},{-98,-85}},
                                               color={0,127,255}));
      connect(sinSpeDX.port_b, hea.port_a)
        annotation (Line(points={{-40,-85},{80,-85}},          color={0,127,255}));
      connect(hea.port_b, fan.port_a)
        annotation (Line(points={{118,-85},{240,-85}}, color={0,127,255}));
    connect(OAOutPor, mixDam.port_Exh) annotation (Line(points={{-400,-238},{-304,-238},
              {-304,-237.6},{-274,-237.6}},  color={0,127,255}));
    connect(fan.P, fanPowDem) annotation (Line(points={{284.1,-66.1},{284.1,-46},{284,
              -46},{284,-6},{464,-6}},      color={0,0,127}));
    connect(fanPowDem, fanPowDem)
      annotation (Line(points={{464,-6},{464,-6}},   color={0,0,127}));
    connect(hea.Q_flow, heaPowDem) annotation (Line(points={{119.9,-72.4},{136,-72.4},
              {136,60},{464,60}}, color={0,0,127}));
    connect(cooPowDem, sinSpeDX.P) annotation (Line(points={{464,122},{22,122},{22,-58.9},
              {-37.1,-58.9}},         color={0,0,127}));
      connect(fan.port_b, volSenSup.port_a) annotation (Line(points={{282,-85},{346,
              -85},{346,-84}}, color={0,127,255}));
      connect(OAInlPor, volSenOA.port_a)
        annotation (Line(points={{-400,-200},{-316,-200}}, color={0,127,255}));
      connect(volSenOA.port_b, mixDam.port_Out) annotation (Line(points={{-296,-200},
              {-290,-200},{-290,-200.4},{-274,-200.4}}, color={0,127,255}));
      connect(oveHCSet.y, hea.u) annotation (Line(points={{-205,52},{48,52},{48,-72.4},
              {76.2,-72.4}}, color={0,0,127}));
      connect(oveFanSet.y, fan.m_flow_in) annotation (Line(points={{-205,-16},{261,-16},
              {261,-59.8}}, color={0,0,127}));
      connect(oveDamSet.y, mixDam.y) annotation (Line(points={{-205,-52},{-198,-52},
              {-198,-68},{-243,-68},{-243,-181.8}}, color={0,0,127}));
      connect(oveCCSet.y, reaToBooCC.u)
        annotation (Line(points={{-205,20},{-188,20}}, color={0,0,127}));
      connect(reaToBooCC.y, sinSpeDX.on) annotation (Line(points={{-165,20},{-132,20},
              {-132,-61.8},{-100.9,-61.8}}, color={255,0,255}));
      connect(temSenRet, senTemRoo.u) annotation (Line(points={{-414,-118},{-418,
              -118},{-418,6},{-418,6}}, color={0,0,127}));
      connect(senRelHum.phi, senRelHumOut.u) annotation (Line(points={{89.9,-249},{70.05,
              -249},{70.05,-132},{50,-132}},        color={0,0,127}));
      connect(senRelHum.port_b, mixDam.port_Ret) annotation (Line(points={{80,
              -238},{-66,-238},{-66,-237.6},{-212,-237.6}}, color={0,127,255}));
      connect(senRelHum.port_a, zonRetPor) annotation (Line(points={{100,-238},
              {276,-238},{276,-238},{452,-238}}, color={0,127,255}));
      connect(volSenOA.V_flow, senVolOA.u) annotation (Line(points={{-306,-189},
              {-306,-174},{-324,-174}}, color={0,0,127}));
      connect(volSenSup.V_flow, senVolSup.u) annotation (Line(points={{356,-73},
              {356,-64},{312,-64},{312,-156},{-262,-156}}, color={0,0,127}));
      connect(sinSpeDX.TConIn, senTemOA) annotation (Line(points={{-100.9,-76.3},{-382,
              -76.3},{-382,-76},{-414,-76}}, color={0,0,127}));
      connect(zonSupPort, senTSup.port_b) annotation (Line(points={{446,-158},{426,-158},
              {426,-84},{404,-84}}, color={0,127,255}));
      connect(volSenSup.port_b, senTSup.port_a)
        annotation (Line(points={{366,-84},{384,-84}}, color={0,127,255}));
      connect(controls.outHeaSet, oveHCSet.u) annotation (Line(points={{-288.469,
              33.8909},{-259.235,33.8909},{-259.235,52},{-228,52}},
                                                           color={0,0,127}));
      connect(controls.outCCSet, oveCCSet.u) annotation (Line(points={{-288.469,
              30.4},{-258.235,30.4},{-258.235,20},{-228,20}},
                                                        color={0,0,127}));
      connect(controls.outFanSet, oveFanSet.u) annotation (Line(points={{-288.469,
              26.9091},{-259.235,26.9091},{-259.235,-16},{-228,-16}},
                                                             color={0,0,127}));
      connect(controls.outDamSet, oveDamSet.u) annotation (Line(points={{-288.469,
              22.8364},{-288.469,-34.5818},{-228,-34.5818},{-228,-52}},
                                                               color={0,0,127}));
      connect(controls.senTemOut, senTemOA) annotation (Line(points={{-316.713,48.0727},
              {-316.713,48},{-346,48},{-346,-14},{-414,-14},{-414,-76}}, color={0,0,
              127}));
      connect(controls.senTemSup, senTemSup.y) annotation (Line(points={{-316.587,
              40.0727},{-316.587,41.0363},{-395,41.0363},{-395,40}},
                                                            color={0,0,127}));
      connect(controls.senTemRet, senTemRoo.y) annotation (Line(points={{-316.587,
              31.4909},{-355.293,31.4909},{-355.293,6},{-395,6}},
                                                         color={0,0,127}));
      connect(controls.senFanVFR, senVolSup.y) annotation (Line(points={{-316.629,
              22.4727},{-334,22.4727},{-334,-156},{-285,-156}},
                                                       color={0,0,127}));
      connect(controls.senDamVFR, senVolOA.y) annotation (Line(points={{-316.587,
              13.7455},{-344,13.7455},{-344,-106},{-366,-106},{-366,-174},{-347,
              -174}},
            color={0,0,127}));
      connect(controls.senHRRet, senRelHumOut.y) annotation (Line(points={{-316.629,
              5.89091},{-316.629,-132},{27,-132}}, color={0,0,127}));
      connect(senTemSup.u, senTSup.T) annotation (Line(points={{-418,40},{-426,40},{
              -426,80},{394,80},{394,-73}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-420,-260},
                {440,220}}),     graphics={
          Rectangle(
            extent={{-422,358},{598,-260}},
            lineColor={28,108,200},
            fillColor={170,213,255},
            fillPattern=FillPattern.Solid),
          Text(
            extent={{-232,364},{368,10}},
            lineColor={28,108,200},
            fillColor={170,213,255},
            fillPattern=FillPattern.None,
            textString="CAV"),
          Rectangle(
            extent={{486,-258},{162,-106}},
            lineColor={28,108,200},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid),
          Text(
            extent={{38,-110},{588,-194}},
            lineColor={28,108,200},
            fillColor={175,175,175},
            fillPattern=FillPattern.None,
            textString="Power"),
          Text(
            extent={{66,-196},{596,-244}},
            lineColor={28,108,200},
            fillColor={175,175,175},
            fillPattern=FillPattern.None,
            textString="Fan  HC  CC")}),                             Diagram(
          coordinateSystem(preserveAspectRatio=false, extent={{-420,-260},{440,220}})),
      uses(Buildings(version="8.0.0")),
        Documentation(revisions="<html>
<ul>
<li>November 19, 2020 by Thibault Marzullo:<br>First implementation.</li>
</ul>
</html>", info="<html>
<p>Packaged Single-Zone Rooftop Unit following the specifications of ASHRAE&apos;s HVAC System 3 (PZS-AC).</p>
</html>"));
    end ASHRAESystem3;
  Buildings.Utilities.Time.CalendarTime calTim(
      zerTim=Buildings.Utilities.Time.Types.ZeroTime.Custom,
      yearRef=2017,
      outputUnixTimeStamp=false)
                    "Calendar Time"
    annotation (Placement(transformation(extent={{-268,136},{-236,168}})));
  ASHRAESystem3 HVAC(heaNomPow = 14035.23, CCNomPow = -8607.92,
    controls(fanOccSet = 0.4487, minOAHVACOff =  0.080548, minOAHVACOn = 0.1795))                                      "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-14},{-42,16}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal
    annotation (Placement(transformation(extent={{-206,152},{-186,172}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal1
    annotation (Placement(transformation(extent={{-206,130},{-186,150}})));
  Modelica.Blocks.Routing.Multiplex3 mul "Multiplex for gains"
    annotation (Placement(transformation(extent={{-42,130},{-22,150}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k=0) "Convective heat gain"
    annotation (Placement(transformation(extent={{-94,130},{-74,150}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k=0) "Radiative heat gain"
    annotation (Placement(transformation(extent={{-94,170},{-74,190}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k=0) "Latent heat gain"
    annotation (Placement(transformation(extent={{-94,98},{-74,118}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
        transformation(extent={{-202,58},{-162,98}}), iconTransformation(extent={{-102,
              -558},{-8,-464}})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow(u(min=0.0, max=15000.0, unit="W"), description=
          "Core Heating Coil Power",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"Core heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={120,-10})));
  ASHRAESystem3 HVAC1(heaNomPow = 11316.80, CCNomPow = -6909.58,
    controls(fanOccSet = 0.3703, minOAHVACOff =  0.061060, minOAHVACOn =  0.1649))   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-94},{-40,-64}})));
  ASHRAESystem3 HVAC2(heaNomPow = 9873.02, CCNomPow = -6137.71,
    controls(fanOccSet = 0.3604, minOAHVACOff = 0.036222, minOAHVACOn =  0.1005))   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-184},{-40,-154}})));
  ASHRAESystem3 HVAC3(heaNomPow = 11587.62, CCNomPow = -7081.44,
    controls(fanOccSet = 0.3824, minOAHVACOff = 0.061060, minOAHVACOn = 0.1597))   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-272},{-42,-242}})));
  ASHRAESystem3 HVAC4(heaNomPow = 9691.66, CCNomPow = -6779.76,
    controls(fanOccSet = 0.3523, minOAHVACOff = 0.036222, minOAHVACOn = 0.1028))   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-350},{-40,-320}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon1(
      zoneName="Perimeter_ZN_1",
      redeclare final package Medium = Medium,
      nPorts=4) "Perimeter zone 1"
      annotation (Placement(transformation(extent={{54,-94},{94,-54}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon2(
      zoneName="Perimeter_ZN_2",
      redeclare final package Medium = Medium,
      nPorts=4) "Perimeter zone 2"
      annotation (Placement(transformation(extent={{54,-184},{94,-144}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon3(
      zoneName="Perimeter_ZN_3",
      redeclare final package Medium = Medium,
      nPorts=4) "Perimeter zone 3"
      annotation (Placement(transformation(extent={{52,-274},{92,-234}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon4(
      zoneName="Perimeter_ZN_4",
      redeclare final package Medium = Medium,
      nPorts=4) "Perimeter zone 4"
      annotation (Placement(transformation(extent={{52,-352},{92,-312}})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow1(u(min=0.0, max=15000.0, unit="W"), description=
          "P1 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P1 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={166,-88})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow2(u(min=0.0, max=15000.0, unit="W"), description=
          "P2 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P2 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={136,-182})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow3(u(min=0.0, max=15000.0, unit="W"), description=
          "P3 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P3 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={164,-274})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow4(u(min=0.0, max=15000.0, unit="W"), description=
          "P4 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P4 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={132,-376})));
Buildings.Utilities.IO.SignalExchange.Read senHou(u(min=0.0, max=24, unit="1"), description=
          "Current hour - 24hr", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Hour of the day - 24hr\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={146,-444})));
Buildings.Utilities.IO.SignalExchange.Read senDay(u(min=0.0, max=7, unit="1"), description=
          "Day of the week - 1 to 7", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Day of the week - 1 to 7\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={146,-476})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow4(u(min=0.0, max=2000.0, unit="W"), description="P4 Fan Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P4 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={132,-406})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow4(u(min=-9000, max=0, unit="W"), description="P4 Cooling Coil Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P4 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={132,-346})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow3(u(min=0.0, max=2000.0, unit="W"), description="P3 Fan Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P3 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={164,-304})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow3(u(min=-9000, max=0, unit="W"), description="P3 Cooling Coil Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P3 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={164,-244})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow2(u(min=0.0, max=2000.0, unit="W"), description="P2 Fan Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P2 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={136,-214})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow2(u(min=-9000, max=0, unit="W"), description="P2 Cooling Coil Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P2 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={136,-154})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow1(u(min=0.0, max=2000.0, unit="W"), description="P1 Fan Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P1 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={166,-120})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow1(u(min=-9000, max=0, unit="W"), description="P1 Cooling Coil Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"P1 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={166,-60})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow(u(min=0.0, max=2000.0, unit="W"), description="Core Fan Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Core zone fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={122,-40})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow(u(min=-9000, max=0, unit="W"), description="Core Cooling Coil Power demand",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Core zone cooling coil power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={122,20})));
Buildings.Utilities.IO.SignalExchange.Read senTemOA(u(min=240.0, max=320.0, unit="K"), description="OA Temperature",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
    "Outside air temperature from weather file" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={148,-508})));
Buildings.Utilities.IO.SignalExchange.Read senMin(
      u(min=0,
        max=60,
        unit="1"),
      description="Minutes",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "Minutes of the hour" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={-168,186})));
    Modelica.Blocks.Math.MultiSum multiSum5(nu=3)
      annotation (Placement(transformation(extent={{220,-6},{232,6}})));
Buildings.Utilities.IO.SignalExchange.Read senPowCor(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Core AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Core zone AHU power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={264,0})));
    Modelica.Blocks.Math.MultiSum multiSum4(nu=3)
      annotation (Placement(transformation(extent={{242,-94},{254,-82}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer1(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 1 AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Perimeter zone 1 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={294,-92})));
    Modelica.Blocks.Math.MultiSum multiSum3(nu=3)
      annotation (Placement(transformation(extent={{244,-188},{256,-176}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer2(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 2 AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Perimeter zone 2 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={298,-184})));
    Modelica.Blocks.Math.MultiSum multiSum2(nu=3)
      annotation (Placement(transformation(extent={{240,-272},{252,-260}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer3(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 3 AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Perimeter zone 3 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={302,-268})));
    Modelica.Blocks.Math.MultiSum multiSum(nu=3)
      annotation (Placement(transformation(extent={{230,-374},{242,-362}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer4(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 4 AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Perimeter zone 4 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={312,-366})));
    Buildings.Airflow.Multizone.ZonalFlow_ACS airLeaCor(V=456.46, redeclare
        final package Medium = Medium)
    "OA air leakage in the core zone"
    annotation (Placement(transformation(extent={{-86,-44},{-66,-24}})));
  Modelica.Blocks.Sources.RealExpression OAInfCor(y=OAInfCore)
    "Core zone OA infiltration"
    annotation (Placement(transformation(extent={{-120,-34},{-100,-14}})));
    Buildings.Airflow.Multizone.ZonalFlow_ACS airLeaPer1(V=346.02, redeclare
        final package Medium = Medium)
    "OA air leakage in the perimeter zone 1"
    annotation (Placement(transformation(extent={{-86,-128},{-66,-108}})));
  Modelica.Blocks.Sources.RealExpression OAInfPer1(y=OAInfP1)
    "Perimeter zone 1 OA infiltration"
    annotation (Placement(transformation(extent={{-120,-118},{-100,-98}})));
  Modelica.Blocks.Sources.RealExpression OAInfPer2(y=OAInfP2)
    "Perimeter zone 2 OA infiltration"
    annotation (Placement(transformation(extent={{-122,-204},{-102,-184}})));
    Buildings.Airflow.Multizone.ZonalFlow_ACS airLeaPer2(V=205.26, redeclare
        final package Medium = Medium)
    "OA air leakage in the perimeter zone 2"
    annotation (Placement(transformation(extent={{-90,-222},{-70,-202}})));
  Modelica.Blocks.Sources.RealExpression OAInfPer3(y=OAInfP3)
    "Perimeter zone 3 OA infiltration"
    annotation (Placement(transformation(extent={{-126,-294},{-106,-274}})));
    Buildings.Airflow.Multizone.ZonalFlow_ACS airLeaPer3(V=346.02, redeclare
        final package Medium = Medium)
    "OA air leakage in the perimeter zone 3"
    annotation (Placement(transformation(extent={{-88,-306},{-68,-286}})));
    Buildings.Airflow.Multizone.ZonalFlow_ACS airLeaPer4(V=205.26, redeclare
        final package Medium = Medium)
    "OA air leakage in the perimeter zone 3"
    annotation (Placement(transformation(extent={{-92,-386},{-72,-366}})));
  Modelica.Blocks.Sources.RealExpression OAInfPer4(y=OAInfP4)
    "Perimeter zone 4 OA infiltration"
    annotation (Placement(transformation(extent={{-122,-376},{-102,-356}})));
equation

  connect(calTim.hour, integerToReal.u) annotation (Line(points={{-234.4,162.24},
          {-216.2,162.24},{-216.2,162},{-208,162}}, color={255,127,0}));
  connect(integerToReal.y, HVAC.hour) annotation (Line(points={{-185,162},{-130,
            162},{-130,-11.125},{-96.4372,-11.125}},    color={0,0,127}));
  connect(HVAC.day, integerToReal1.y) annotation (Line(points={{-96.4372,-6.5},{
            -134,-6.5},{-134,140},{-185,140}},color={0,0,127}));
  connect(HVAC.OAInlPor, Outside.ports[1]) annotation (Line(points={{-97.3488,
            20.375},{-144,20.375},{-144,11.8},{-184,11.8}},
                                                        color={0,127,255}));
  connect(HVAC.OAOutPor, Outside.ports[2]) annotation (Line(points={{-97.3488,4},
            {-140,4},{-140,11.4},{-184,11.4}},
                                           color={0,127,255}));
  connect(mul.u3[1],qLatGai_flow. y) annotation (Line(points={{-44,133},{-54,
            133},{-54,108},{-73,108}},
                                color={0,0,127}));
  connect(qConGai_flow.y,mul. u2[1]) annotation (Line(
      points={{-73,140},{-44,140}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(qRadGai_flow.y,mul. u1[1]) annotation (Line(
      points={{-73,180},{-54,180},{-54,147},{-44,147}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(mul.y, corZon.qGai_flow) annotation (Line(points={{-21,140},{46,140},
            {46,94},{52,94}},
                        color={0,0,127}));
  connect(Outside.weaBus, building.weaBus) annotation (Line(
      points={{-204,8.2},{-204,35.1},{-254,35.1},{-254,82}},
      color={255,204,51},
      thickness=0.5));
  connect(building.weaBus, weaBus) annotation (Line(
      points={{-254,82},{-218,82},{-218,78},{-182,78}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{6,3},{6,3}},
      horizontalAlignment=TextAlignment.Left));
  connect(weaBus.TDryBul, HVAC.senTemOA) annotation (Line(
      points={{-182,78},{-140,78},{-140,-1},{-96.5674,-1}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
    connect(corZon.TAir, HVAC.temSenRet) annotation (Line(points={{95,97.8},{
            31.5,97.8},{31.5,24.625},{-33.014,24.625}},
                                                   color={0,0,127}));
    connect(perZon1.qGai_flow, mul.y) annotation (Line(points={{52,-64},{52,-62},
            {46,-62},{46,140},{-21,140}},
                                       color={0,0,127}));
    connect(perZon2.qGai_flow, mul.y) annotation (Line(points={{52,-154},{46,
            -154},{46,140},{-21,140}},
                                    color={0,0,127}));
    connect(perZon3.qGai_flow, mul.y) annotation (Line(points={{50,-244},{46,
            -244},{46,140},{-21,140}},
                                    color={0,0,127}));
    connect(perZon4.qGai_flow, mul.y) annotation (Line(points={{50,-322},{46,
            -322},{46,140},{-21,140}},
                                    color={0,0,127}));
    connect(HVAC1.OAInlPor, Outside.ports[3]) annotation (Line(points={{
            -95.3488,-59.625},{-132,-59.625},{-132,-60},{-144,-60},{-144,8},{
            -184,8},{-184,11}}, color={0,127,255}));
    connect(HVAC1.OAOutPor, Outside.ports[4]) annotation (Line(points={{
            -95.3488,-76},{-100,-76},{-100,-74},{-146,-74},{-146,6},{-180,6},{
            -180,10.6},{-184,10.6}},
                                   color={0,127,255}));
    connect(HVAC2.OAInlPor, Outside.ports[5]) annotation (Line(points={{
            -95.3488,-149.625},{-95.3488,-150},{-150,-150},{-150,10.2},{-184,
            10.2}},
          color={0,127,255}));
    connect(HVAC2.OAOutPor, Outside.ports[6]) annotation (Line(points={{
            -95.3488,-166},{-154,-166},{-154,9.8},{-184,9.8}}, color={0,127,255}));
    connect(HVAC3.OAInlPor, Outside.ports[7]) annotation (Line(points={{
            -97.3488,-237.625},{-160,-237.625},{-160,9.4},{-184,9.4}}, color={0,
            127,255}));
    connect(HVAC3.OAOutPor, Outside.ports[8]) annotation (Line(points={{
            -97.3488,-254},{-164,-254},{-164,9},{-184,9}}, color={0,127,255}));
    connect(HVAC4.OAInlPor, Outside.ports[9]) annotation (Line(points={{
            -95.3488,-315.625},{-168,-315.625},{-168,8.6},{-184,8.6}}, color={0,
            127,255}));
    connect(HVAC4.OAOutPor, Outside.ports[10]) annotation (Line(points={{
            -95.3488,-332},{-172,-332},{-172,8.2},{-184,8.2}}, color={0,127,255}));
    connect(HVAC4.zonSupPort, perZon4.ports[1]) annotation (Line(points={{
            -28.9302,-315.625},{10,-315.625},{10,-360},{69,-360},{69,-351.1}},
          color={0,127,255}));
    connect(HVAC4.zonRetPor, perZon4.ports[2]) annotation (Line(points={{-28.8,
            -331.875},{0,-331.875},{0,-366},{71,-366},{71,-351.1}}, color={0,
            127,255}));
    connect(HVAC3.zonSupPort, perZon3.ports[1]) annotation (Line(points={{
            -30.9302,-237.625},{8,-237.625},{8,-278},{69,-278},{69,-273.1}},
          color={0,127,255}));
    connect(HVAC3.zonRetPor, perZon3.ports[2]) annotation (Line(points={{-30.8,
            -253.875},{-30.8,-254},{2,-254},{2,-282},{71,-282},{71,-273.1}},
          color={0,127,255}));
    connect(HVAC2.zonSupPort, perZon2.ports[1]) annotation (Line(points={{
            -28.9302,-149.625},{2,-149.625},{2,-190},{71,-190},{71,-183.1}},
          color={0,127,255}));
    connect(HVAC2.zonRetPor, perZon2.ports[2]) annotation (Line(points={{-28.8,
            -165.875},{-2,-165.875},{-2,-198},{73,-198},{73,-183.1}}, color={0,
            127,255}));
    connect(HVAC1.zonSupPort, perZon1.ports[1]) annotation (Line(points={{
            -28.9302,-59.625},{6,-59.625},{6,-98},{71,-98},{71,-93.1}}, color={
            0,127,255}));
    connect(HVAC1.zonRetPor, perZon1.ports[2]) annotation (Line(points={{-28.8,
            -75.875},{0,-75.875},{0,-106},{73,-106},{73,-93.1}}, color={0,127,
            255}));
    connect(perZon1.TAir, HVAC1.temSenRet) annotation (Line(points={{95,-60.2},
            {100,-60.2},{100,-52},{-31.014,-52},{-31.014,-55.375}}, color={0,0,
            127}));
    connect(perZon2.TAir, HVAC2.temSenRet) annotation (Line(points={{95,-150.2},
            {102,-150.2},{102,-140},{-12,-140},{-12,-145.375},{-31.014,-145.375}},
          color={0,0,127}));
    connect(perZon3.TAir, HVAC3.temSenRet) annotation (Line(points={{93,-240.2},
            {102,-240.2},{102,-226},{-4,-226},{-4,-233.375},{-33.014,-233.375}},
          color={0,0,127}));
    connect(perZon4.TAir, HVAC4.temSenRet) annotation (Line(points={{93,-318.2},
            {102,-318.2},{102,-304},{2,-304},{2,-311.375},{-31.014,-311.375}},
          color={0,0,127}));
    connect(HVAC1.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,
            -81},{-140,-81},{-140,-1},{-96.5674,-1}}, color={0,0,127}));
    connect(HVAC2.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,
            -171},{-140,-171},{-140,-1},{-96.5674,-1}}, color={0,0,127}));
    connect(HVAC3.senTemOA, HVAC.senTemOA) annotation (Line(points={{-96.5674,
            -259},{-140,-259},{-140,-1},{-96.5674,-1}}, color={0,0,127}));
    connect(HVAC4.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,
            -337},{-118,-337},{-118,-338},{-140,-338},{-140,-1},{-96.5674,-1}},
          color={0,0,127}));
    connect(HVAC1.day, integerToReal1.y) annotation (Line(points={{-94.4372,-86.5},
            {-134,-86.5},{-134,140},{-185,140}},        color={0,0,127}));
    connect(HVAC1.hour, HVAC.hour) annotation (Line(points={{-94.4372,-91.125},{
            -130,-91.125},{-130,-11.125},{-96.4372,-11.125}},  color={0,0,127}));
    connect(HVAC2.day, integerToReal1.y) annotation (Line(points={{-94.4372,-176.5},
            {-134,-176.5},{-134,140},{-185,140}},         color={0,0,127}));
    connect(HVAC2.hour, HVAC.hour) annotation (Line(points={{-94.4372,-181.125},
            {-130,-181.125},{-130,-11.125},{-96.4372,-11.125}}, color={0,0,127}));
    connect(HVAC3.day, integerToReal1.y) annotation (Line(points={{-96.4372,-264.5},
            {-134,-264.5},{-134,140},{-185,140}},         color={0,0,127}));
    connect(HVAC3.hour, HVAC.hour) annotation (Line(points={{-96.4372,-269.125},
            {-130,-269.125},{-130,-11.125},{-96.4372,-11.125}}, color={0,0,127}));
    connect(HVAC4.day, integerToReal1.y) annotation (Line(points={{-94.4372,
            -342.5},{-134,-342.5},{-134,140},{-185,140}}, color={0,0,127}));
    connect(HVAC4.hour, HVAC.hour) annotation (Line(points={{-94.4372,-347.125},
            {-94.4372,-348},{-130,-348},{-130,-11.125},{-96.4372,-11.125}},
          color={0,0,127}));
    connect(senHou.u, HVAC.hour) annotation (Line(points={{134,-444},{-130,-444},
            {-130,-11.125},{-96.4372,-11.125}},       color={0,0,127}));
    connect(senDay.u, integerToReal1.y) annotation (Line(points={{134,-476},{
            -134,-476},{-134,140},{-185,140}}, color={0,0,127}));
    connect(senHeaPow3.u, HVAC3.heaPowDem) annotation (Line(points={{152,-274},
            {142,-274},{142,-290},{-49.0326,-290},{-49.0326,-273.5}}, color={0,
            0,127}));
    connect(senFanPow3.u, HVAC3.fanPowDem) annotation (Line(points={{152,-304},
            {142,-304},{142,-294},{-55.2837,-294},{-55.2837,-273.5}},color={0,0,
            127}));
    connect(senCCPow3.u, HVAC3.cooPowDem) annotation (Line(points={{152,-244},{
            138,-244},{138,-284},{-42.1302,-284},{-42.1302,-273.5}},
                                                                 color={0,0,127}));
    connect(senHeaPow4.u, HVAC4.heaPowDem) annotation (Line(points={{120,-376},
            {110,-376},{110,-386},{-47.0326,-386},{-47.0326,-351.5}}, color={0,
            0,127}));
    connect(senCCPow4.u, HVAC4.cooPowDem) annotation (Line(points={{120,-346},{
            106,-346},{106,-380},{-40.1302,-380},{-40.1302,-351.5}},
                                                                 color={0,0,127}));
    connect(senFanPow4.u, HVAC4.fanPowDem) annotation (Line(points={{120,-406},
            {116,-406},{116,-390},{-53.2837,-390},{-53.2837,-351.5}},color={0,0,
            127}));
    connect(senCCPow2.u, HVAC2.cooPowDem) annotation (Line(points={{124,-154},{
            100,-154},{100,-204},{-40.1302,-204},{-40.1302,-185.5}},
                                                                 color={0,0,127}));
    connect(senHeaPow2.u, HVAC2.heaPowDem) annotation (Line(points={{124,-182},
            {104,-182},{104,-208},{-47.0326,-208},{-47.0326,-185.5}}, color={0,
            0,127}));
    connect(senFanPow2.u, HVAC2.fanPowDem) annotation (Line(points={{124,-214},
            {-53.2837,-214},{-53.2837,-185.5}},color={0,0,127}));
    connect(senCCPow1.u, HVAC1.cooPowDem) annotation (Line(points={{154,-60},{
            106,-60},{106,-112},{-40.1302,-112},{-40.1302,-95.5}},
                                                               color={0,0,127}));
    connect(senHeaPow1.u, HVAC1.heaPowDem) annotation (Line(points={{154,-88},{
            114,-88},{114,-118},{-47.0326,-118},{-47.0326,-95.5}}, color={0,0,
            127}));
    connect(senFanPow1.u, HVAC1.fanPowDem) annotation (Line(points={{154,-120},
            {122,-120},{122,-124},{-53.2837,-124},{-53.2837,-95.5}},color={0,0,127}));
    connect(senHeaPow.u, HVAC.heaPowDem) annotation (Line(points={{108,-10},{98,
            -10},{98,-24},{-49.0326,-24},{-49.0326,-15.5}},    color={0,0,127}));
    connect(senCCPow.u, HVAC.cooPowDem) annotation (Line(points={{110,20},{94,
            20},{94,-20},{-42.1302,-20},{-42.1302,-15.5}},
                                                       color={0,0,127}));
    connect(senFanPow.u, HVAC.fanPowDem) annotation (Line(points={{110,-40},{
            100,-40},{100,-28},{-55.2837,-28},{-55.2837,-15.5}},
                                                             color={0,0,127}));
  connect(senTemOA.u, HVAC.senTemOA) annotation (Line(points={{136,-508},{-140,
            -508},{-140,-1},{-96.5674,-1}},
                                    color={0,0,127}));
    connect(calTim.weekDay, integerToReal1.u) annotation (Line(points={{-234.4,
            145.6},{-221.2,145.6},{-221.2,140},{-208,140}}, color={255,127,0}));
    connect(senMin.u, calTim.minute) annotation (Line(points={{-180,186},{-220,186},
            {-220,166.4},{-234.4,166.4}}, color={0,0,127}));
    connect(multiSum5.y,senPowCor. u)
      annotation (Line(points={{233.02,0},{252,0}},   color={0,0,127}));
    connect(multiSum4.y,senPowPer1. u) annotation (Line(points={{255.02,-88},{268,
            -88},{268,-92},{282,-92}}, color={0,0,127}));
    connect(multiSum3.y,senPowPer2. u) annotation (Line(points={{257.02,-182},{272,
            -182},{272,-184},{286,-184}}, color={0,0,127}));
    connect(multiSum2.y,senPowPer3. u) annotation (Line(points={{253.02,-266},{270,
            -266},{270,-268},{290,-268}}, color={0,0,127}));
    connect(multiSum.y,senPowPer4. u) annotation (Line(points={{243.02,-368},{272,
            -368},{272,-366},{300,-366}}, color={0,0,127}));
    connect(senCCPow.y, multiSum5.u[1]) annotation (Line(points={{133,20},{176,20},
            {176,2.8},{220,2.8}}, color={0,0,127}));
    connect(senHeaPow.y, multiSum5.u[2]) annotation (Line(points={{131,-10},{176,
            -10},{176,4.44089e-16},{220,4.44089e-16}}, color={0,0,127}));
    connect(senFanPow.y, multiSum5.u[3]) annotation (Line(points={{133,-40},{180,
            -40},{180,-2.8},{220,-2.8}}, color={0,0,127}));
    connect(senCCPow1.y, multiSum4.u[1]) annotation (Line(points={{177,-60},{210,
            -60},{210,-85.2},{242,-85.2}}, color={0,0,127}));
    connect(senHeaPow1.y, multiSum4.u[2]) annotation (Line(points={{177,-88},{210,
            -88},{210,-88},{242,-88}}, color={0,0,127}));
    connect(senFanPow1.y, multiSum4.u[3]) annotation (Line(points={{177,-120},{210,
            -120},{210,-90.8},{242,-90.8}}, color={0,0,127}));
    connect(senCCPow2.y, multiSum3.u[1]) annotation (Line(points={{147,-154},{196,
            -154},{196,-179.2},{244,-179.2}}, color={0,0,127}));
    connect(senHeaPow2.y, multiSum3.u[2]) annotation (Line(points={{147,-182},{196,
            -182},{196,-182},{244,-182}}, color={0,0,127}));
    connect(senFanPow2.y, multiSum3.u[3]) annotation (Line(points={{147,-214},{196,
            -214},{196,-184.8},{244,-184.8}}, color={0,0,127}));
    connect(senCCPow3.y, multiSum2.u[1]) annotation (Line(points={{175,-244},{208,
            -244},{208,-263.2},{240,-263.2}}, color={0,0,127}));
    connect(senHeaPow3.y, multiSum2.u[2]) annotation (Line(points={{175,-274},{208,
            -274},{208,-266},{240,-266}}, color={0,0,127}));
    connect(senFanPow3.y, multiSum2.u[3]) annotation (Line(points={{175,-304},{212,
            -304},{212,-268.8},{240,-268.8}}, color={0,0,127}));
    connect(senCCPow4.y, multiSum.u[1]) annotation (Line(points={{143,-346},{186,
            -346},{186,-365.2},{230,-365.2}}, color={0,0,127}));
    connect(senHeaPow4.y, multiSum.u[2]) annotation (Line(points={{143,-376},{186,
            -376},{186,-368},{230,-368}}, color={0,0,127}));
    connect(senFanPow4.y, multiSum.u[3]) annotation (Line(points={{143,-406},{190,
            -406},{190,-370.8},{230,-370.8}}, color={0,0,127}));
    connect(airLeaCor.ACS, OAInfCor.y)
      annotation (Line(points={{-87,-24},{-99,-24}}, color={0,0,127}));
  connect(OAInfPer1.y,airLeaPer1. ACS) annotation (Line(points={{-99,-108},{-87,
            -108}},                  color={0,0,127}));
  connect(OAInfPer2.y,airLeaPer2. ACS) annotation (Line(points={{-101,-194},{
            -96,-194},{-96,-202},{-91,-202}},
                                        color={0,0,127}));
  connect(OAInfPer3.y,airLeaPer3. ACS) annotation (Line(points={{-105,-284},{
            -96,-284},{-96,-286},{-89,-286}},
                                        color={0,0,127}));
    connect(OAInfPer4.y, airLeaPer4.ACS)
      annotation (Line(points={{-101,-366},{-93,-366}}, color={0,0,127}));
    connect(airLeaPer4.port_a1, Outside.ports[11]) annotation (Line(points={{
            -92,-370},{-148,-370},{-148,-315.625},{-168,-315.625},{-168,5.2},{
            -184,5.2},{-184,7.8}}, color={0,127,255}));
    connect(airLeaPer4.port_b2, Outside.ports[12]) annotation (Line(points={{
            -92,-382},{-160,-382},{-160,-332},{-172,-332},{-172,5.09091},{-184,
            5.09091},{-184,7.4}}, color={0,127,255}));
    connect(airLeaPer4.port_b1, perZon4.ports[3]) annotation (Line(points={{-72,
            -370},{73,-370},{73,-351.1}}, color={0,127,255}));
    connect(airLeaPer4.port_a2, perZon4.ports[4]) annotation (Line(points={{-72,
            -382},{75,-382},{75,-351.1}}, color={0,127,255}));
    connect(airLeaPer3.port_a1, Outside.ports[13]) annotation (Line(points={{
            -88,-290},{-168,-290},{-168,6.33333},{-184,6.33333},{-184,7}},
          color={0,127,255}));
    connect(airLeaPer3.port_b2, Outside.ports[14]) annotation (Line(points={{
            -88,-302},{-172,-302},{-172,6.15385},{-184,6.15385},{-184,6.6}},
          color={0,127,255}));
    connect(airLeaPer3.port_b1, perZon3.ports[3]) annotation (Line(points={{-68,
            -290},{73,-290},{73,-273.1}}, color={0,127,255}));
    connect(airLeaPer3.port_a2, perZon3.ports[4]) annotation (Line(points={{-68,
            -302},{75,-302},{75,-273.1}}, color={0,127,255}));
    connect(airLeaPer2.port_a1, Outside.ports[15]) annotation (Line(points={{
            -90,-206},{-160,-206},{-160,8.28571},{-184,8.28571},{-184,6.2}},
          color={0,127,255}));
    connect(airLeaPer2.port_b2, Outside.ports[16]) annotation (Line(points={{
            -90,-218},{-164,-218},{-164,5.8},{-184,5.8}}, color={0,127,255}));
    connect(airLeaPer2.port_b1, perZon2.ports[3]) annotation (Line(points={{-70,
            -206},{75,-206},{75,-183.1}}, color={0,127,255}));
    connect(airLeaPer2.port_a2, perZon2.ports[4]) annotation (Line(points={{-70,
            -218},{77,-218},{77,-183.1}}, color={0,127,255}));
    connect(airLeaPer1.port_a1, Outside.ports[17]) annotation (Line(points={{
            -86,-112},{-150,-112},{-150,9.75},{-184,9.75},{-184,5.4}}, color={0,
            127,255}));
    connect(airLeaPer1.port_b2, Outside.ports[18]) annotation (Line(points={{
            -86,-124},{-154,-124},{-154,9.41176},{-184,9.41176},{-184,5}},
          color={0,127,255}));
    connect(airLeaPer1.port_b1, perZon1.ports[3]) annotation (Line(points={{-66,
            -112},{75,-112},{75,-93.1}}, color={0,127,255}));
    connect(airLeaPer1.port_a2, perZon1.ports[4]) annotation (Line(points={{-66,
            -124},{77,-124},{77,-93.1}}, color={0,127,255}));
    connect(airLeaCor.port_a1, Outside.ports[19]) annotation (Line(points={{-86,
            -28},{-144,-28},{-144,4.6},{-184,4.6}}, color={0,127,255}));
    connect(airLeaCor.port_b2, Outside.ports[20]) annotation (Line(points={{-86,
            -40},{-146,-40},{-146,6},{-180,6},{-180,10.5263},{-184,10.5263},{
            -184,4.2}}, color={0,127,255}));
    connect(airLeaCor.port_a2, corZon.ports[1]) annotation (Line(points={{-66,
            -40},{71,-40},{71,64.9}}, color={0,127,255}));
    connect(HVAC.zonRetPor, corZon.ports[2]) annotation (Line(points={{-30.8,
            4.125},{73,4.125},{73,64.9}}, color={0,127,255}));
    connect(HVAC.zonSupPort, corZon.ports[3]) annotation (Line(points={{
            -30.9302,20.375},{75,20.375},{75,64.9}}, color={0,127,255}));
    connect(airLeaCor.port_b1, corZon.ports[4]) annotation (Line(points={{-66,
            -28},{77,-28},{77,64.9}}, color={0,127,255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-280,
              -500},{180,200}}), graphics={
          Rectangle(
            extent={{-280,202},{180,-502}},
            lineColor={0,0,0},
            fillColor={28,108,200},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-274,20},{172,-312}},
            lineColor={215,215,215},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            lineThickness=1),
          Bitmap(
            extent={{-256,-354},{156,58}},
            imageSource="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"
                 + "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",
            fileName="modelica://wrapped/../../../../../../Pictures/Screenshot from 2021-02-11 15-49-58.png"),
          Rectangle(
            extent={{-272,184},{170,38}},
            lineColor={215,215,215},
            lineThickness=1,
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
          Bitmap(extent={{-258,44},{-128,174}},
            imageSource=
                "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",

            fileName=
                "modelica://wrapped/../../../../../../../Pictures/Screenshot from 2021-02-11 15-58-21.png"),
          Text(
            extent={{-110,184},{146,48}},
            lineColor={0,0,0},
            lineThickness=1,
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid,
            textString="SoEP",
            textStyle={TextStyle.Bold}),
          Rectangle(
            extent={{-272,-330},{172,-490}},
            lineColor={215,215,215},
            lineThickness=1,
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
          Text(
            extent={{-264,-326},{172,-490}},
            lineColor={0,0,0},
            lineThickness=1,
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid,
            textStyle={TextStyle.Bold},
            textString="Small Office
Building")}),                                                    Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-280,-500},{180,
              200}})),
    uses(Buildings(version="8.0.0"), Modelica(version="3.2.3")),
    experiment(
      StopTime=84600,
      Interval=60,
      __Dymola_Algorithm="Dassl"));
end SOM3;
  //SOM3 - A Spawn of EnergyPlus model for BOPTEST
  //Model: DOE Prototype Small Office Building
  //Zones:
  //        1: Core zone
  //        2: Perimeter 1
  //        3: Perimeter 2
  //        4: Perimeter 3
  //        5: Perimeter 4

  ////////////
  // INPUTS //
  ////////////



  // Temperature setpoints

  Modelica.Blocks.Interfaces.RealInput oveHeaOccSet_u(
    unit="K",
    min=273.15,
    max=313.15) "Core zone heating setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaOccSet_activate
    "Activation for core zone heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHeaNonOccSet_u(
    unit="K",
    min=273.15,
    max=313.15) "Core zone heating setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaNonOccSet_activate
    "Activation for core zone heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooOccSet_u(
    unit="K",
    min=273.15,
    max=313.15) "Core zone cooling setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooOccSet_activate
    "Activation for core zone cooling setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooNonOccSet_u(
    unit="K",
    min=273.15,
    max=313.15) "Core zone cooling setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooNonOccSet_activate
    "Activation for core zone cooling setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHeaOccSet1_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 1 heating setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaOccSet1_activate
    "Activation for perimeter zone 1 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHeaNonOccSet1_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 1 heating setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaNonOccSet1_activate
    "Activation for perimeter zone 1 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooOccSet1_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 1 cooling setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooOccSet1_activate
    "Activation for perimeter zone 1 cooling setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooNonOccSet1_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 1 cooling setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooNonOccSet1_activate
    "Activation for Perimeter zone 1 cooling setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHeaOccSet2_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 2 heating setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaOccSet2_activate
    "Activation for perimeter zone 2 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHeaNonOccSet2_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 2 heating setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaNonOccSet2_activate
    "Activation for perimeter zone 2 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooOccSet2_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 2 cooling setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooOccSet2_activate
    "Activation for perimeter zone 2 cooling setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooNonOccSet2_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 2 cooling setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooNonOccSet2_activate
    "Activation for Perimeter zone 2 cooling setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHeaOccSet3_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 3 heating setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaOccSet3_activate
    "Activation for perimeter zone 3 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHeaNonOccSet3_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 3 heating setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaNonOccSet3_activate
    "Activation for perimeter zone 3 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooOccSet3_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 3 cooling setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooOccSet3_activate
    "Activation for perimeter zone 3 cooling setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooNonOccSet3_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 3 cooling setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooNonOccSet3_activate
    "Activation for Perimeter zone 3 cooling setpoint";

    Modelica.Blocks.Interfaces.RealInput oveHeaOccSet4_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 4 heating setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaOccSet4_activate
    "Activation for perimeter zone 4 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHeaNonOccSet4_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 4 heating setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveHeaNonOccSet4_activate
    "Activation for perimeter zone 4 heating setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooOccSet4_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 4 cooling setpoint, occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooOccSet4_activate
    "Activation for perimeter zone 4 cooling setpoint";
  Modelica.Blocks.Interfaces.RealInput oveCooNonOccSet4_u(
    unit="K",
    min=273.15,
    max=313.15) "Perimeter zone 4 cooling setpoint, non occupied (K)";
  Modelica.Blocks.Interfaces.BooleanInput oveCooNonOccSet4_activate
    "Activation for Perimeter zone 4 cooling setpoint";

  // Heating coils
  Modelica.Blocks.Interfaces.RealInput oveHCSet_u(
    unit="1",
    min=0,
    max=1) "Core zone heating coil setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveHCSet_activate
    "Activation for core zone heating coil setpoint";
  Modelica.Blocks.Interfaces.RealInput oveHCSet1_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 1 heating coil setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveHCSet1_activate
    "Activation for perimeter 1 heating coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHCSet2_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 2 heating coil setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveHCSet2_activate
    "Activation for perimeter 2 heating coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHCSet3_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 3 heating coil setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveHCSet3_activate
    "Activation for perimeter 3 heating coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveHCSet4_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 4 heating coil setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveHCSet4_activate
    "Activation for perimeter 4 heating coil setpoint";



  // Cooling coils

  Modelica.Blocks.Interfaces.RealInput oveCC_u(
    unit="1",
    min=0,
    max=1) "Core zone cooling coil On/Off (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveCC_activate
    "Activation for core zone cooling coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveCC1_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 1 cooling coil On/Off (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveCC1_activate
    "Activation for perimeter zone 1 cooling coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveCC2_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 2 cooling coil On/Off (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveCC2_activate
    "Activation for perimeter zone 2 cooling coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveCC3_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 3 cooling coil On/Off (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveCC3_activate
    "Activation for perimeter zone 3 cooling coil setpoint";

  Modelica.Blocks.Interfaces.RealInput oveCC4_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 4 cooling coil On/Off (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveCC4_activate
    "Activation for perimeter zone 4 cooling coil setpoint";

  // OA damper settings

  Modelica.Blocks.Interfaces.RealInput oveDSet_u(
    unit="1",
    min=0,
    max=1) "Core zone OA damper setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveDSet_activate
    "Activation for core zone OA damper setpoint";

  Modelica.Blocks.Interfaces.RealInput oveDSet1_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 1 OA damper setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveDSet1_activate
    "Activation for perimeter zone 1 OA damper setpoint";

  Modelica.Blocks.Interfaces.RealInput oveDSet2_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 2 OA damper setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveDSet2_activate
    "Activation for perimeter zone 2 OA damper setpoint";

  Modelica.Blocks.Interfaces.RealInput oveDSet3_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 3 OA damper setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveDSet3_activate
    "Activation for perimeter zone 3 OA damper setpoint";

  Modelica.Blocks.Interfaces.RealInput oveDSet4_u(
    unit="1",
    min=0,
    max=1) "Perimeter zone 4 OA damper setpoint (0-1)";
  Modelica.Blocks.Interfaces.BooleanInput oveDSet4_activate
    "Activation for perimeter zone 4 OA damper setpoint";

  // Fan On/Off signals

  Modelica.Blocks.Interfaces.RealInput oveVFRSet_u(
    unit="1",
    min=0,
    max=10) "Core zone fan VFR setpoint";
  Modelica.Blocks.Interfaces.BooleanInput oveVFRSet_activate
    "Activation for core zone fan VFR setpoint";

  Modelica.Blocks.Interfaces.RealInput oveVFRSet1_u(
    unit="1",
    min=0,
    max=10) "Perimeter zone 1 fan VFR setpoint";
  Modelica.Blocks.Interfaces.BooleanInput oveVFRSet1_activate
    "Activation for perimeter zone 1 fan VFR setpoint";

  Modelica.Blocks.Interfaces.RealInput oveVFRSet2_u(
    unit="1",
    min=0,
    max=10) "Perimeter zone 2 fan VFR setpoint";
  Modelica.Blocks.Interfaces.BooleanInput oveVFRSet2_activate
    "Activation for perimeter zone 2 fan VFR setpoint";

  Modelica.Blocks.Interfaces.RealInput oveVFRSet3_u(
    unit="1",
    min=0,
    max=10) "Perimeter zone 3 fan VFR setpoint";
  Modelica.Blocks.Interfaces.BooleanInput oveVFRSet3_activate
    "Activation for perimeter zone 3 fan VFR setpoint";

  Modelica.Blocks.Interfaces.RealInput oveVFRSet4_u(
    unit="1",
    min=0,
    max=10) "Perimeter zone 4 fan VFR setpoint";
  Modelica.Blocks.Interfaces.BooleanInput oveVFRSet4_activate
    "Activation for perimeter zone 4 fan VFR setpoint";

  /////////////
  // OUTPUTS //
  /////////////

  Modelica.Blocks.Interfaces.RealOutput senTRoom_y(unit="K", min = 270, max = 310) = mod.HVAC.senTemRoo.y
    "Core Room Temperature";
  Modelica.Blocks.Interfaces.RealOutput senRH_y(unit="1", min = 0, max = 0.99) = mod.HVAC.senRelHumOut.y
    "Core Room HR";
  Modelica.Blocks.Interfaces.RealOutput senHeaPow_y(unit="W", min = 0, max = mod.HVAC.heaNomPow) = mod.senHeaPow.y
    "Core zone heating coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senCCPow_y(unit="W", min = mod.HVAC.CCNomPow, max = 0) = mod.senCCPow.y
    "Core zone cooling coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanPow_y(unit="W", min = 0, max = 2000) = mod.senFanPow.y
    "Core zone fan power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanVol_y(unit="m3/s", min = 0, max = 1) = mod.HVAC.senVolSup.y
    "Core zone fan volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senOAVol_y(unit="m3/s", min = 0, max = 1) = mod.HVAC.senVolOA.y
    "Core zone OA volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senPowCor_y(unit="W", min = 0, max = 25000) = mod.senPowCor.y
    "Core zone fAHU power demand";

  Modelica.Blocks.Interfaces.RealOutput senTRoom1_y(unit="K", min = 270, max = 310) = mod.HVAC1.senTemRoo.y
    "Perimeter zone 1 Temperature";
  Modelica.Blocks.Interfaces.RealOutput senRH1_y(unit="1", min = 0, max = 0.99) = mod.HVAC1.senRelHumOut.y
    "Perimeter zone 1 HR";
  Modelica.Blocks.Interfaces.RealOutput senHeaPow1_y(unit="1", min = 0, max = mod.HVAC1.heaNomPow) = mod.senHeaPow1.y
    "Perimeter zone 1 heating coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senCCPow1_y(unit="1", min = mod.HVAC1.CCNomPow, max = 0) = mod.senCCPow1.y
    "Perimeter zone 1 cooling coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanPow1_y(unit="1", min = 0, max = 2000) = mod.senFanPow1.y
    "Perimeter zone 1 fan power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanVol1_y(unit="m3/s", min = 0, max = 1) = mod.HVAC1.senVolSup.y
    "Perimeter zone 1 fan volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senOAVol1_y(unit="m3/s", min = 0, max = 1) = mod.HVAC1.senVolOA.y
    "Perimeter zone 1 OA volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senPowPer1_y(unit="W", min = 0, max = 25000) = mod.senPowPer1.y
    "Perimeter Zone 1 AHU power demand";

  Modelica.Blocks.Interfaces.RealOutput senTRoom2_y(unit="K", min = 270, max = 310) = mod.HVAC2.senTemRoo.y
    "Perimeter zone 2 Temperature";
  Modelica.Blocks.Interfaces.RealOutput senRH2_y(unit="1", min = 0, max = 0.99) = mod.HVAC2.senRelHumOut.y
    "Perimeter zone 2 HR";
  Modelica.Blocks.Interfaces.RealOutput senHeaPow2_y(unit="1", min = 0, max = mod.HVAC2.heaNomPow) = mod.senHeaPow2.y
    "Perimeter zone 2 heating coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senCCPow2_y(unit="1", min = mod.HVAC2.CCNomPow, max = 0) = mod.senCCPow2.y
    "Perimeter zone 2 cooling coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanPow2_y(unit="1", min = 0, max = 2000) = mod.senFanPow2.y
    "Perimeter zone 2 fan power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanVol2_y(unit="m3/s", min = 0, max = 1) = mod.HVAC2.senVolSup.y
    "Perimeter zone 2 fan volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senOAVol2_y(unit="m3/s", min = 0, max = 1) = mod.HVAC2.senVolOA.y
    "Perimeter zone 2 OA volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senPowPer2_y(unit="W", min = 0, max = 25000) = mod.senPowPer2.y
    "Perimeter Zone 2 AHU power demand";

  Modelica.Blocks.Interfaces.RealOutput senTRoom3_y(unit="K", min = 270, max = 310) = mod.HVAC3.senTemRoo.y
    "Perimeter zone 3 Temperature";
  Modelica.Blocks.Interfaces.RealOutput senRH3_y(unit="1", min = 0, max = 0.99) = mod.HVAC3.senRelHumOut.y
    "Perimeter zone 3 HR";
  Modelica.Blocks.Interfaces.RealOutput senHeaPow3_y(unit="1", min = 0, max = mod.HVAC3.heaNomPow) = mod.senHeaPow3.y
    "Perimeter zone 3 heating coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senCCPow3_y(unit="1", min = mod.HVAC3.CCNomPow, max = 0) = mod.senCCPow3.y
    "Perimeter zone 3 cooling coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanPow3_y(unit="1", min = 0, max = 2000) = mod.senFanPow3.y
    "Perimeter zone 3 fan power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanVol3_y(unit="m3/s", min = 0, max = 1) = mod.HVAC3.senVolSup.y
    "Perimeter zone 3 fan volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senOAVol3_y(unit="m3/s", min = 0, max = 1) = mod.HVAC3.senVolOA.y
    "Perimeter zone 3 OA volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senPowPer3_y(unit="W", min = 0, max = 25000) = mod.senPowPer3.y
    "Perimeter Zone 3 AHU power demand";

  Modelica.Blocks.Interfaces.RealOutput senTRoom4_y(unit="K", min = 270, max = 310) = mod.HVAC4.senTemRoo.y
    "Perimeter zone 4 Temperature";
  Modelica.Blocks.Interfaces.RealOutput senRH4_y(unit="1", min = 0, max = 0.99) = mod.HVAC4.senRelHumOut.y
    "Perimeter zone 4 HR";
  Modelica.Blocks.Interfaces.RealOutput senHeaPow4_y(unit="1", min = 0, max = mod.HVAC4.heaNomPow) = mod.senHeaPow4.y
    "Perimeter zone 4 heating coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senCCPow4_y(unit="1", min = mod.HVAC4.CCNomPow, max = 0) = mod.senCCPow4.y
    "Perimeter zone 4 cooling coil power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanPow4_y(unit="1", min = 0, max = 2000) = mod.senFanPow4.y
    "Perimeter zone 4 fan power demand";
  Modelica.Blocks.Interfaces.RealOutput senFanVol4_y(unit="m3/s", min = 0, max = 1) = mod.HVAC4.senVolSup.y
    "Perimeter zone 4 fan volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senOAVol4_y(unit="m3/s", min = 0, max = 1) = mod.HVAC4.senVolOA.y
    "Perimeter zone 4 OA volumetric flow rate";
  Modelica.Blocks.Interfaces.RealOutput senPowPer4_y(unit="W", min = 0, max = 25000) = mod.senPowPer4.y
    "Perimeter Zone 4 AHU power demand";

  Modelica.Blocks.Interfaces.RealOutput senHouMin_y(unit="1") = mod.senHou.y + mod.senMin.y / 60
    "Hour and minute of the day (24hr, decimal format)";
  Modelica.Blocks.Interfaces.RealOutput senMin_y(unit="1") = mod.senMin.y
    "Hour of the day (24hr format)";
  Modelica.Blocks.Interfaces.RealOutput senHou_y(unit="1") = mod.senHou.y
    "Hour of the day (24hr format)";
  Modelica.Blocks.Interfaces.RealOutput senDay_y(unit="1") = mod.senDay.y
    "Day of the week (1-7)";
  Modelica.Blocks.Interfaces.RealOutput senTemOA_y(unit="K") = mod.senTemOA.y
    "Outside dry bulb air temperature";

  // Original model
  SOM3 mod(HVAC(
    oveHCSet(      uExt(y=oveHCSet_u), activate(y=oveHCSet_activate)),
    oveCCSet(      uExt(y=oveCC_u), activate(y=oveCC_activate)),
    oveDamSet(      uExt(y=oveDSet_u), activate(y=oveDSet_activate)),
    oveFanSet(      uExt(y=oveVFRSet_u), activate(y=oveVFRSet_activate)),
    controls(
    oveRBCHeaSetOcc(      uExt(y=oveHeaOccSet_u), activate(y=oveHeaOccSet_activate)),
    oveRBCHeaSetNonOcc(      uExt(y=oveHeaNonOccSet_u), activate(y=oveHeaNonOccSet_activate)),
    oveRBCCooOccSet(      uExt(y=oveCooOccSet_u), activate(y=oveCooOccSet_activate)),
    oveRBCCooNonOccSet(      uExt(y=oveCooNonOccSet_u), activate(y=oveCooNonOccSet_activate)))),
    HVAC1(
    oveHCSet(      uExt(y=oveHCSet1_u), activate(y=oveHCSet1_activate)),
    oveCCSet(      uExt(y=oveCC1_u), activate(y=oveCC1_activate)),
    oveDamSet(      uExt(y=oveDSet1_u), activate(y=oveDSet1_activate)),
    oveFanSet(      uExt(y=oveVFRSet1_u), activate(y=oveVFRSet1_activate)),
    controls(
    oveRBCHeaSetOcc(      uExt(y=oveHeaOccSet1_u), activate(y=oveHeaOccSet1_activate)),
    oveRBCHeaSetNonOcc(      uExt(y=oveHeaNonOccSet1_u), activate(y=oveHeaNonOccSet1_activate)),
    oveRBCCooOccSet(      uExt(y=oveCooOccSet1_u), activate(y=oveCooOccSet1_activate)),
    oveRBCCooNonOccSet(      uExt(y=oveCooNonOccSet1_u), activate(y=oveCooNonOccSet1_activate)))),
    HVAC2(
    oveHCSet(      uExt(y=oveHCSet2_u), activate(y=oveHCSet2_activate)),
    oveCCSet(      uExt(y=oveCC2_u), activate(y=oveCC2_activate)),
    oveDamSet(      uExt(y=oveDSet2_u), activate(y=oveDSet2_activate)),
    oveFanSet(      uExt(y=oveVFRSet2_u), activate(y=oveVFRSet2_activate)),
    controls(
    oveRBCHeaSetOcc(      uExt(y=oveHeaOccSet2_u), activate(y=oveHeaOccSet2_activate)),
    oveRBCHeaSetNonOcc(      uExt(y=oveHeaNonOccSet2_u), activate(y=oveHeaNonOccSet2_activate)),
    oveRBCCooOccSet(      uExt(y=oveCooOccSet2_u), activate(y=oveCooOccSet2_activate)),
    oveRBCCooNonOccSet(      uExt(y=oveCooNonOccSet2_u), activate(y=oveCooNonOccSet2_activate)))),
    HVAC3(
    oveHCSet(      uExt(y=oveHCSet3_u), activate(y=oveHCSet3_activate)),
    oveCCSet(      uExt(y=oveCC3_u), activate(y=oveCC3_activate)),
    oveDamSet(      uExt(y=oveDSet3_u), activate(y=oveDSet3_activate)),
    oveFanSet(      uExt(y=oveVFRSet3_u), activate(y=oveVFRSet3_activate)),
    controls(
    oveRBCHeaSetOcc(      uExt(y=oveHeaOccSet3_u), activate(y=oveHeaOccSet3_activate)),
    oveRBCHeaSetNonOcc(      uExt(y=oveHeaNonOccSet3_u), activate(y=oveHeaNonOccSet3_activate)),
    oveRBCCooOccSet(      uExt(y=oveCooOccSet3_u), activate(y=oveCooOccSet3_activate)),
    oveRBCCooNonOccSet(      uExt(y=oveCooNonOccSet3_u), activate(y=oveCooNonOccSet3_activate)))),
    HVAC4(
    oveHCSet(      uExt(y=oveHCSet4_u), activate(y=oveHCSet4_activate)),
    oveCCSet(      uExt(y=oveCC4_u), activate(y=oveCC4_activate)),
    oveDamSet(      uExt(y=oveDSet4_u), activate(y=oveDSet4_activate)),
    oveFanSet(      uExt(y=oveVFRSet4_u), activate(y=oveVFRSet4_activate)),
    controls(
    oveRBCHeaSetOcc(      uExt(y=oveHeaOccSet4_u), activate(y=oveHeaOccSet4_activate)),
    oveRBCHeaSetNonOcc(      uExt(y=oveHeaNonOccSet4_u), activate(y=oveHeaNonOccSet4_activate)),
    oveRBCCooOccSet(      uExt(y=oveCooOccSet4_u), activate(y=oveCooOccSet4_activate)),
    oveRBCCooNonOccSet(      uExt(y=oveCooNonOccSet4_u), activate(y=oveCooNonOccSet4_activate)))))
    "Original model with overwrites"
    annotation (Placement(transformation(extent={{-62,-100},{64,100}})));

  annotation (uses(Modelica(version="3.2.3"), Buildings(version="8.0.0")),
      experiment(
      StopTime=31449600,
      Interval=60,
      __Dymola_Algorithm="Dassl"),
    Icon(coordinateSystem(extent={{-100,-120},{100,120}}), graphics={
        Rectangle(
          extent={{-28,50},{432,-654}},
          lineColor={0,0,0},
          fillColor={28,108,200},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-22,-132},{424,-464}},
          lineColor={215,215,215},
          fillColor={175,175,175},
          fillPattern=FillPattern.Solid,
          lineThickness=1),
        Bitmap(
          extent={{-4,-506},{408,-94}},
          imageSource="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"
               + "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",
          fileName="modelica://wrapped/../../../../../../Pictures/Screenshot from 2021-02-11 15-49-58.png"),
        Rectangle(
          extent={{-20,32},{422,-114}},
          lineColor={215,215,215},
          lineThickness=1,
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Bitmap(extent={{-6,-108},{124,22}},
          imageSource=
              "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",

          fileName=
              "modelica://wrapped/../../../../../../../Pictures/Screenshot from 2021-02-11 15-58-21.png"),
        Text(
          extent={{142,32},{398,-104}},
          lineColor={0,0,0},
          lineThickness=1,
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid,
          textString="SoEP",
          textStyle={TextStyle.Bold}),
        Rectangle(
          extent={{-20,-482},{424,-642}},
          lineColor={215,215,215},
          lineThickness=1,
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-12,-478},{424,-642}},
          lineColor={0,0,0},
          lineThickness=1,
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid,
          textStyle={TextStyle.Bold},
          textString="Small Office
Building")}),
    Diagram(coordinateSystem(extent={{-100,-120},{100,120}})));

end wrapped;
