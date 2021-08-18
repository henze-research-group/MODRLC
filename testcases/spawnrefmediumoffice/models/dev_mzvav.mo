within ;
model dev_mzvav "Development rig for the MZVAV system"

  package Medium = Buildings.Media.Air "Moist Air"; // Moist air

  model PackagedMZVAVReheat
  "Packaged MZVAV with electric reheat coil for the DOE Reference Medium Office Building"
  package Medium = Buildings.Media.Air;
  parameter Integer nZones = 5;
  parameter Real mFlowNom = 1;
  parameter Real dpNom = 50;
  parameter Integer numZon = 5;
  parameter Real sampleReheat = 120;

  parameter Real reheaNomPow1 = 1000;
  parameter Real reheaNomPow2 = 1000;
  parameter Real reheaNomPow3 = 1000;
  parameter Real reheaNomPow4 = 1000;
  parameter Real reheaNomPow5 = 1000;
  parameter Real heaNomPow = 10000;

  parameter Real tHeaOccSet = 273.15 + 21;
  parameter Real tHeaUnoSet = 273.15 + 15.6;
  parameter Real tCooOccSet = 273.15 + 24;
  parameter Real tCooUnoSet = 273.15 + 26.7;

  parameter Real CCNomPowS1 = -39656.37;
  parameter Real CCCOPS1 = 3.28;
  parameter Real CCSHRS1 = 0.8;
  parameter Real CCmass_flow_nomS1 = 3;
  parameter Real speS1 = 1200;

  parameter Real CCNomPowS2 = -118981.01;
  parameter Real CCCOPS2 = 3.23;
  parameter Real CCSHRS2 = 0.80;
  parameter Real CCmass_flow_nomS2 = 8.5;
  parameter Real speS2 = 1200*CCNomPowS2/CCNomPowS1;

  parameter Real ACore = 983.54;
  parameter Real AP1 = 207.34;
  parameter Real AP2 = 131.26;
  parameter Real AP3 = 207.34;
  parameter Real AP4 = 131.25;
  parameter Real VFRCore = 3.58;
  parameter Real VFRP1 = 0.940984;
  parameter Real VFRP2 = 0.958392;
  parameter Real VFRP3 = 0.594831;
  parameter Real VFRP4 = 1.11;

  parameter Real fanMaxVFR = 7.19;

  Modelica.Fluid.Interfaces.FluidPort_a vavOAinlet(redeclare package Medium =
          Medium)
    annotation (Placement(transformation(extent={{-210,54},{-190,74}})));
  Modelica.Fluid.Interfaces.FluidPort_b vavOAoutlet(redeclare package Medium =
          Medium)
    annotation (Placement(transformation(extent={{-212,166},{-192,186}})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u heaGas(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=heaNomPow) "Gas fired heating coil"
    annotation (Placement(transformation(extent={{54,54},{74,74}})));
  Buildings.Fluid.Actuators.Dampers.Exponential damOA(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) "Outside air damper"
    annotation (Placement(transformation(extent={{-114,54},{-94,74}})));
  Buildings.Fluid.Actuators.Dampers.Exponential damRet(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) "Return air damper" annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=270,
        origin={-36,122})));
  Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.MultiStage mulStaDX(
      datCoi(nSta=2, sta={
            Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.Stage(
            spe=speS1,
            nomVal=
              Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.NominalValues(
              Q_flow_nominal=CCNomPowS1,
              COP_nominal=CCCOPS1,
              SHR_nominal=CCSHRS1,
              m_flow_nominal=CCmass_flow_nomS1),
            perCur=
              Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.PerformanceCurve(
              capFunT={0.4136,0.03105,0,0.006952,-0.00021280,0},
              capFunFF={1,0,0},
              EIRFunT={1.1389,-0.04518,0.0014298,0.006044,0.0006745,-0.0012325},
              EIRFunFF={1,0,0},
              TConInMin=273.15 + 10,
              TConInMax=273.15 + 50.3,
              TEvaInMin=273.15 + 11.1,
              TEvaInMax=273.15 + 29.4,
              ffMin=0,
              ffMax=1.5)),
            Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.Stage(
            spe=speS2,
            nomVal=
              Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.NominalValues(
              Q_flow_nominal=CCNomPowS2,
              COP_nominal=CCCOPS2,
              SHR_nominal=CCSHRS2,
              m_flow_nominal=CCmass_flow_nomS2),
            perCur=
              Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.Data.Generic.BaseClasses.PerformanceCurve(
              capFunT={0.52357,0.03478,0,-0.001915,-0.00010838,0},
              capFunFF={0.7685,0.2315,0},
              EIRFunT={0.9847,-0.04285,0.0013562,0.009934,0.0006398,-0.0011690},
              EIRFunFF={1.192,-0.1917,0},
              TConInMin=273.15 + 10,
              TConInMax=273.15 + 50.3,
              TEvaInMin=273.15 + 11.1,
              TEvaInMax=273.15 + 29.4,
              ffMin=0,
              ffMax=1.5))}),
      redeclare final package Medium = Medium,
    dp_nominal=dpNom)
    annotation (Placement(transformation(extent={{178,54},{198,74}})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolOut(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{-168,54},{-148,74}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemMix(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{0,54},{20,74}})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolSup(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{338,54},{358,74}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemSup(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{400,54},{420,74}})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec1(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=reheaNomPow1) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={494,148})));
  Buildings.Fluid.Movers.SpeedControlled_y fanVSD(redeclare package Medium =
        Medium,
      per(
        pressure(V_flow={0,2*fanMaxVFR}, dp={2*1109.648,0}),
        use_powerCharacteristic=false,
        hydraulicEfficiency(V_flow={fanMaxVFR}, eta={0.5915}),
        motorEfficiency(V_flow={fanMaxVFR}, eta={0.91}),
        motorCooledByFluid=true),
      inputType=Buildings.Fluid.Types.InputType.Continuous)
    annotation (Placement(transformation(extent={{270,54},{290,74}})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec2(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=reheaNomPow2) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={668,148})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec3(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=reheaNomPow3) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,148})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec4(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=reheaNomPow4) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,146})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec5(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom,
    Q_flow_nominal=reheaNomPow5) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={1114,144})));
  Buildings.Fluid.Actuators.Dampers.PressureIndependent damCore(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={494,188})));
  Buildings.Fluid.Actuators.Dampers.PressureIndependent damPerimeter1(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={668,188})));
  Buildings.Fluid.Actuators.Dampers.PressureIndependent damPerimeter2(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,190})));
  Buildings.Fluid.Actuators.Dampers.PressureIndependent damPerimeter3(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,190})));
  Buildings.Fluid.Actuators.Dampers.PressureIndependent damPerimeter4(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dpDamper_nominal=dpNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={1112,190})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolCore(redeclare package Medium =
          Medium,                                   m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={494,228})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolPerimeter1(redeclare package
        Medium = Medium,                                  m_flow_nominal=
        mFlowNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={668,228})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolPerimeter2(redeclare package
        Medium = Medium,                                  m_flow_nominal=
        mFlowNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,228})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolPerimeter3(redeclare package
        Medium = Medium,                                  m_flow_nominal=
        mFlowNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,228})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolPerimeter4(redeclare package
        Medium = Medium,                                  m_flow_nominal=
        mFlowNom) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={1112,228})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemCore(redeclare package Medium =
               Medium, m_flow_nominal=mFlowNom) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={494,266})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemPerimeter1(redeclare package
        Medium=Medium, m_flow_nominal=mFlowNom) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={668,266})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemPerimeter2(redeclare package
        Medium=Medium, m_flow_nominal=mFlowNom) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,266})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemPerimeter3(redeclare package
        Medium=Medium, m_flow_nominal=mFlowNom) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,268})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemPerimeter4(redeclare package
        Medium=Medium, m_flow_nominal=mFlowNom) annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={1112,266})));
  Modelica.Fluid.Interfaces.FluidPort_b vavCoreOut(redeclare package Medium =
        Medium) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={492,320}), iconTransformation(
          extent={{-10,-10},{10,10}},
          rotation=90,
          origin={280,658})));
  Modelica.Fluid.Interfaces.FluidPort_b vavPerimeter1Out(redeclare package Medium =
               Medium) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={666,320}), iconTransformation(
          extent={{-10,-10},{10,10}},
          rotation=90,
          origin={492,658})));
  Modelica.Fluid.Interfaces.FluidPort_b vavPerimeter2Out(redeclare package Medium =
               Medium) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,320}), iconTransformation(
          extent={{-10,-10},{10,10}},
          rotation=90,
          origin={706,662})));
  Modelica.Fluid.Interfaces.FluidPort_b vavPerimeter3Out(redeclare package Medium =
               Medium) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,320}), iconTransformation(
          extent={{-10,-10},{10,10}},
          rotation=90,
          origin={926,658})));
  Modelica.Fluid.Interfaces.FluidPort_b vavPerimeter4Out(redeclare package Medium =
               Medium) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={1112,322}), iconTransformation(
          extent={{-10,-10},{10,10}},
          rotation=90,
          origin={1116,658})));
  Buildings.Fluid.FixedResistances.Junction splitterSupCore(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={494,64})));
  Buildings.Fluid.FixedResistances.Junction splitterSup1(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={666,64})));
  Buildings.Fluid.FixedResistances.Junction splitterSup2(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={824,64})));
  Buildings.Fluid.FixedResistances.Junction splitterSup3(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={966,64})));
  Modelica.Fluid.Interfaces.FluidPort_a vavReturnCore(redeclare package Medium =
        Medium)
    annotation (Placement(transformation(extent={{200,650},{220,670}}),
          iconTransformation(extent={{200,650},{220,670}})));
  Modelica.Fluid.Interfaces.FluidPort_a vavReturnPerimeter1(redeclare package
        Medium=Medium)
    annotation (Placement(transformation(extent={{384,648},{404,668}}),
          iconTransformation(extent={{384,648},{404,668}})));
  Modelica.Fluid.Interfaces.FluidPort_a vavReturnPerimeter2(redeclare package
        Medium=Medium)
    annotation (Placement(transformation(extent={{624,654},{644,674}}),
          iconTransformation(extent={{624,654},{644,674}})));
  Modelica.Fluid.Interfaces.FluidPort_a vavReturnPerimeter3(redeclare package
        Medium=Medium)
    annotation (Placement(transformation(extent={{826,650},{846,670}}),
          iconTransformation(extent={{826,650},{846,670}})));
  Modelica.Fluid.Interfaces.FluidPort_a vavReturnPerimeter4(redeclare package
        Medium=Medium)
    annotation (Placement(transformation(extent={{1010,650},{1030,670}}),
          iconTransformation(extent={{1010,650},{1030,670}})));
  Buildings.Fluid.FixedResistances.Junction junctionReturn(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={398,360})));
  Buildings.Fluid.FixedResistances.Junction junctionReturn1(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={604,360})));
  Buildings.Fluid.FixedResistances.Junction junctionReturn2(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={770,360})));
  Buildings.Fluid.FixedResistances.Junction junctionReturn3(
    redeclare final package Medium = Medium,
    m_flow_nominal={0.5,0.5,0.5},
    dp_nominal={10,10,10})
                      annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={916,360})));
  Buildings.Fluid.Sensors.VolumeFlowRate senVolRet(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{258,350},{238,370}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTemRet(redeclare package Medium =
        Medium, m_flow_nominal=mFlowNom)
    annotation (Placement(transformation(extent={{202,350},{182,370}})));
  Buildings.Fluid.FixedResistances.PressureDrop resReturn(
    redeclare final package Medium = Medium,
    m_flow_nominal=mFlowNom,
    dp_nominal=dpNom)
    annotation (Placement(transformation(extent={{326,350},{306,370}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus zonSta[numZon](
    THeaSetOcc=tHeaOccSet,
      THeaSetUno=tHeaUnoSet,
    TCooSetOcc=tCooOccSet,
    TCooSetUno=tCooUnoSet)
    annotation (Placement(transformation(extent={{38,532},{58,560}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.GroupStatus groSta(numZon=
        nZones)
    annotation (Placement(transformation(extent={{112,524},{132,564}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSel(numZon=numZon)
    annotation (Placement(transformation(extent={{168,530},{188,562}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSet[numZon](have_occSen=false, have_winSen=false)
    annotation (Placement(transformation(extent={{200,468},{220,496}})));
  Modelica.Blocks.Interfaces.RealInput senTemRoom "Zone temperature, single"
    annotation (Placement(transformation(extent={{-244,612},{-204,652}})));
  Modelica.Blocks.Interfaces.RealOutput y
    annotation (Placement(transformation(extent={{-100,686},{-80,706}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant warmupCooldown[numZon](
      final k=fill(1800, numZon)) "Warm up and cool down time"
    annotation (Placement(transformation(extent={{-82,560},{-62,580}})));
  Buildings.Controls.OBC.CDL.Logical.Sources.Constant falSta[numZon](final k=
        fill(false, numZon))
    "All windows are closed, no zone has override switch"
    annotation (Placement(transformation(extent={{-82,600},{-62,620}})));
  Buildings.Controls.OBC.CDL.Routing.IntegerReplicator intRep(final nout=nZones)
    "All zones in same operation mode"
    annotation (Placement(transformation(extent={{180,504},{188,512}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.Controller terUniCon(
      samplePeriod=sampleReheat,
      V_flow_nominal=VFRCore,
      AFlo=ACore)
    annotation (Placement(transformation(extent={{410,212},{430,232}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.MultiZone.VAV.Controller conAHU(
        VPriSysMax_flow=7.5, peaSysPop=89.4)
    annotation (Placement(transformation(extent={{418,482},{498,626}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.MultiZone.VAV.SetPoints.OutdoorAirFlow.Zone
    zonOutAirSet[numZon](
      AFlo={ACore,AP1,AP2,AP3,AP4},
                         have_occSen=fill(false, numZon), have_winSen=fill(false,
        numZon),
      occDen=0.0538,
      minZonPriFlo={1.07,0.282295,0.287517,0.178449,0.334447})
    annotation (Placement(transformation(extent={{146,614},{166,634}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.MultiZone.VAV.SetPoints.OutdoorAirFlow.SumZone
    zonToSys(numZon=nZones)
    annotation (Placement(transformation(extent={{262,612},{282,632}})));
  Buildings.Controls.SetPoints.Table tab(table=[0.0,0.0; 0.1,1.0; 0.5,2.0],
      constantExtrapolation=true)
    annotation (Placement(transformation(extent={{558,508},{578,528}})));
  Buildings.Controls.OBC.CDL.Conversions.RealToInteger reaToInt
    annotation (Placement(transformation(extent={{594,508},{614,528}})));
  Buildings.Fluid.Sensors.RelativePressure dpDisSupFan(redeclare package Medium =
        Medium)  "Supply fan static discharge pressure" annotation (Placement(
        transformation(
        extent={{-10,10},{10,-10}},
        rotation=90,
        origin={302,90})));
  Modelica.Blocks.Interfaces.RealInput senTOut "Outside air temperature"
    annotation (Placement(transformation(extent={{-234,486},{-194,526}}),
          iconTransformation(extent={{-234,486},{-194,526}})));
  Buildings.Controls.OBC.CDL.Integers.Sources.Constant demLimLev[numZon](final
      k=fill(0, numZon)) "Demand limit level, assumes to be 0"
    annotation (Placement(transformation(extent={{-80,476},{-60,496}})));
  Buildings.Controls.OBC.CDL.Integers.MultiSum PZonResReq(nin=5)
    "Number of zone pressure requests"
    annotation (Placement(transformation(extent={{446,368},{466,388}})));
  Buildings.Controls.OBC.CDL.Integers.MultiSum TZonResReq(nin=5)
    "Number of zone temperature requests"
    annotation (Placement(transformation(extent={{446,404},{466,424}})));
  Modelica.Blocks.Routing.Multiplex5 VDis_flow
    "Air flow rate at the terminal boxes"
    annotation (Placement(transformation(extent={{140,384},{160,404}})));
  Modelica.Blocks.Routing.Multiplex5 TDis "Discharge air temperatures"
    annotation (Placement(transformation(extent={{140,424},{160,444}})));
  Buildings.Controls.OBC.CDL.Routing.BooleanReplicator booRep1(final nout=
        numZon)
    "Replicate signal whether the outdoor airflow is required"
    annotation (Placement(transformation(extent={{544,532},{564,552}})));
  Buildings.Controls.OBC.CDL.Routing.RealReplicator reaRep1(final nout=numZon)
    "Replicate design uncorrected minimum outdoor airflow setpoint"
    annotation (Placement(transformation(extent={{544,568},{564,588}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.Controller terUniCon1(
      samplePeriod=sampleReheat,
      V_flow_nominal=VFRP1,
      AFlo=AP1)
    annotation (Placement(transformation(extent={{598,210},{618,230}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.Controller terUniCon2(
      samplePeriod=sampleReheat,
      V_flow_nominal=VFRP2,
      AFlo=AP2)
    annotation (Placement(transformation(extent={{762,206},{782,226}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.Controller terUniCon3(
      samplePeriod=sampleReheat,
      V_flow_nominal=VFRP3,
      AFlo=AP3)
    annotation (Placement(transformation(extent={{902,196},{922,216}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.Controller terUniCon4(
      samplePeriod=sampleReheat,
      V_flow_nominal=VFRP4,
      AFlo=AP4)
    annotation (Placement(transformation(extent={{1054,192},{1074,212}})));
    Modelica.Blocks.Interfaces.RealVectorInput u[numZon]
      annotation (Placement(transformation(extent={{-238,572},{-198,612}})));
  Buildings.Controls.OBC.CDL.Routing.BooleanReplicator booRep2(final nout=numZon)
    "Replicate signal whether the outdoor airflow is required"
    annotation (Placement(transformation(extent={{-42,620},{-22,640}})));
  Buildings.Controls.OBC.CDL.Routing.RealReplicator reaRep2(final nout=numZon)
    "Replicate design uncorrected minimum outdoor airflow setpoint"
    annotation (Placement(transformation(extent={{-10,636},{10,656}})));
    Modelica.Blocks.Routing.DeMultiplex5 TRooAir(u(each unit="K", each
          displayUnit="degC")) "Demultiplex for room air temperature"
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=0,
          origin={170,236})));
    Buildings.Controls.SetPoints.OccupancySchedule occSchWeekdays(
      occupancy=3600*{30,46,54,70,78,94,102,118,126,142,150,161},
      firstEntryOccupied=true,
      period=7*24*3600)
      annotation (Placement(transformation(extent={{-106,636},{-86,656}})));
  equation
  connect(damRet.port_b, vavOAoutlet) annotation (Line(points={{-36,132},{-36,
          176},{-202,176}}, color={0,127,255}));
  connect(damOA.port_b, damRet.port_a)
    annotation (Line(points={{-94,64},{-36,64},{-36,112}}, color={0,127,255}));
  connect(heaGas.port_b, mulStaDX.port_a)
    annotation (Line(points={{74,64},{178,64}}, color={0,127,255}));
  connect(mulStaDX.port_b, fanVSD.port_a) annotation (Line(points={{198,64},{
          236.5,64},{236.5,64},{270,64}}, color={0,0,127}));
  connect(senTemMix.port_a, damRet.port_a)
    annotation (Line(points={{0,64},{-36,64},{-36,112}}, color={0,127,255}));
  connect(senTemMix.port_b, heaGas.port_a)
    annotation (Line(points={{20,64},{54,64}}, color={0,127,255}));
  connect(damOA.port_a, senVolOut.port_b)
    annotation (Line(points={{-114,64},{-148,64}}, color={0,127,255}));
  connect(senVolOut.port_a, vavOAinlet)
    annotation (Line(points={{-168,64},{-200,64}}, color={0,127,255}));
  connect(senVolSup.port_a, fanVSD.port_b)
    annotation (Line(points={{338,64},{290,64}}, color={0,127,255}));
  connect(senVolSup.port_b, senTemSup.port_a)
    annotation (Line(points={{358,64},{400,64}}, color={0,127,255}));
  connect(reheatElec1.port_b, damCore.port_a)
    annotation (Line(points={{494,158},{494,178}}, color={0,127,255}));
  connect(reheatElec2.port_b, damPerimeter1.port_a)
    annotation (Line(points={{668,158},{668,178}}, color={0,127,255}));
  connect(damPerimeter2.port_a, reheatElec3.port_b)
    annotation (Line(points={{826,180},{826,158}}, color={0,127,255}));
  connect(reheatElec4.port_b, damPerimeter3.port_a)
    annotation (Line(points={{968,156},{968,180}}, color={0,127,255}));
  connect(reheatElec5.port_b, damPerimeter4.port_a) annotation (Line(points={{
          1114,154},{1114,180},{1112,180}}, color={0,127,255}));
  connect(damCore.port_b, senVolCore.port_a)
    annotation (Line(points={{494,198},{494,218}}, color={0,127,255}));
  connect(damPerimeter1.port_b, senVolPerimeter1.port_a)
    annotation (Line(points={{668,198},{668,218}}, color={0,127,255}));
  connect(damPerimeter2.port_b, senVolPerimeter2.port_a)
    annotation (Line(points={{826,200},{826,218}}, color={0,127,255}));
  connect(damPerimeter3.port_b, senVolPerimeter3.port_a)
    annotation (Line(points={{968,200},{968,218}}, color={0,127,255}));
  connect(damPerimeter4.port_b, senVolPerimeter4.port_a)
    annotation (Line(points={{1112,200},{1112,218}}, color={0,127,255}));
  connect(senVolCore.port_b, senTemCore.port_a)
    annotation (Line(points={{494,238},{494,256}}, color={0,127,255}));
  connect(senVolPerimeter1.port_b, senTemPerimeter1.port_a)
    annotation (Line(points={{668,238},{668,256}}, color={0,127,255}));
  connect(senVolPerimeter2.port_b, senTemPerimeter2.port_a)
    annotation (Line(points={{826,238},{826,256}}, color={0,127,255}));
  connect(senVolPerimeter3.port_b, senTemPerimeter3.port_a)
    annotation (Line(points={{968,238},{968,258}}, color={0,127,255}));
  connect(senVolPerimeter4.port_b, senTemPerimeter4.port_a)
    annotation (Line(points={{1112,238},{1112,256}}, color={0,127,255}));
  connect(senTemCore.port_b, vavCoreOut) annotation (Line(points={{494,276},{
          494,298},{494,320},{492,320}}, color={0,127,255}));
  connect(senTemPerimeter1.port_b, vavPerimeter1Out) annotation (Line(points={{
          668,276},{668,320},{666,320}}, color={0,127,255}));
  connect(senTemPerimeter2.port_b, vavPerimeter2Out)
    annotation (Line(points={{826,276},{826,320}}, color={0,127,255}));
  connect(senTemPerimeter3.port_b, vavPerimeter3Out)
    annotation (Line(points={{968,278},{968,320}}, color={0,127,255}));
  connect(senTemPerimeter4.port_b, vavPerimeter4Out)
    annotation (Line(points={{1112,276},{1112,322}}, color={0,127,255}));
  connect(senTemSup.port_b, splitterSupCore.port_1)
    annotation (Line(points={{420,64},{484,64}}, color={0,127,255}));
  connect(splitterSupCore.port_3, reheatElec1.port_a)
    annotation (Line(points={{494,74},{494,138}}, color={0,127,255}));
  connect(splitterSupCore.port_2, splitterSup1.port_1)
    annotation (Line(points={{504,64},{656,64}}, color={0,127,255}));
  connect(reheatElec2.port_a, splitterSup1.port_3)
    annotation (Line(points={{668,138},{668,74},{666,74}}, color={0,127,255}));
  connect(splitterSup1.port_2, splitterSup2.port_1)
    annotation (Line(points={{676,64},{814,64}}, color={0,127,255}));
  connect(reheatElec3.port_a, splitterSup2.port_3)
    annotation (Line(points={{826,138},{826,74},{824,74}}, color={0,127,255}));
  connect(splitterSup2.port_2, splitterSup3.port_1)
    annotation (Line(points={{834,64},{956,64}}, color={0,127,255}));
  connect(reheatElec4.port_a, splitterSup3.port_3)
    annotation (Line(points={{968,136},{968,74},{966,74}}, color={0,127,255}));
  connect(splitterSup3.port_2, reheatElec5.port_a) annotation (Line(points={{
          976,64},{1114,64},{1114,134}}, color={0,127,255}));
  connect(junctionReturn1.port_3, vavReturnPerimeter1)
    annotation (Line(points={{604,370},{604,514},{604,658},{394,658}},
                                                   color={0,127,255}));
  connect(junctionReturn.port_3, vavReturnCore)
    annotation (Line(points={{398,370},{398,516},{398,660},{210,660}},
                                                   color={0,127,255}));
  connect(junctionReturn.port_1, junctionReturn1.port_2)
    annotation (Line(points={{408,360},{594,360}}, color={0,127,255}));
  connect(junctionReturn1.port_1, junctionReturn2.port_2)
    annotation (Line(points={{614,360},{760,360}}, color={0,127,255}));
  connect(junctionReturn2.port_1, junctionReturn3.port_2)
    annotation (Line(points={{780,360},{906,360}}, color={0,127,255}));
  connect(junctionReturn3.port_1, vavReturnPerimeter4) annotation (Line(points={{926,360},
            {1020,360},{1020,660}},          color={0,127,255}));
  connect(vavReturnPerimeter3, junctionReturn3.port_3)
    annotation (Line(points={{836,660},{836,516},{916,516},{916,370}},
                                                   color={0,127,255}));
  connect(vavReturnPerimeter2, junctionReturn2.port_3)
    annotation (Line(points={{634,664},{634,516},{770,516},{770,370}},
                                                   color={0,127,255}));
  connect(senVolRet.port_a, resReturn.port_b)
    annotation (Line(points={{258,360},{306,360}}, color={0,127,255}));
  connect(resReturn.port_a, junctionReturn.port_2)
    annotation (Line(points={{326,360},{388,360}}, color={0,127,255}));
  connect(senVolRet.port_b, senTemRet.port_a)
    annotation (Line(points={{238,360},{202,360}}, color={0,127,255}));
  connect(senTemRet.port_b, vavOAoutlet) annotation (Line(points={{182,360},{
          -36,360},{-36,176},{-202,176}}, color={0,127,255}));
  connect(groSta.uGroOcc, opeModSel.uOcc) annotation (Line(points={{134,563},{159,
          563},{159,560},{166,560}},     color={255,0,255}));
  connect(groSta.nexOcc, opeModSel.tNexOcc)
    annotation (Line(points={{134,561},{166,561},{166,558}}, color={0,0,127}));
  connect(groSta.yCooTim, opeModSel.maxCooDowTim)
    annotation (Line(points={{134,557},{166,557},{166,556}}, color={0,0,127}));
  connect(groSta.yHigOccCoo, opeModSel.uHigOccCoo) annotation (Line(points={{134,549},
          {166,549},{166,554}},          color={255,0,255}));
  connect(groSta.yWarTim, opeModSel.maxWarUpTim)
    annotation (Line(points={{134,555},{166,555},{166,552}}, color={0,0,127}));
  connect(groSta.yOccHeaHig, opeModSel.uOccHeaHig) annotation (Line(points={{134,551},
          {166,551},{166,550}},          color={255,0,255}));
  connect(groSta.yOpeWin, opeModSel.uOpeWin) annotation (Line(points={{134,525},
          {159,525},{159,548},{166,548}}, color={255,127,0}));
  connect(groSta.yColZon, opeModSel.totColZon) annotation (Line(points={{134,546},
          {166,546}},                color={255,127,0}));
  connect(groSta.ySetBac, opeModSel.uSetBac) annotation (Line(points={{134,544},
          {166,544}},           color={255,0,255}));
  connect(groSta.yEndSetBac, opeModSel.uEndSetBac) annotation (Line(points={{134,542},
          {166,542}},                    color={255,0,255}));
  connect(groSta.yHotZon, opeModSel.totHotZon) annotation (Line(points={{134,539},
          {159,539},{159,536},{166,536}},      color={255,127,0}));
  connect(groSta.TZonMax, opeModSel.TZonMax)
    annotation (Line(points={{134,531},{166,531},{166,540}}, color={0,0,127}));
  connect(groSta.TZonMin, opeModSel.TZonMin)
    annotation (Line(points={{134,529},{166,529},{166,538}}, color={0,0,127}));
  connect(groSta.ySetUp, opeModSel.uSetUp) annotation (Line(points={{134,537},{166,
          537},{166,534}},     color={255,0,255}));
  connect(groSta.yEndSetUp, opeModSel.uEndSetUp) annotation (Line(points={{134,535},
          {166,535},{166,532}},      color={255,0,255}));
  connect(opeModSel.yOpeMod, intRep.u) annotation (Line(points={{190,546},{214,546},
          {214,522},{178,522},{178,508},{179.2,508}},      color={255,127,0}));
  connect(terUniCon.yDam, damCore.y) annotation (Line(points={{432,228},{458,
          228},{458,188},{482,188}}, color={0,0,127}));
  connect(terUniCon.yVal, reheatElec1.u) annotation (Line(points={{432,223},{
          454,223},{454,136},{488,136}}, color={0,0,127}));
  connect(terUniCon.VDis_flow, senVolCore.V_flow) annotation (Line(points={{408,
          220},{390,220},{390,206},{483,206},{483,228}}, color={0,0,127}));
  connect(terUniCon.yDam_actual, damCore.y_actual) annotation (Line(points={{
          408,218},{392,218},{392,208},{487,208},{487,193}}, color={0,0,127}));
  connect(terUniCon.TDis, senTemCore.T) annotation (Line(points={{408,216},{394,
          216},{394,210},{480,210},{480,266},{483,266}}, color={0,0,127}));
  connect(senTemSup.T, terUniCon.TSupAHU) annotation (Line(points={{410,75},{
          410,202},{396,202},{396,214},{408,214}}, color={0,0,127}));
  connect(opeModSel.yOpeMod, terUniCon.uOpeMod) annotation (Line(points={{190,
          546},{298,546},{298,212},{408,212}}, color={255,127,0}));
  connect(fanVSD.y, conAHU.ySupFanSpe) annotation (Line(points={{280,76},{344,
          76},{344,436},{534,436},{534,602},{502,602}}, color={0,0,127}));
  connect(conAHU.yHea, heaGas.u) annotation (Line(points={{502,530},{522,530},{
          522,442},{340,442},{340,112},{38,112},{38,70},{52,70}}, color={0,0,
          127}));
  connect(tab.y, reaToInt.u)
    annotation (Line(points={{579,518},{592,518}}, color={0,0,127}));
  connect(conAHU.yCoo, tab.u)
    annotation (Line(points={{502,518},{556,518}}, color={0,0,127}));
  connect(reaToInt.y, mulStaDX.stage) annotation (Line(points={{616,518},{624,
          518},{624,446},{342,446},{342,106},{148,106},{148,72},{177,72}},
        color={255,127,0}));
  connect(senVolOut.V_flow, conAHU.VOut_flow) annotation (Line(points={{-158,75},
          {-158,152},{326,152},{326,520},{414,520}}, color={0,0,127}));
  connect(conAHU.TMix, senTemMix.T) annotation (Line(points={{414,512},{330,512},
          {330,146},{10,146},{10,75}}, color={0,0,127}));
  connect(conAHU.yRetDamPos, damRet.y) annotation (Line(points={{502,506},{512,
          506},{512,452},{-24,452},{-24,122}}, color={0,0,127}));
  connect(damOA.y, conAHU.yOutDamPos) annotation (Line(points={{-104,76},{-104,
          456},{506,456},{506,494},{502,494}}, color={0,0,127}));
  connect(conAHU.TSup, terUniCon.TSupAHU) annotation (Line(points={{414,544},{
          370,544},{370,202},{396,202},{396,214},{408,214}}, color={0,0,127}));
  connect(zonToSys.ySumDesZonPop, conAHU.sumDesZonPop) annotation (Line(points=
          {{284,631},{310,631},{310,630},{350,630},{350,592},{414,592}}, color=
          {0,0,127}));
  connect(zonToSys.VSumDesPopBreZon_flow, conAHU.VSumDesPopBreZon_flow)
    annotation (Line(points={{284,628},{348,628},{348,586},{414,586}}, color={0,
          0,127}));
  connect(zonToSys.VSumDesAreBreZon_flow, conAHU.VSumDesAreBreZon_flow)
    annotation (Line(points={{284,625},{302,625},{302,626},{344,626},{344,580},
          {414,580}}, color={0,0,127}));
  connect(zonToSys.yDesSysVenEff, conAHU.uDesSysVenEff) annotation (Line(points=
         {{284,622},{334,622},{334,574},{414,574}}, color={0,0,127}));
  connect(zonToSys.VSumUncOutAir_flow, conAHU.VSumUncOutAir_flow) annotation (
      Line(points={{284,619},{298,619},{298,620},{328,620},{328,568},{414,568}},
        color={0,0,127}));
  connect(zonToSys.VSumSysPriAir_flow, conAHU.VSumSysPriAir_flow) annotation (
      Line(points={{284,613},{292,613},{292,614},{322,614},{322,562},{414,562}},
        color={0,0,127}));
  connect(zonToSys.uOutAirFra_max, conAHU.uOutAirFra_max) annotation (Line(
        points={{284,616},{318,616},{318,556},{414,556}}, color={0,0,127}));
  connect(dpDisSupFan.port_a, fanVSD.port_b)
    annotation (Line(points={{302,80},{302,64},{290,64}}, color={0,127,255}));
  connect(dpDisSupFan.port_b, vavOAoutlet) annotation (Line(points={{302,100},{
          302,176},{-202,176}}, color={0,127,255}));
  connect(dpDisSupFan.p_rel, conAHU.ducStaPre) annotation (Line(points={{293,90},
          {356,90},{356,604},{414,604}}, color={0,0,127}));
  connect(senTOut, conAHU.TOut) annotation (Line(points={{-214,506},{124,506},{124,
            648},{370,648},{370,610},{414,610}},   color={0,0,127}));
  connect(zonToSys.yAveOutAirFraPlu, conAHU.yAveOutAirFraPlu) annotation (Line(
        points={{260,624},{252,624},{252,468},{522,468},{522,566},{502,566}},
        color={0,0,127}));
  connect(conAHU.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{414,504},
          {356,504},{356,506},{298,506},{298,212},{408,212}}, color={255,127,0}));
  connect(terUniCon.yZonTemResReq, TZonResReq.u[1]) annotation (Line(points={{432,218},
          {436,218},{436,419.6},{444,419.6}},      color={255,127,0}));
  connect(terUniCon.yZonPreResReq, PZonResReq.u[1]) annotation (Line(points={{432,214},
          {440,214},{440,383.6},{444,383.6}},      color={255,127,0}));
  connect(TZonResReq.y, conAHU.uZonTemResReq) annotation (Line(points={{468,414},
          {482,414},{482,462},{402,462},{402,498},{414,498}}, color={255,127,0}));
  connect(PZonResReq.y, conAHU.uZonPreResReq) annotation (Line(points={{468,378},
          {486,378},{486,472},{410,472},{410,492},{414,492}}, color={255,127,0}));
  connect(TDis.u1[1], senTemCore.T) annotation (Line(points={{138,444},{2,444},{
          2,266},{483,266}}, color={0,0,127}));
  connect(senTemPerimeter1.T, TDis.u2[1]) annotation (Line(points={{657,266},{336,
          266},{336,270},{14,270},{14,439},{138,439}}, color={0,0,127}));
  connect(senTemPerimeter2.T, TDis.u3[1]) annotation (Line(points={{815,266},{648,
          266},{648,276},{24,276},{24,434},{138,434}}, color={0,0,127}));
  connect(senTemPerimeter3.T, TDis.u4[1]) annotation (Line(points={{957,268},{32.5,
          268},{32.5,429},{138,429}}, color={0,0,127}));
  connect(senTemPerimeter4.T, TDis.u5[1]) annotation (Line(points={{1101,266},{46,
          266},{46,424},{138,424}}, color={0,0,127}));
  connect(VDis_flow.u1[1], senVolCore.V_flow) annotation (Line(points={{138,404},
          {108,404},{108,402},{58,402},{58,286},{483,286},{483,228}}, color={0,0,
          127}));
  connect(VDis_flow.u2[1], senVolPerimeter1.V_flow) annotation (Line(points={{138,399},
          {90,399},{90,398},{54,398},{54,290},{642,290},{642,228},{657,228}},
        color={0,0,127}));
  connect(VDis_flow.u3[1], senVolPerimeter2.V_flow) annotation (Line(points={{138,
          394},{108,394},{108,392},{74,392},{74,296},{815,296},{815,228}},
        color={0,0,127}));
  connect(VDis_flow.u4[1], senVolPerimeter3.V_flow) annotation (Line(points={{138,
          389},{82,389},{82,302},{948,302},{948,228},{957,228}}, color={0,0,127}));
  connect(VDis_flow.u5[1], senVolPerimeter4.V_flow) annotation (Line(points={{138,
          384},{90,384},{90,310},{1101,310},{1101,228}}, color={0,0,127}));
  connect(warmupCooldown.y, zonSta.cooDowTim) annotation (Line(points={{-60,570},
          {-16,570},{-16,554},{36,554}}, color={0,0,127}));
  connect(zonSta.warUpTim, warmupCooldown.y) annotation (Line(points={{36,550},{
          -16,550},{-16,570},{-60,570}}, color={0,0,127}));
  connect(zonSta.yCooTim, groSta.uCooTim) annotation (Line(points={{60,559},{76,
          559},{76,558},{94,558},{94,555},{110,555}}, color={0,0,127}));
  connect(zonSta.yWarTim, groSta.uWarTim) annotation (Line(points={{60,557},{60,
          556},{92,556},{92,553},{110,553}}, color={0,0,127}));
  connect(zonSta.yOccHeaHig, groSta.uOccHeaHig) annotation (Line(points={{60,552},
          {84,552},{84,549},{110,549}}, color={255,0,255}));
  connect(zonSta.yHigOccCoo, groSta.uHigOccCoo) annotation (Line(points={{60,547},
          {62,547},{62,547},{110,547}}, color={255,0,255}));
  connect(zonSta.yUnoHeaHig, groSta.uUnoHeaHig) annotation (Line(points={{60,542},
          {84,542},{84,543},{110,543}}, color={255,0,255}));
  connect(zonSta.yEndSetBac, groSta.uEndSetBac) annotation (Line(points={{60,540},
          {86,540},{86,539},{110,539}}, color={255,0,255}));
  connect(zonSta.yHigUnoCoo, groSta.uHigUnoCoo) annotation (Line(points={{60,535},
          {62,535},{62,535},{110,535}}, color={255,0,255}));
  connect(zonSta.yEndSetUp, groSta.uEndSetUp) annotation (Line(points={{60,533},
          {62,533},{62,532},{110,532},{110,531}}, color={255,0,255}));
  connect(zonSta.THeaSetOff, groSta.THeaSetOff) annotation (Line(points={{60,544},
          {88,544},{88,541},{110,541}}, color={0,0,127}));
  connect(zonSta.TCooSetOff, groSta.TCooSetOff) annotation (Line(points={{60,537},
          {86,537},{86,533},{110,533}}, color={0,0,127}));
  connect(TZonSet.TZonHeaSetUno, zonSta.THeaSetOff) annotation (Line(points={{198,
          484},{88,484},{88,544},{60,544}}, color={0,0,127}));
  connect(zonSta.THeaSetOn, TZonSet.TZonHeaSetOcc) annotation (Line(points={{60,
          554},{84,554},{84,486},{198,486}}, color={0,0,127}));
  connect(TZonSet.TZonCooSetUno, zonSta.TCooSetOff) annotation (Line(points={{198,
          489},{192,489},{192,490},{86,490},{86,537},{60,537}}, color={0,0,127}));
  connect(zonSta.TCooSetOn, TZonSet.TZonCooSetOcc) annotation (Line(points={{60,
          549},{68,549},{68,548},{82,548},{82,491},{198,491}}, color={0,0,127}));
  connect(TZonSet.uOpeMod, intRep.y) annotation (Line(points={{198,495},{198,496},
          {194,496},{194,508},{188.8,508}}, color={255,127,0}));
  connect(TZonSet.uCooDemLimLev, demLimLev.y) annotation (Line(points={{198,476},
          {-30,476},{-30,486},{-58,486}}, color={255,127,0}));
  connect(TZonSet.uHeaDemLimLev, demLimLev.y) annotation (Line(points={{198,474},
          {-30,474},{-30,486},{-58,486}}, color={255,127,0}));
  connect(groSta.uWin, falSta.y) annotation (Line(points={{110,525},{108,525},{108,
          524},{98,524},{98,610},{-60,610}}, color={255,0,255}));
  connect(conAHU.yReqOutAir, booRep1.u)
    annotation (Line(points={{502,542},{542,542}}, color={255,0,255}));
  connect(booRep1.y, zonOutAirSet.uReqOutAir) annotation (Line(points={{566,542},
          {586,542},{586,638},{136,638},{136,627},{144,627}}, color={255,0,255}));
  connect(conAHU.VDesUncOutAir_flow, reaRep1.u)
    annotation (Line(points={{502,578},{542,578}}, color={0,0,127}));
  connect(reaRep1.y, zonOutAirSet.VUncOut_flow_nominal) annotation (Line(points=
         {{566,578},{574,578},{574,660},{132,660},{132,615},{144,615}}, color={0,
          0,127}));
  connect(zonOutAirSet.TDis, TDis.y) annotation (Line(points={{144,621},{140,621},
          {140,508},{174,508},{174,434},{161,434}}, color={0,0,127}));
  connect(VDis_flow.y, zonOutAirSet.VDis_flow) annotation (Line(points={{161,394},
          {176,394},{176,510},{142,510},{142,618},{144,618}}, color={0,0,127}));
  connect(zonOutAirSet.yDesZonPeaOcc, zonToSys.uDesZonPeaOcc) annotation (Line(
        points={{168,633},{214,633},{214,630},{260,630}}, color={0,0,127}));
  connect(zonOutAirSet.VDesPopBreZon_flow, zonToSys.VDesPopBreZon_flow)
    annotation (Line(points={{168,630},{214,630},{214,628},{260,628}}, color={0,
          0,127}));
  connect(zonOutAirSet.VDesAreBreZon_flow, zonToSys.VDesAreBreZon_flow)
    annotation (Line(points={{168,627},{214,627},{214,626},{260,626}}, color={0,
          0,127}));
  connect(zonOutAirSet.yDesPriOutAirFra, zonToSys.uDesPriOutAirFra) annotation (
     Line(points={{168,624},{214,624},{214,620},{260,620}}, color={0,0,127}));
  connect(zonOutAirSet.VUncOutAir_flow, zonToSys.VUncOutAir_flow) annotation (
      Line(points={{168,621},{214,621},{214,618},{260,618}}, color={0,0,127}));
  connect(zonOutAirSet.yPriOutAirFra, zonToSys.uPriOutAirFra) annotation (Line(
        points={{168,618},{214,618},{214,616},{260,616}}, color={0,0,127}));
  connect(zonOutAirSet.VPriAir_flow, zonToSys.VPriAir_flow) annotation (Line(
        points={{168,615},{214,615},{214,614},{260,614}}, color={0,0,127}));
  connect(terUniCon.TZonHeaSet, TZonSet[1].TZonHeaSet) annotation (Line(points={
          {408,232},{398,232},{398,330},{278,330},{278,482},{222,482}}, color={0,
          0,127}));
  connect(TZonSet[1].TZonCooSet, terUniCon.TZonCooSet) annotation (Line(points={
          {222,490},{274,490},{274,324},{390,324},{390,230},{408,230}}, color={0,
          0,127}));
  connect(terUniCon1.yDam, damPerimeter1.y) annotation (Line(points={{620,226},{
          628,226},{628,188},{656,188}}, color={0,0,127}));
  connect(terUniCon1.yVal, reheatElec2.u) annotation (Line(points={{620,221},{624,
          221},{624,136},{662,136}}, color={0,0,127}));
  connect(terUniCon1.TDis, senTemPerimeter1.T) annotation (Line(points={{596,214},
          {590,214},{590,206},{648,206},{648,266},{657,266}}, color={0,0,127}));
  connect(damPerimeter1.y_actual, terUniCon1.yDam_actual) annotation (Line(
        points={{661,193},{661,204},{584,204},{584,216},{596,216}}, color={0,0,127}));
  connect(terUniCon1.VDis_flow, senVolPerimeter1.V_flow) annotation (Line(
        points={{596,218},{582,218},{582,202},{657,202},{657,228}}, color={0,0,127}));
  connect(terUniCon1.TZonHeaSet, TZonSet[2].TZonHeaSet)
    annotation (Line(points={{596,230},{222,230},{222,482}}, color={0,0,127}));
  connect(terUniCon1.TZonCooSet, TZonSet[2].TZonCooSet)
    annotation (Line(points={{596,228},{222,228},{222,490}}, color={0,0,127}));
  connect(terUniCon1.yZonTemResReq, TZonResReq.u[2]) annotation (Line(points={{620,
          216},{628,216},{628,342},{436,342},{436,416.8},{444,416.8}}, color={255,
          127,0}));
  connect(terUniCon1.yZonPreResReq, PZonResReq.u[2]) annotation (Line(points={{620,
          212},{628,212},{628,336},{440,336},{440,380.8},{444,380.8}}, color={255,
          127,0}));
  connect(terUniCon2.yDam, damPerimeter2.y) annotation (Line(points={{784,222},{
          800,222},{800,190},{814,190}}, color={0,0,127}));
  connect(terUniCon2.yVal, reheatElec3.u) annotation (Line(points={{784,217},{788,
          217},{788,216},{796,216},{796,136},{820,136}}, color={0,0,127}));
  connect(terUniCon2.TDis, senTemPerimeter2.T) annotation (Line(points={{760,210},
          {752,210},{752,196},{808,196},{808,266},{815,266}}, color={0,0,127}));
  connect(terUniCon2.yDam_actual, damPerimeter2.y_actual) annotation (Line(
        points={{760,212},{750,212},{750,195},{819,195}}, color={0,0,127}));
  connect(terUniCon2.VDis_flow, senVolPerimeter2.V_flow) annotation (Line(
        points={{760,214},{748,214},{748,192},{815,192},{815,228}}, color={0,0,127}));
  connect(terUniCon1.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{596,210},
          {382,210},{382,212},{408,212}}, color={255,127,0}));
  connect(terUniCon2.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{760,206},
          {574,206},{574,210},{382,210},{382,212},{408,212}}, color={255,127,0}));
  connect(terUniCon2.TZonCooSet, TZonSet[3].TZonCooSet) annotation (Line(points={{760,224},
            {222,224},{222,490}},                             color={0,0,127}));
  connect(terUniCon2.TZonHeaSet, TZonSet[3].TZonHeaSet) annotation (Line(points=
         {{760,226},{750,226},{750,482},{222,482}}, color={0,0,127}));
  connect(terUniCon2.yZonTemResReq, TZonResReq.u[3]) annotation (Line(points={{784,
          212},{444,212},{444,414}}, color={255,127,0}));
  connect(terUniCon2.yZonPreResReq, PZonResReq.u[3]) annotation (Line(points={{784,
          208},{784,378},{444,378}}, color={255,127,0}));
  connect(terUniCon3.yDam, damPerimeter3.y) annotation (Line(points={{924,212},{
          940,212},{940,190},{956,190}}, color={0,0,127}));
  connect(terUniCon3.yVal, reheatElec4.u) annotation (Line(points={{924,207},{930,
          207},{930,206},{936,206},{936,134},{962,134}}, color={0,0,127}));
  connect(terUniCon3.TDis, senTemPerimeter3.T) annotation (Line(points={{900,200},
          {896,200},{896,188},{957,188},{957,268}}, color={0,0,127}));
  connect(terUniCon3.yDam_actual, damPerimeter3.y_actual) annotation (Line(
        points={{900,202},{894,202},{894,192},{950,192},{950,195},{961,195}},
        color={0,0,127}));
  connect(terUniCon3.VDis_flow, senVolPerimeter3.V_flow) annotation (Line(
        points={{900,204},{892,204},{892,194},{957,194},{957,228}}, color={0,0,127}));
  connect(terUniCon3.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{900,196},
          {756,196},{756,206},{574,206},{574,210},{382,210},{382,212},{408,212}},
        color={255,127,0}));
  connect(terUniCon3.TZonHeaSet, TZonSet[4].TZonHeaSet)
    annotation (Line(points={{900,216},{222,216},{222,482}}, color={0,0,127}));
  connect(TZonSet[4].TZonCooSet, terUniCon3.TZonCooSet) annotation (Line(points=
         {{222,490},{878,490},{878,214},{900,214}}, color={0,0,127}));
  connect(terUniCon3.yZonTemResReq, TZonResReq.u[4]) annotation (Line(points={{924,
          202},{930,202},{930,411.2},{444,411.2}}, color={255,127,0}));
  connect(terUniCon3.yZonPreResReq, PZonResReq.u[4]) annotation (Line(points={{924,
          198},{924,375.2},{444,375.2}}, color={255,127,0}));
  connect(terUniCon4.yVal, reheatElec5.u) annotation (Line(points={{1076,203},{1080,
          203},{1080,204},{1092,204},{1092,126},{1108,126},{1108,132}}, color={0,
          0,127}));
  connect(terUniCon4.yDam, damPerimeter4.y) annotation (Line(points={{1076,208},
          {1094,208},{1094,190},{1100,190}}, color={0,0,127}));
  connect(terUniCon4.yDam_actual, damPerimeter4.y_actual) annotation (Line(
        points={{1052,198},{1046,198},{1046,180},{1098,180},{1098,195},{1105,195}},
        color={0,0,127}));
  connect(terUniCon4.TDis, senTemPerimeter4.T) annotation (Line(points={{1052,196},
          {1048,196},{1048,182},{1101,182},{1101,266}}, color={0,0,127}));
  connect(terUniCon4.VDis_flow, senVolPerimeter4.V_flow) annotation (Line(
        points={{1052,200},{1042,200},{1042,184},{1101,184},{1101,228}}, color={
          0,0,127}));
  connect(terUniCon4.yZonTemResReq, TZonResReq.u[5]) annotation (Line(points={{1076,
          198},{1084,198},{1084,408.4},{444,408.4}}, color={255,127,0}));
  connect(terUniCon4.yZonPreResReq, PZonResReq.u[5]) annotation (Line(points={{1076,
          194},{1080,194},{1080,192},{1092,192},{1092,372.4},{444,372.4}},
        color={255,127,0}));
  connect(terUniCon4.TZonCooSet, TZonSet[5].TZonCooSet) annotation (Line(points=
         {{1052,210},{1030,210},{1030,490},{222,490}}, color={0,0,127}));
  connect(terUniCon4.TZonHeaSet, TZonSet[5].TZonHeaSet) annotation (Line(points=
         {{1052,212},{1052,482},{222,482}}, color={0,0,127}));
    connect(booRep2.y, groSta.uOcc) annotation (Line(points={{-20,630},{40,630},{40,
            561},{110,561}}, color={255,0,255}));
    connect(reaRep2.y, groSta.tNexOcc) annotation (Line(points={{12,646},{36,646},
            {36,644},{94,644},{94,559},{110,559}}, color={0,0,127}));
    connect(zonSta.TZon, u) annotation (Line(points={{36,538},{-156,538},{-156,592},
            {-218,592}}, color={0,0,127}));
    connect(groSta.TZon, u) annotation (Line(points={{110,527},{102,527},{102,528},
            {6,528},{6,538},{-156,538},{-156,592},{-218,592}}, color={0,0,127}));
    connect(zonOutAirSet.TZon, u) annotation (Line(points={{144,624},{80,624},{80,
            592},{-218,592}}, color={0,0,127}));
    connect(TRooAir.u, u) annotation (Line(points={{158,236},{-218,236},{-218,592}},
          color={0,0,127}));
    connect(terUniCon.TZon, TRooAir.y1[1]) annotation (Line(points={{408,222},{218,
            222},{218,244},{181,244}}, color={0,0,127}));
    connect(TRooAir.y2[1], terUniCon1.TZon) annotation (Line(points={{181,240},{214,
            240},{214,220},{596,220}}, color={0,0,127}));
    connect(terUniCon2.TZon, TRooAir.y3[1]) annotation (Line(points={{760,216},{756,
            216},{756,220},{210,220},{210,236},{181,236}}, color={0,0,127}));
    connect(TRooAir.y4[1], terUniCon3.TZon) annotation (Line(points={{181,232},{208,
            232},{208,206},{900,206}}, color={0,0,127}));
    connect(terUniCon4.TZon, TRooAir.y5[1]) annotation (Line(points={{1052,202},{204,
            202},{204,228},{181,228}}, color={0,0,127}));
    connect(occSchWeekdays.occupied, booRep2.u) annotation (Line(points={{-85,640},
            {-64,640},{-64,630},{-44,630}}, color={255,0,255}));
    connect(occSchWeekdays.tNexOcc, reaRep2.u) annotation (Line(points={{-85,652},
            {-48,652},{-48,646},{-12,646}}, color={0,0,127}));
    connect(mulStaDX.TConIn, conAHU.TOut) annotation (Line(points={{177,67},{-136,
            67},{-136,506},{124,506},{124,648},{370,648},{370,610},{414,610}},
          color={0,0,127}));
    connect(groSta.zonOcc, falSta.y) annotation (Line(points={{110,563},{108,563},
            {108,608},{98,608},{98,610},{-60,610}}, color={255,0,255}));
    connect(conAHU.TZonHeaSet, TZonSet[1].TZonHeaSet) annotation (Line(points={{414,
            622},{248,622},{248,482},{222,482}}, color={0,0,127}));
    connect(conAHU.TZonCooSet, TZonSet[1].TZonCooSet) annotation (Line(points={{414,
            616},{268,616},{268,490},{222,490}}, color={0,0,127}));
    connect(senTemRet.T, conAHU.TOutCut)
      annotation (Line(points={{192,371},{192,538},{414,538}}, color={0,0,127}));
    connect(senTemSup.T, terUniCon1.TSupAHU) annotation (Line(points={{410,75},{410,
            170},{596,170},{596,212}}, color={0,0,127}));
    connect(terUniCon2.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{760,
            208},{732,208},{732,170},{596,170},{596,212}}, color={0,0,127}));
    connect(terUniCon3.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{900,
            198},{892,198},{892,170},{596,170},{596,212}}, color={0,0,127}));
    connect(terUniCon4.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{1052,
            194},{1002,194},{1002,170},{596,170},{596,212}}, color={0,0,127}));
    connect(terUniCon4.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{1052,
            192},{880,192},{880,196},{756,196},{756,206},{574,206},{574,210},{382,
            210},{382,212},{408,212}}, color={255,127,0}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false, extent={{-200,0},{1160,640}})),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-200,0},{1160,
            640}})),
    uses(Modelica(version="3.2.3"), Buildings(version="8.0.0")));
  end PackagedMZVAVReheat;

  PackagedMZVAVReheat packagedMZVAVReheat
    annotation (Placement(transformation(extent={{-50,-26},{86,38}})));
  Buildings.Fluid.Sources.Outside out(redeclare package Medium = Medium,
                                      nPorts=2)
    annotation (Placement(transformation(extent={{-132,-26},{-112,-6}})));
  inner Buildings.ThermalZones.EnergyPlus.Building building(idfName=
        Modelica.Utilities.Files.loadResource(
        "/home/thibault/Desktop/MODRLC/Working/New/MODRLC/testcases/spawnrefmediumoffice/models/Ressources/RefBldgMediumOfficeNew2004_v1.4_7.2_5B_USA_CO_BOULDER.idf"),
      weaName=Modelica.Utilities.Files.loadResource(
        "modelica://Buildings/Resources/weatherdata/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos"))
    annotation (Placement(transformation(extent={{-190,62},{-170,82}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Core_bottom(
    zoneName="Core_bottom",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{-70,80},{-30,120}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_bot_ZN_1(
    zoneName="Perimeter_bot_ZN_1",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{-18,78},{22,118}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_bot_ZN_2(
    zoneName="Perimeter_bot_ZN_2",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{42,80},{82,120}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_bot_ZN_3(
    zoneName="Perimeter_bot_ZN_3",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{94,82},{134,122}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_bot_ZN_4(
    zoneName="Perimeter_bot_ZN_4",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{150,86},{190,126}})));
Modelica.Blocks.Routing.Multiplex5 TRooms "Discharge air temperatures"
    annotation (Placement(transformation(extent={{-108,58},{-88,78}})));
  Modelica.Blocks.Routing.Multiplex3 mul "Multiplex for gains"
    annotation (Placement(transformation(extent={{-208,140},{-188,160}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k=0) "Latent heat gain"
    annotation (Placement(transformation(extent={{-260,108},{-240,128}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k=0) "Convective heat gain"
    annotation (Placement(transformation(extent={{-260,140},{-240,160}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k=0) "Radiative heat gain"
    annotation (Placement(transformation(extent={{-260,180},{-240,200}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
        transformation(extent={{-174,48},{-134,88}}), iconTransformation(extent={{-8,-172},
            {12,-152}})));
equation
  connect(packagedMZVAVReheat.vavOAinlet, out.ports[1]) annotation (Line(points={{-50,
          -19.6},{-82,-19.6},{-82,-14},{-112,-14}},      color={0,127,255}));
  connect(packagedMZVAVReheat.vavOAoutlet, out.ports[2]) annotation (Line(
        points={{-50.2,-8.4},{-81.1,-8.4},{-81.1,-18},{-112,-18}}, color={0,127,
          255}));
  connect(out.weaBus, building.weaBus) annotation (Line(
      points={{-132,-15.8},{-170,-15.8},{-170,72}},
      color={255,204,51},
      thickness=0.5));
  connect(packagedMZVAVReheat.vavReturnCore, Core_bottom.ports[1]) annotation (
      Line(points={{-9,40},{-30,40},{-30,80.9},{-52,80.9}}, color={0,127,255}));
  connect(packagedMZVAVReheat.vavCoreOut, Core_bottom.ports[2]) annotation (
      Line(points={{-2,39.8},{-28,39.8},{-28,80.9},{-48,80.9}}, color={0,127,
          255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter1, Perimeter_bot_ZN_1.ports[1])
    annotation (Line(points={{9.4,39.8},{9.4,57.9},{0,57.9},{0,78.9}}, color={0,
          127,255}));
  connect(packagedMZVAVReheat.vavPerimeter1Out, Perimeter_bot_ZN_1.ports[2])
    annotation (Line(points={{19.2,39.8},{19.2,58.9},{4,58.9},{4,78.9}}, color=
          {0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter2, Perimeter_bot_ZN_2.ports[1])
    annotation (Line(points={{33.4,40.4},{33.4,61.2},{60,61.2},{60,80.9}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavPerimeter2Out, Perimeter_bot_ZN_2.ports[2])
    annotation (Line(points={{40.6,40.2},{40.6,60.1},{64,60.1},{64,80.9}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter3, Perimeter_bot_ZN_3.ports[1])
    annotation (Line(points={{53.6,40},{84,40},{84,82.9},{112,82.9}}, color={0,
          127,255}));
  connect(packagedMZVAVReheat.vavPerimeter3Out, Perimeter_bot_ZN_3.ports[2])
    annotation (Line(points={{62.6,39.8},{89.3,39.8},{89.3,82.9},{116,82.9}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavReturnPerimeter4, Perimeter_bot_ZN_4.ports[1])
    annotation (Line(points={{72,40},{120,40},{120,86.9},{168,86.9}}, color={0,
          127,255}));
  connect(packagedMZVAVReheat.vavPerimeter4Out, Perimeter_bot_ZN_4.ports[2])
    annotation (Line(points={{81.6,39.8},{125.8,39.8},{125.8,86.9},{172,86.9}},
        color={0,127,255}));
  connect(Core_bottom.TAir, TRooms.u1[1]) annotation (Line(points={{-29,118},{
          -28,118},{-28,132},{-110,132},{-110,78}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_1.TAir, TRooms.u2[1]) annotation (Line(points={{23,
          116},{24,116},{24,132},{26,132},{26,130},{-130,130},{-130,73},{-110,
          73}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_2.TAir, TRooms.u3[1]) annotation (Line(points={{83,
          118},{78,118},{78,148},{-98,148},{-98,88},{-104,88},{-104,68},{-110,
          68}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_3.TAir, TRooms.u4[1]) annotation (Line(points={{135,
          120},{135,130},{-130,130},{-130,63},{-110,63}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_4.TAir, TRooms.u5[1]) annotation (Line(points={{191,
          124},{196,124},{196,130},{-138,130},{-138,58},{-110,58}}, color={0,0,
          127}));
  connect(mul.u3[1],qLatGai_flow. y) annotation (Line(points={{-210,143},{-220,
          143},{-220,118},{-239,118}},
                                color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qConGai_flow.y,mul. u2[1]) annotation (Line(
      points={{-239,150},{-210,150}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qRadGai_flow.y,mul. u1[1]) annotation (Line(
      points={{-239,190},{-220,190},{-220,157},{-210,157}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(mul.y, Core_bottom.qGai_flow) annotation (Line(points={{-187,150},{
          -130,150},{-130,110},{-72,110}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_1.qGai_flow, mul.y) annotation (Line(points={{-20,
          108},{-106,108},{-106,150},{-187,150}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_2.qGai_flow, mul.y) annotation (Line(points={{40,110},
          {-74,110},{-74,150},{-187,150}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_3.qGai_flow, mul.y) annotation (Line(points={{92,112},
          {-48,112},{-48,150},{-187,150}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_4.qGai_flow, mul.y) annotation (Line(points={{148,
          116},{-22,116},{-22,150},{-187,150}}, color={0,0,127}));
  connect(TRooms.y, packagedMZVAVReheat.u) annotation (Line(points={{-87,68},{
          -70,68},{-70,33.2},{-51.8,33.2}}, color={0,0,127}));
  connect(building.weaBus, weaBus.TDryBul) annotation (Line(
      points={{-170,72},{-162,72},{-162,68},{-154,68}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{6,3},{6,3}},
      horizontalAlignment=TextAlignment.Left));
  connect(packagedMZVAVReheat.senTOut, weaBus.TDryBul.TDryBul) annotation (Line(
        points={{-51.4,24.6},{-154,24.6},{-154,68}}, color={0,0,127}), Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    uses(Buildings(version="8.0.0"), Modelica(version="3.2.3")),
    experiment(
      StopTime=604800,
      Interval=600,
      __Dymola_Algorithm="Dassl"));
end dev_mzvav;
