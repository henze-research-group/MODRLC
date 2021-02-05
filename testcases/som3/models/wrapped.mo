within ;
model wrapped "Wrapped model"
model SOM3 "Spawn replica of the Reference Small Office Building"

  // User input //
  String idfPat = "RefBldgSmallOfficeNew2004.idf";         // insert .idf file path
  String weaPat = "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw";         // insert  .mos file path

  //Parameters//

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
      T_start=288.75,
      nPorts=2) "\"Core zone\""
    annotation (Placement(transformation(extent={{54,64},{94,104}})));

    // Fluids - non HVAC //
  Buildings.Fluid.Sources.Outside Outside(redeclare final package Medium = Medium,
      nPorts=10)
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

        Boolean isOcc( start= false) "Schedule: occupied or non-occupied";
        Real day "Day of the week (1: Mon, 7:Sun)";
        Real hou "Hour of the day (24-hour format)";
        parameter Real staOcc = 8 "Start of day (24-hour)";
        parameter Real stoOcc = 18 "End of day (24-hour)";    // staOcc and stoOcc are currently fixed (the RefBldgSmallOffice case has a simple schedule)

          //Setpoints//

        parameter Real heaOccSet = 273.15 + 21 "Heating setpoint for occupied mode";
        parameter Real heaNonOccSet = 273.15 + 15.6 "Heating setpoint for non occupied mode";
        Real heaSet( start= 273.15 + 15.6) "Current heating setpoint";
        Real ploHeaSet(  start= 273.15 + 15.6) "plotting utility";
        Boolean neeHea( start= false) "True if the zone needs heating";
        parameter Real maxRH = 0.5 "Relative Humidity setpoint";
        parameter Real minOACCOpeTemp = 273.15 "Minimum outside air temperature for cooling coil operation";

        parameter Real cooOccSet = 273.15 + 24 "Cooling setpoint for occupied mode";
        parameter Real cooNonOccSet = 273.15 + 26.7 "Cooling setpoint for non occupied mode";
        Real cooSet( start= 273.15 + 26.7) "Current cooling setpoint";
        Real ploCooSet(  start= 273.15 + 26.7) "plotting utility";
        Boolean neeCoo( start= false);
        Real setpoint( start= 273.15 + 21) "Current setpoint";

        parameter Real fanOccSet = 0.44 "Fan volumetric flow rate when operating (m3/s)";
        parameter Real fanMinVFR = 0.01 "Fan minimum volumetic flow rate (m3/s)";
        Real fanSet( start= fanMinVFR) "Fan setpoint (m3/s)";

        parameter Real damSetOcc = 0.3 "Mixing box OA volumetric flow rate - occupied mode (m3/s)";
        parameter Real damSetNonOcc = 0.08 "Minimum OA volumetric flow rate (m3/s)";
        parameter Real minOA = 0.08 "Minimum OA fraction (m3/s)";
        Real damSet( start= 0.08) "OA fraction Setpoint (m3/s)";

          //Controls//

        parameter Real heaK = 0.5 "Proportional term for the heater command";
        parameter Real heaTi = 200 "Derivative term for the heater command";

        parameter Real fanK = 0.1 "Proportional term for the fan command";
        parameter Real fanTi = 60 "Derivative term for the fan command";

        parameter Real damK = 0.1 "Proportional term for the mixing box command";
        parameter Real damTi = 100 "Derivative term for the mixing box command";

        //parameter Real timShoCyc = 600 "Time constant for short cycling control (seconds)";
        //Boolean timRes "timer reset";

        // Inputs/Outputs//

        Modelica.Blocks.Interfaces.RealInput senTemRet annotation (Placement(
              transformation(extent={{-442,-4},{-402,36}}), iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-128,28})));
        Modelica.Blocks.Interfaces.RealOutput outDamSet annotation (Placement(
              transformation(extent={{154,34},{192,72}}), iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={129,-69})));
        Modelica.Blocks.Interfaces.RealOutput outHeaSet annotation (Placement(
              transformation(extent={{154,-2},{192,36}}), iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={129,83})));

        // Control components //

        Buildings.Controls.Continuous.LimPID heaPID(
          controllerType=Modelica.Blocks.Types.SimpleController.PI,
          k=heaK,
          Ti=heaTi,
          yMin = 0,
          yMax = 1)
          "P, PI or PID control of the heater command. As per DOE Ref Small Office Building"
          annotation (Placement(transformation(extent={{-378,248},{-358,268}})));

        Buildings.Controls.Continuous.LimPID fanPID(
          controllerType=Modelica.Blocks.Types.SimpleController.PI,
          k=fanK,
          Ti=fanTi,
          reverseActing=true)
          "P, PI or PID control of the fan command. Used to maintain constant V with a MFR-controlled fan model"
          annotation (Placement(transformation(extent={{-302,262},{-282,282}})));

        Buildings.Controls.Continuous.LimPID damPID(
          controllerType=Modelica.Blocks.Types.SimpleController.PI,
          k=damK,
          Ti=damTi,
          yMin = 0,
          yMax = 1)
          "P, PI or PID control of the mixing box command."
          annotation (Placement(transformation(extent={{-360,174},{-340,194}})));

        //Buildings.Controls.OBC.CDL.Logical.TimerAccumulating timerShortCycling(t=timShoCyc)
        //  annotation (Placement(transformation(extent={{32,4},{52,24}})));

        Modelica.Blocks.Interfaces.RealOutput outCCSet annotation (Placement(
              transformation(extent={{154,-42},{192,-4}}),iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={129,35})));
        Modelica.Blocks.Interfaces.RealInput senFanVFR annotation (Placement(
              transformation(extent={{-442,-40},{-402,0}}),   iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-128,-28})));
        Modelica.Blocks.Interfaces.RealOutput outFanSet
                                                       annotation (Placement(
              transformation(extent={{154,-78},{192,-40}}),
                                                          iconTransformation(
              extent={{-19,-19},{19,19}},
              rotation=0,
              origin={129,-13})));
        Modelica.Blocks.Interfaces.RealInput senDamVFR annotation (Placement(
              transformation(extent={{-440,-72},{-400,-32}}),  iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-128,-78})));
        Modelica.Blocks.Interfaces.RealInput senTemOut annotation (Placement(
              transformation(extent={{-442,28},{-402,68}}), iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-128,80})));

        Modelica.Blocks.Sources.RealExpression rea1(y=heaSet)
          annotation (Placement(transformation(extent={{-418,248},{-398,268}})));
        Modelica.Blocks.Sources.RealExpression rea2(y=senTemRet)
          annotation (Placement(transformation(extent={{-406,228},{-386,248}})));
        Modelica.Blocks.Sources.RealExpression rea3(y=fanSet)
          annotation (Placement(transformation(extent={{-334,262},{-314,282}})));
        Modelica.Blocks.Sources.RealExpression rea4(y=senFanVFR)
          annotation (Placement(transformation(extent={{-314,236},{-294,256}})));
        Modelica.Blocks.Sources.RealExpression rea5(y=damSet)
          annotation (Placement(transformation(extent={{-390,174},{-370,194}})));
        Modelica.Blocks.Sources.RealExpression rea6(y=senDamVFR)
          annotation (Placement(transformation(extent={{-372,152},{-352,172}})));
        //Modelica.Blocks.Sources.BooleanExpression boo1(y=timRes)
        //  annotation (Placement(transformation(extent={{-80,4},{-60,24}})));

        Modelica.Blocks.Interfaces.RealInput senHRRet annotation (Placement(
              transformation(extent={{-440,-104},{-400,-64}}),
              iconTransformation(
              extent={{-20,-20},{20,20}},
              rotation=0,
              origin={-128,-128})));
      equation

        //Setpoints - General//

        isOcc =  if (abs(day-7.0)>0.1 and hou>=staOcc and hou<stoOcc) then true else false; //if the day is not Sunday and the current hour is between staOcc and stoOcc, then the building is considered occupied
        heaSet = if isOcc then heaOccSet else heaNonOccSet;
        ploHeaSet = heaSet - 273.15;
        cooSet = if isOcc then cooOccSet else cooNonOccSet;
        ploCooSet = cooSet - 273.15;
        setpoint = (heaSet + cooSet) / 2.0;

        // Fan control: Constant volume, always on (??) (TODO: CHECK)

        if (neeHea or neeCoo or isOcc) then fanSet = fanOccSet; else fanSet = fanMinVFR; end if;
        outFanSet = fanPID.y;

        // Heating: modulating control (this is strange, but that is how the E+ model responds)
        if (senTemRet <= (heaSet-0.5)) then
          neeHea = true;
        elseif (senTemRet >= (heaSet+0.5)) then
          neeHea = false;
        else
          neeHea=true;
        end if;
        if (neeHea and senFanVFR >= fanSet*0.1) then outHeaSet = heaPID.y; else outHeaSet = 0; end if;// this is the BOPTEST override for the HC. Reads the PI control if inactive, otherwise overwrites the PI control with the external python controller

        // Cooling: On/Off operation with short cycling protection
        if ((senTemRet >= (cooSet + 0.5) or senHRRet >= maxRH) and senTemOut >= minOACCOpeTemp) then
          outCCSet = 1.0;
          neeCoo = true;
        elseif (senTemRet <= (cooSet - 0.5) or senTemOut < minOACCOpeTemp) then
          outCCSet = 0.0;
          neeCoo = false;
        else
          neeCoo = true;
          outCCSet = 1.0;
        end if;

        //if (neeCoo and pre(timerShortCycling.passed)) then 1.0 else 0.0; // SignalExchange blocks read Reals, not bools
        //timRes =  if (outCCSet+1.0 <= 1.0) then true else false;
        //timerShortCycling.reset = pre(timerShortCycling.passed);

        // Damper control: On/Off (strange too, but the RefBldgSmallOffice is done this way)
        if (senTemOut <= heaSet or senTemOut >= cooSet) then damSet = minOA; else damSet = setpoint; end if;
        outDamSet = damPID.y;

      connect(rea5.y, damPID.u_s)
        annotation (Line(points={{-369,184},{-362,184}},
                                                       color={0,0,127}));
      connect(rea6.y, damPID.u_m) annotation (Line(points={{-351,162},{-350,162},
                {-350,172}},        color={0,0,127}));
      connect(rea1.y, heaPID.u_s)
        annotation (Line(points={{-397,258},{-380,258}},
                                                     color={0,0,127}));
      connect(rea2.y, heaPID.u_m) annotation (Line(points={{-385,238},{-372,238},
                {-372,246},{-368,246}},
                                 color={0,0,127}));
      connect(rea3.y, fanPID.u_s)
        annotation (Line(points={{-313,272},{-304,272}},
                                                  color={0,0,127}));
      connect(rea4.y, fanPID.u_m) annotation (Line(points={{-293,246},{-293,253},
                {-292,253},{-292,260}},
                            color={0,0,127}));
        //connect(boo1.y, timerShortCycling.u)
        //  annotation (Line(points={{-59,14},{30,14}}, color={255,0,255}));
        annotation (Icon(graphics={Rectangle(extent={{-100,100},{100,-100}},
                  lineColor={28,108,200})}),Inline=true,GenerateEvents=true,
          Diagram(graphics={
              Rectangle(extent={{-172,-142},{218,-386}}, lineColor={28,108,200}),
              Text(
                extent={{116,-346},{216,-392}},
                lineColor={28,108,200},
                textString="Heating"),
              Text(
                extent={{118,-618},{218,-664}},
                lineColor={28,108,200},
                textString="Cooling"),
              Rectangle(extent={{-170,-414},{220,-658}}, lineColor={28,108,200}),
              Text(
                extent={{592,-478},{692,-524}},
                lineColor={28,108,200},
                textString="CV Fan controls"),
              Rectangle(extent={{304,-274},{694,-518}}, lineColor={28,108,200}),
              Text(
                extent={{-370,-618},{-270,-664}},
                lineColor={28,108,200},
                textString="Schedule"),
              Rectangle(extent={{-658,-414},{-268,-658}}, lineColor={28,108,200}),
              Text(
                extent={{120,-902},{220,-948}},
                lineColor={28,108,200},
                textString="Economizer"),
              Rectangle(extent={{-168,-698},{222,-942}}, lineColor={28,108,200})}));
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

      System3RBControls controls(day=day, hou=hour)   "CAV controller"
      annotation (Placement(transformation(extent={{-308,34},{-288,54}})));

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
            transformation(extent={{-434,-98},{-394,-58}}), iconTransformation(
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
      Modelica.Blocks.Logical.Switch switch1
        annotation (Placement(transformation(extent={{-296,-74},{-276,-54}})));
      Modelica.Blocks.Sources.RealExpression realExpression(y=280)
        annotation (Placement(transformation(extent={{-348,-106},{-328,-86}})));
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
            origin={38,-198})));
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
      connect(volSenSup.port_b, zonSupPort) annotation (Line(points={{366,-84},{406,
              -84},{406,-158},{446,-158}}, color={0,127,255}));
      connect(OAInlPor, volSenOA.port_a)
        annotation (Line(points={{-400,-200},{-316,-200}}, color={0,127,255}));
      connect(volSenOA.port_b, mixDam.port_Out) annotation (Line(points={{-296,-200},
              {-290,-200},{-290,-200.4},{-274,-200.4}}, color={0,127,255}));
      connect(controls.outHeaSet, oveHCSet.u) annotation (Line(points={{-285.1,52.3},
              {-240,52.3},{-240,52},{-228,52}}, color={0,0,127}));
      connect(controls.outCCSet, oveCCSet.u) annotation (Line(points={{-285.1,47.5},
              {-244,47.5},{-244,20},{-228,20}}, color={0,0,127}));
      connect(controls.outFanSet, oveFanSet.u) annotation (Line(points={{-285.1,42.7},
              {-250,42.7},{-250,-16},{-228,-16}}, color={0,0,127}));
      connect(controls.outDamSet, oveDamSet.u) annotation (Line(points={{-285.1,37.1},
              {-256,37.1},{-256,-52},{-228,-52}}, color={0,0,127}));
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
    connect(senTemRoo.y, controls.senTemRet) annotation (Line(points={{-395,6},{
              -378,6},{-378,46.8},{-310.8,46.8}}, color={0,0,127}));
      connect(controls.senTemOut, senTemOA) annotation (Line(points={{-310.8,52},
              {-382,52},{-382,-78},{-414,-78}},
                                          color={0,0,127}));
      connect(temSenRet, senTemRoo.u) annotation (Line(points={{-414,-118},{-418,
              -118},{-418,6},{-418,6}}, color={0,0,127}));
      connect(switch1.u1, senTemOA) annotation (Line(points={{-298,-56},{-346,
              -56},{-346,-78},{-414,-78}}, color={0,0,127}));
      connect(switch1.u2, sinSpeDX.on) annotation (Line(points={{-298,-64},{
              -310,-64},{-310,2},{-152,2},{-152,20},{-132,20},{-132,-61.8},{
              -100.9,-61.8}}, color={255,0,255}));
      connect(switch1.y, sinSpeDX.TConIn) annotation (Line(points={{-275,-64},{
              -188,-64},{-188,-76.3},{-100.9,-76.3}}, color={0,0,127}));
      connect(realExpression.y, switch1.u3) annotation (Line(points={{-327,-96},
              {-312,-96},{-312,-72},{-298,-72}}, color={0,0,127}));
      connect(senRelHum.phi, senRelHumOut.u) annotation (Line(points={{89.9,
              -249},{70.05,-249},{70.05,-198},{50,-198}},
                                                    color={0,0,127}));
      connect(senRelHumOut.y, controls.senHRRet) annotation (Line(points={{27,-198},
              {-162,-198},{-162,-130},{-352,-130},{-352,31.2},{-310.8,31.2}},
            color={0,0,127}));
      connect(senRelHum.port_b, mixDam.port_Ret) annotation (Line(points={{80,
              -238},{-66,-238},{-66,-237.6},{-212,-237.6}}, color={0,127,255}));
      connect(senRelHum.port_a, zonRetPor) annotation (Line(points={{100,-238},
              {276,-238},{276,-238},{452,-238}}, color={0,127,255}));
      connect(volSenOA.V_flow, senVolOA.u) annotation (Line(points={{-306,-189},
              {-306,-174},{-324,-174}}, color={0,0,127}));
      connect(senVolOA.y, controls.senDamVFR) annotation (Line(points={{-347,-174},
              {-370,-174},{-370,36.2},{-310.8,36.2}}, color={0,0,127}));
      connect(volSenSup.V_flow, senVolSup.u) annotation (Line(points={{356,-73},
              {356,-64},{312,-64},{312,-156},{-262,-156}}, color={0,0,127}));
      connect(senVolSup.y, controls.senFanVFR) annotation (Line(points={{-285,-156},
              {-290,-156},{-290,-154},{-360,-154},{-360,41.2},{-310.8,41.2}},
            color={0,0,127}));
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
  Buildings.Utilities.Time.CalendarTime calTim(zerTim=Buildings.Utilities.Time.Types.ZeroTime.NY2017,
      yearRef=2017) "Calendar Time"
    annotation (Placement(transformation(extent={{-268,136},{-236,168}})));
  ASHRAESystem3 HVAC(heaNomPow = 14035.23, CCNomPow = -8607.92) "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-14},{-42,16}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal
    annotation (Placement(transformation(extent={{-206,152},{-186,172}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal1
    annotation (Placement(transformation(extent={{-206,130},{-186,150}})));
  Modelica.Blocks.Routing.Multiplex3 mul "Multiplex for gains"
    annotation (Placement(transformation(extent={{-30,84},{-10,104}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k=0) "Convective heat gain"
    annotation (Placement(transformation(extent={{-82,84},{-62,104}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k=0) "Radiative heat gain"
    annotation (Placement(transformation(extent={{-82,124},{-62,144}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k=0) "Latent heat gain"
    annotation (Placement(transformation(extent={{-82,52},{-62,72}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
        transformation(extent={{-202,58},{-162,98}}), iconTransformation(extent=
           {{-352,68},{-332,88}})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow(u(min=0.0, max=15000.0, unit="W"), description=
          "Core Heating Coil Power",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"Core heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={120,-10})));
  ASHRAESystem3 HVAC1(heaNomPow = 11316.80, CCNomPow = -6909.58)   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-94},{-40,-64}})));
  ASHRAESystem3 HVAC2(heaNomPow = 9873.02, CCNomPow = -6137.71)   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-184},{-40,-154}})));
  ASHRAESystem3 HVAC3(heaNomPow = 11587.62, CCNomPow = -7081.44)   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-272},{-42,-242}})));
  ASHRAESystem3 HVAC4(heaNomPow = 9691.66, CCNomPow = -6779.76)   "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-350},{-40,-320}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone attZon(
      zoneName="Attic",
      redeclare final package Medium = Medium,
      nPorts=2) "\"Attic\""
      annotation (Placement(transformation(extent={{54,126},{94,166}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon1(
      zoneName="Perimeter_ZN_1",
      redeclare final package Medium = Medium,
      T_start=288.75,
      nPorts=2) "Perimeter zone 1"
      annotation (Placement(transformation(extent={{54,-94},{94,-54}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon2(
      zoneName="Perimeter_ZN_2",
      redeclare final package Medium = Medium,
      T_start=288.75,
      nPorts=2) "Perimeter zone 2"
      annotation (Placement(transformation(extent={{54,-184},{94,-144}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon3(
      zoneName="Perimeter_ZN_3",
      redeclare final package Medium = Medium,
      T_start=288.75,
      nPorts=2) "Perimeter zone 3"
      annotation (Placement(transformation(extent={{52,-274},{92,-234}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon4(
      zoneName="Perimeter_ZN_4",
      redeclare final package Medium = Medium,
      T_start=288.75,
      nPorts=2) "Perimeter zone 4"
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
          origin={-152,190})));
    Modelica.Blocks.Math.MultiSum multiSum(nu=3)
      annotation (Placement(transformation(extent={{202,-376},{214,-364}})));
    Modelica.Blocks.Math.MultiSum multiSum2(nu=3)
      annotation (Placement(transformation(extent={{212,-274},{224,-262}})));
    Modelica.Blocks.Math.MultiSum multiSum3(nu=3)
      annotation (Placement(transformation(extent={{216,-190},{228,-178}})));
    Modelica.Blocks.Math.MultiSum multiSum4(nu=3)
      annotation (Placement(transformation(extent={{214,-96},{226,-84}})));
    Modelica.Blocks.Math.MultiSum multiSum5(nu=3)
      annotation (Placement(transformation(extent={{192,-8},{204,4}})));
Buildings.Utilities.IO.SignalExchange.Read senPowCor(
      u(min=0.0,
        max=25000.0,
        unit="W"),
      description="Core AHU Power demand",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Core zone AHU power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={236,-2})));
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
          origin={266,-94})));
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
          origin={270,-186})));
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
          origin={274,-270})));
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
          origin={284,-368})));
equation

  connect(calTim.hour, integerToReal.u) annotation (Line(points={{-234.4,162.24},
          {-216.2,162.24},{-216.2,162},{-208,162}}, color={255,127,0}));
  connect(integerToReal.y, HVAC.hour) annotation (Line(points={{-185,162},{-130,
            162},{-130,-11.125},{-96.4372,-11.125}},    color={0,0,127}));
  connect(HVAC.day, integerToReal1.y) annotation (Line(points={{-96.4372,-6.5},{
            -134,-6.5},{-134,140},{-185,140}},color={0,0,127}));
  connect(HVAC.zonSupPort, corZon.ports[1]) annotation (Line(points={{-30.9302,20.375},
            {72.5349,20.375},{72.5349,64.9},{72,64.9}},       color={0,127,255}));
  connect(HVAC.zonRetPor, corZon.ports[2]) annotation (Line(points={{-30.8,4.125},
            {76.6,4.125},{76.6,64.9},{76,64.9}},
                                               color={0,127,255}));
  connect(HVAC.OAInlPor, Outside.ports[1]) annotation (Line(points={{-97.3488,20.375},
            {-144,20.375},{-144,11.6},{-184,11.6}},     color={0,127,255}));
  connect(HVAC.OAOutPor, Outside.ports[2]) annotation (Line(points={{-97.3488,4},
            {-140,4},{-140,10.8},{-184,10.8}},
                                           color={0,127,255}));
  connect(mul.u3[1],qLatGai_flow. y) annotation (Line(points={{-32,87},{-42,87},
            {-42,62},{-61,62}}, color={0,0,127}));
  connect(qConGai_flow.y,mul. u2[1]) annotation (Line(
      points={{-61,94},{-32,94}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(qRadGai_flow.y,mul. u1[1]) annotation (Line(
      points={{-61,134},{-42,134},{-42,101},{-32,101}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(mul.y, corZon.qGai_flow) annotation (Line(points={{-9,94},{52,94}},
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
    connect(corZon.TAir, HVAC.temSenRet) annotation (Line(points={{95,97.8},{31.5,
            97.8},{31.5,24.625},{-33.014,24.625}}, color={0,0,127}));
    connect(perZon1.qGai_flow, mul.y) annotation (Line(points={{52,-64},{52,-62},
            {46,-62},{46,94},{-9,94}}, color={0,0,127}));
    connect(perZon2.qGai_flow, mul.y) annotation (Line(points={{52,-154},{36,
            -154},{36,94},{-9,94}}, color={0,0,127}));
    connect(perZon3.qGai_flow, mul.y) annotation (Line(points={{50,-244},{22,
            -244},{22,94},{-9,94}}, color={0,0,127}));
    connect(perZon4.qGai_flow, mul.y) annotation (Line(points={{50,-322},{12,
            -322},{12,94},{-9,94}}, color={0,0,127}));
    connect(HVAC1.OAInlPor, Outside.ports[3]) annotation (Line(points={{-95.3488,
            -59.625},{-132,-59.625},{-132,-60},{-144,-60},{-144,8},{-184,8},{-184,
            10}},               color={0,127,255}));
    connect(HVAC1.OAOutPor, Outside.ports[4]) annotation (Line(points={{-95.3488,
            -76},{-100,-76},{-100,-74},{-146,-74},{-146,6},{-180,6},{-180,9.2},{
            -184,9.2}},            color={0,127,255}));
    connect(HVAC2.OAInlPor, Outside.ports[5]) annotation (Line(points={{-95.3488,
            -149.625},{-95.3488,-150},{-150,-150},{-150,8.4},{-184,8.4}},
          color={0,127,255}));
    connect(HVAC2.OAOutPor, Outside.ports[6]) annotation (Line(points={{-95.3488,
            -166},{-154,-166},{-154,7.6},{-184,7.6}},          color={0,127,255}));
    connect(HVAC3.OAInlPor, Outside.ports[7]) annotation (Line(points={{-97.3488,
            -237.625},{-160,-237.625},{-160,6.8},{-184,6.8}},          color={0,
            127,255}));
    connect(HVAC3.OAOutPor, Outside.ports[8]) annotation (Line(points={{-97.3488,
            -254},{-164,-254},{-164,6},{-184,6}},          color={0,127,255}));
    connect(HVAC4.OAInlPor, Outside.ports[9]) annotation (Line(points={{-95.3488,
            -315.625},{-168,-315.625},{-168,5.2},{-184,5.2}},          color={0,
            127,255}));
    connect(HVAC4.OAOutPor, Outside.ports[10]) annotation (Line(points={{-95.3488,
            -332},{-172,-332},{-172,4.4},{-184,4.4}},          color={0,127,255}));
    connect(HVAC4.zonSupPort, perZon4.ports[1]) annotation (Line(points={{-28.9302,
            -315.625},{10,-315.625},{10,-360},{70,-360},{70,-351.1}},
          color={0,127,255}));
    connect(HVAC4.zonRetPor, perZon4.ports[2]) annotation (Line(points={{-28.8,
            -331.875},{0,-331.875},{0,-366},{74,-366},{74,-351.1}}, color={0,
            127,255}));
    connect(HVAC3.zonSupPort, perZon3.ports[1]) annotation (Line(points={{-30.9302,
            -237.625},{8,-237.625},{8,-278},{70,-278},{70,-273.1}},
          color={0,127,255}));
    connect(HVAC3.zonRetPor, perZon3.ports[2]) annotation (Line(points={{-30.8,-253.875},
            {-30.8,-254},{2,-254},{2,-282},{74,-282},{74,-273.1}},
          color={0,127,255}));
    connect(HVAC2.zonSupPort, perZon2.ports[1]) annotation (Line(points={{-28.9302,
            -149.625},{2,-149.625},{2,-190},{72,-190},{72,-183.1}},
          color={0,127,255}));
    connect(HVAC2.zonRetPor, perZon2.ports[2]) annotation (Line(points={{-28.8,-165.875},
            {-2,-165.875},{-2,-198},{76,-198},{76,-183.1}},           color={0,
            127,255}));
    connect(HVAC1.zonSupPort, perZon1.ports[1]) annotation (Line(points={{-28.9302,
            -59.625},{6,-59.625},{6,-98},{72,-98},{72,-93.1}},          color={
            0,127,255}));
    connect(HVAC1.zonRetPor, perZon1.ports[2]) annotation (Line(points={{-28.8,-75.875},
            {0,-75.875},{0,-106},{76,-106},{76,-93.1}},          color={0,127,
            255}));
    connect(perZon1.TAir, HVAC1.temSenRet) annotation (Line(points={{95,-60.2},{
            100,-60.2},{100,-52},{-31.014,-52},{-31.014,-55.375}},  color={0,0,
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
    connect(attZon.qGai_flow, mul.y) annotation (Line(points={{52,156},{4,156},
            {4,94},{-9,94}}, color={0,0,127}));
    connect(HVAC1.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,-81},
            {-140,-81},{-140,-1},{-96.5674,-1}},      color={0,0,127}));
    connect(HVAC2.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,-171},
            {-140,-171},{-140,-1},{-96.5674,-1}},       color={0,0,127}));
    connect(HVAC3.senTemOA, HVAC.senTemOA) annotation (Line(points={{-96.5674,-259},
            {-140,-259},{-140,-1},{-96.5674,-1}},       color={0,0,127}));
    connect(HVAC4.senTemOA, HVAC.senTemOA) annotation (Line(points={{-94.5674,-337},
            {-118,-337},{-118,-338},{-140,-338},{-140,-1},{-96.5674,-1}},
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
    connect(senHeaPow3.u, HVAC3.heaPowDem) annotation (Line(points={{152,-274},{
            142,-274},{142,-290},{-49.0326,-290},{-49.0326,-273.5}},  color={0,
            0,127}));
    connect(senFanPow3.u, HVAC3.fanPowDem) annotation (Line(points={{152,-304},{
            142,-304},{142,-294},{-55.2837,-294},{-55.2837,-273.5}}, color={0,0,
            127}));
    connect(senCCPow3.u, HVAC3.cooPowDem) annotation (Line(points={{152,-244},{138,
            -244},{138,-284},{-42.1302,-284},{-42.1302,-273.5}}, color={0,0,127}));
    connect(senHeaPow4.u, HVAC4.heaPowDem) annotation (Line(points={{120,-376},{
            110,-376},{110,-386},{-47.0326,-386},{-47.0326,-351.5}},  color={0,
            0,127}));
    connect(senCCPow4.u, HVAC4.cooPowDem) annotation (Line(points={{120,-346},{106,
            -346},{106,-380},{-40.1302,-380},{-40.1302,-351.5}}, color={0,0,127}));
    connect(senFanPow4.u, HVAC4.fanPowDem) annotation (Line(points={{120,-406},{
            116,-406},{116,-390},{-53.2837,-390},{-53.2837,-351.5}}, color={0,0,
            127}));
    connect(senCCPow2.u, HVAC2.cooPowDem) annotation (Line(points={{124,-154},{100,
            -154},{100,-204},{-40.1302,-204},{-40.1302,-185.5}}, color={0,0,127}));
    connect(senHeaPow2.u, HVAC2.heaPowDem) annotation (Line(points={{124,-182},{
            104,-182},{104,-208},{-47.0326,-208},{-47.0326,-185.5}},  color={0,
            0,127}));
    connect(senFanPow2.u, HVAC2.fanPowDem) annotation (Line(points={{124,-214},{
            -53.2837,-214},{-53.2837,-185.5}}, color={0,0,127}));
    connect(senCCPow1.u, HVAC1.cooPowDem) annotation (Line(points={{154,-60},{106,
            -60},{106,-112},{-40.1302,-112},{-40.1302,-95.5}}, color={0,0,127}));
    connect(senHeaPow1.u, HVAC1.heaPowDem) annotation (Line(points={{154,-88},{114,
            -88},{114,-118},{-47.0326,-118},{-47.0326,-95.5}},     color={0,0,
            127}));
    connect(senFanPow1.u, HVAC1.fanPowDem) annotation (Line(points={{154,-120},{
            122,-120},{122,-124},{-53.2837,-124},{-53.2837,-95.5}}, color={0,0,127}));
    connect(senHeaPow.u, HVAC.heaPowDem) annotation (Line(points={{108,-10},{98,
            -10},{98,-24},{-49.0326,-24},{-49.0326,-15.5}},    color={0,0,127}));
    connect(senCCPow.u, HVAC.cooPowDem) annotation (Line(points={{110,20},{94,20},
            {94,-20},{-42.1302,-20},{-42.1302,-15.5}}, color={0,0,127}));
    connect(senFanPow.u, HVAC.fanPowDem) annotation (Line(points={{110,-40},{100,
            -40},{100,-28},{-55.2837,-28},{-55.2837,-15.5}}, color={0,0,127}));
  connect(senTemOA.u, HVAC.senTemOA) annotation (Line(points={{136,-508},{-140,-508},
            {-140,-1},{-96.5674,-1}},
                                    color={0,0,127}));
    connect(calTim.weekDay, integerToReal1.u) annotation (Line(points={{-234.4,145.6},
            {-221.2,145.6},{-221.2,140},{-208,140}}, color={255,127,0}));
    connect(calTim.minute, senMin.u) annotation (Line(points={{-234.4,166.4},{-210,
            166.4},{-210,190},{-164,190}}, color={0,0,127}));
    connect(senCCPow4.y, multiSum.u[1]) annotation (Line(points={{143,-346},{170,
            -346},{170,-367.2},{202,-367.2}}, color={0,0,127}));
    connect(senHeaPow4.y, multiSum.u[2]) annotation (Line(points={{143,-376},{150,
            -376},{150,-380},{186,-380},{186,-370},{202,-370}}, color={0,0,127}));
    connect(senFanPow4.y, multiSum.u[3]) annotation (Line(points={{143,-406},{152,
            -406},{152,-408},{194,-408},{194,-372.8},{202,-372.8}}, color={0,0,127}));
    connect(senCCPow3.y, multiSum2.u[1]) annotation (Line(points={{175,-244},{198,
            -244},{198,-265.2},{212,-265.2}}, color={0,0,127}));
    connect(senHeaPow3.y, multiSum2.u[2]) annotation (Line(points={{175,-274},{192,
            -274},{192,-268},{212,-268}}, color={0,0,127}));
    connect(senFanPow3.y, multiSum2.u[3]) annotation (Line(points={{175,-304},{178,
            -304},{178,-306},{198,-306},{198,-270.8},{212,-270.8}}, color={0,0,127}));
    connect(senCCPow2.y, multiSum3.u[1]) annotation (Line(points={{147,-154},{154,
            -154},{154,-156},{192,-156},{192,-181.2},{216,-181.2}}, color={0,0,127}));
    connect(senHeaPow2.y, multiSum3.u[2]) annotation (Line(points={{147,-182},{192,
            -182},{192,-184},{216,-184}}, color={0,0,127}));
    connect(senFanPow2.y, multiSum3.u[3]) annotation (Line(points={{147,-214},{154,
            -214},{154,-216},{190,-216},{190,-186.8},{216,-186.8}}, color={0,0,127}));
    connect(senCCPow1.y, multiSum4.u[1]) annotation (Line(points={{177,-60},{186,
            -60},{186,-64},{200,-64},{200,-87.2},{214,-87.2}}, color={0,0,127}));
    connect(senHeaPow1.y, multiSum4.u[2]) annotation (Line(points={{177,-88},{192,
            -88},{192,-90},{214,-90}}, color={0,0,127}));
    connect(senFanPow1.y, multiSum4.u[3]) annotation (Line(points={{177,-120},{194,
            -120},{194,-92.8},{214,-92.8}}, color={0,0,127}));
    connect(senCCPow.y, multiSum5.u[1]) annotation (Line(points={{133,20},{142,20},
            {142,22},{166,22},{166,0.8},{192,0.8}}, color={0,0,127}));
    connect(senHeaPow.y, multiSum5.u[2]) annotation (Line(points={{131,-10},{160,
            -10},{160,-2},{192,-2}}, color={0,0,127}));
    connect(senFanPow.y, multiSum5.u[3]) annotation (Line(points={{133,-40},{138,
            -40},{138,-42},{152,-42},{152,-12},{192,-12},{192,-4.8}}, color={0,0,
            127}));
    connect(multiSum5.y, senPowCor.u)
      annotation (Line(points={{205.02,-2},{224,-2}}, color={0,0,127}));
    connect(multiSum4.y, senPowPer1.u) annotation (Line(points={{227.02,-90},{240,
            -90},{240,-94},{254,-94}}, color={0,0,127}));
    connect(multiSum3.y, senPowPer2.u) annotation (Line(points={{229.02,-184},{244,
            -184},{244,-186},{258,-186}}, color={0,0,127}));
    connect(multiSum2.y, senPowPer3.u) annotation (Line(points={{225.02,-268},{242,
            -268},{242,-270},{262,-270}}, color={0,0,127}));
    connect(multiSum.y, senPowPer4.u) annotation (Line(points={{215.02,-370},{244,
            -370},{244,-368},{272,-368}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-280,
              -500},{180,200}})),                                Diagram(
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
    oveFanSet(      uExt(y=oveVFRSet_u), activate(y=oveVFRSet_activate))),
    HVAC1(
    oveHCSet(      uExt(y=oveHCSet1_u), activate(y=oveHCSet1_activate)),
    oveCCSet(      uExt(y=oveCC1_u), activate(y=oveCC1_activate)),
    oveDamSet(      uExt(y=oveDSet1_u), activate(y=oveDSet1_activate)),
    oveFanSet(      uExt(y=oveVFRSet1_u), activate(y=oveVFRSet1_activate))),
    HVAC2(
    oveHCSet(      uExt(y=oveHCSet2_u), activate(y=oveHCSet2_activate)),
    oveCCSet(      uExt(y=oveCC2_u), activate(y=oveCC2_activate)),
    oveDamSet(      uExt(y=oveDSet2_u), activate(y=oveDSet2_activate)),
    oveFanSet(      uExt(y=oveVFRSet2_u), activate(y=oveVFRSet2_activate))),
    HVAC3(
    oveHCSet(      uExt(y=oveHCSet3_u), activate(y=oveHCSet3_activate)),
    oveCCSet(      uExt(y=oveCC3_u), activate(y=oveCC3_activate)),
    oveDamSet(      uExt(y=oveDSet3_u), activate(y=oveDSet3_activate)),
    oveFanSet(      uExt(y=oveVFRSet3_u), activate(y=oveVFRSet3_activate))),
    HVAC4(
    oveHCSet(      uExt(y=oveHCSet4_u), activate(y=oveHCSet4_activate)),
    oveCCSet(      uExt(y=oveCC4_u), activate(y=oveCC4_activate)),
    oveDamSet(      uExt(y=oveDSet4_u), activate(y=oveDSet4_activate)),
    oveFanSet(      uExt(y=oveVFRSet4_u), activate(y=oveVFRSet4_activate))))
    "Original model with overwrites";

  annotation (uses(Modelica(version="3.2.3"), Buildings(version="8.0.0")),
      experiment(
      StopTime=31557600,
      Interval=600,
      __Dymola_Algorithm="Dassl"));
end wrapped;
