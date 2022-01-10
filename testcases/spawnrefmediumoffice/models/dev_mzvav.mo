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
      dp_nominal=100,
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
      dp_nominal=100)
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
      dp_nominal=100,
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
      dp_nominal=100,
    Q_flow_nominal=reheaNomPow2) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={668,148})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec3(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
      dp_nominal=100,
    Q_flow_nominal=reheaNomPow3) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={826,148})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec4(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
      dp_nominal=100,
    Q_flow_nominal=reheaNomPow4) "Electric reheat coil" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={968,146})));
  Buildings.Fluid.HeatExchangers.HeaterCooler_u reheatElec5(
    redeclare final package Medium = Medium,
    allowFlowReversal=true,
    m_flow_nominal=mFlowNom,
      dp_nominal=100,
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
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant warmupCooldown[numZon](
      final k=fill(1800, numZon)) "Warm up and cool down time"
    annotation (Placement(transformation(extent={{-82,560},{-62,580}})));
  Buildings.Controls.OBC.CDL.Logical.Sources.Constant falSta[numZon](final k=
        fill(false, numZon))
    "All windows are closed, no zone has override switch"
    annotation (Placement(transformation(extent={{-82,600},{-62,620}})));
    Buildings.Controls.OBC.CDL.Routing.IntegerScalarReplicator intRep(final
        nout=nZones) "All zones in same operation mode"
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
    Buildings.Controls.OBC.CDL.Routing.BooleanScalarReplicator booRep1(final
        nout=numZon) "Replicate signal whether the outdoor airflow is required"
      annotation (Placement(transformation(extent={{544,532},{564,552}})));
    Buildings.Controls.OBC.CDL.Routing.RealScalarReplicator reaRep1(final nout=
          numZon)
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
    Buildings.Controls.OBC.CDL.Routing.BooleanScalarReplicator booRep2(final
        nout=numZon) "Replicate signal whether the outdoor airflow is required"
      annotation (Placement(transformation(extent={{-42,620},{-22,640}})));
    Buildings.Controls.OBC.CDL.Routing.RealScalarReplicator reaRep2(final nout=
          numZon)
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
  connect(terUniCon.yDam, damCore.y) annotation (Line(points={{432,230.333},{
            458,230.333},{458,188},{482,188}},
                                     color={0,0,127}));
  connect(terUniCon.yVal, reheatElec1.u) annotation (Line(points={{432,227},{
            454,227},{454,136},{488,136}},
                                         color={0,0,127}));
  connect(terUniCon.VDis_flow, senVolCore.V_flow) annotation (Line(points={{408,
            220.333},{390,220.333},{390,206},{483,206},{483,228}},
                                                         color={0,0,127}));
  connect(terUniCon.yDam_actual, damCore.y_actual) annotation (Line(points={{408,
            218.667},{392,218.667},{392,208},{487,208},{487,193}},
                                                             color={0,0,127}));
  connect(terUniCon.TDis, senTemCore.T) annotation (Line(points={{408,217},{394,
            217},{394,210},{480,210},{480,266},{483,266}},
                                                         color={0,0,127}));
  connect(senTemSup.T, terUniCon.TSupAHU) annotation (Line(points={{410,75},{
            410,202},{396,202},{396,215.333},{408,215.333}},
                                                   color={0,0,127}));
  connect(opeModSel.yOpeMod, terUniCon.uOpeMod) annotation (Line(points={{190,546},
            {298,546},{298,213.667},{408,213.667}},
                                               color={255,127,0}));
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
            370,544},{370,202},{396,202},{396,215.333},{408,215.333}},
                                                             color={0,0,127}));
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
            {356,504},{356,506},{298,506},{298,213.667},{408,213.667}},
                                                              color={255,127,0}));
  connect(terUniCon.yZonTemResReq, TZonResReq.u[1]) annotation (Line(points={{432,
            223.667},{436,223.667},{436,419.6},{444,419.6}},
                                                   color={255,127,0}));
  connect(terUniCon.yZonPreResReq, PZonResReq.u[1]) annotation (Line(points={{432,
            220.333},{440,220.333},{440,383.6},{444,383.6}},
                                                   color={255,127,0}));
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
  connect(terUniCon.TZonHeaSet, TZonSet[1].TZonHeaSet) annotation (Line(points={{408,
            230.333},{398,230.333},{398,330},{278,330},{278,482},{222,482}},
                                                                        color={0,
          0,127}));
  connect(TZonSet[1].TZonCooSet, terUniCon.TZonCooSet) annotation (Line(points={{222,490},
            {274,490},{274,324},{390,324},{390,228.667},{408,228.667}}, color={0,
          0,127}));
  connect(terUniCon1.yDam, damPerimeter1.y) annotation (Line(points={{620,
            228.333},{628,228.333},{628,188},{656,188}},
                                         color={0,0,127}));
  connect(terUniCon1.yVal, reheatElec2.u) annotation (Line(points={{620,225},{
            624,225},{624,136},{662,136}},
                                     color={0,0,127}));
  connect(terUniCon1.TDis, senTemPerimeter1.T) annotation (Line(points={{596,215},
            {590,215},{590,206},{648,206},{648,266},{657,266}},
                                                              color={0,0,127}));
  connect(damPerimeter1.y_actual, terUniCon1.yDam_actual) annotation (Line(
        points={{661,193},{661,204},{584,204},{584,216.667},{596,216.667}},
                                                                    color={0,0,127}));
  connect(terUniCon1.VDis_flow, senVolPerimeter1.V_flow) annotation (Line(
        points={{596,218.333},{582,218.333},{582,202},{657,202},{657,228}},
                                                                    color={0,0,127}));
  connect(terUniCon1.TZonHeaSet, TZonSet[2].TZonHeaSet)
    annotation (Line(points={{596,228.333},{222,228.333},{222,482}},
                                                             color={0,0,127}));
  connect(terUniCon1.TZonCooSet, TZonSet[2].TZonCooSet)
    annotation (Line(points={{596,226.667},{222,226.667},{222,490}},
                                                             color={0,0,127}));
  connect(terUniCon1.yZonTemResReq, TZonResReq.u[2]) annotation (Line(points={{620,
            221.667},{628,221.667},{628,342},{436,342},{436,416.8},{444,416.8}},
                                                                       color={255,
          127,0}));
  connect(terUniCon1.yZonPreResReq, PZonResReq.u[2]) annotation (Line(points={{620,
            218.333},{628,218.333},{628,336},{440,336},{440,380.8},{444,380.8}},
                                                                       color={255,
          127,0}));
  connect(terUniCon2.yDam, damPerimeter2.y) annotation (Line(points={{784,
            224.333},{800,224.333},{800,190},{814,190}},
                                         color={0,0,127}));
  connect(terUniCon2.yVal, reheatElec3.u) annotation (Line(points={{784,221},{
            788,221},{788,216},{796,216},{796,136},{820,136}},
                                                         color={0,0,127}));
  connect(terUniCon2.TDis, senTemPerimeter2.T) annotation (Line(points={{760,211},
            {752,211},{752,196},{808,196},{808,266},{815,266}},
                                                              color={0,0,127}));
  connect(terUniCon2.yDam_actual, damPerimeter2.y_actual) annotation (Line(
        points={{760,212.667},{750,212.667},{750,195},{819,195}},
                                                          color={0,0,127}));
  connect(terUniCon2.VDis_flow, senVolPerimeter2.V_flow) annotation (Line(
        points={{760,214.333},{748,214.333},{748,192},{815,192},{815,228}},
                                                                    color={0,0,127}));
  connect(terUniCon1.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{596,
            211.667},{382,211.667},{382,213.667},{408,213.667}},
                                          color={255,127,0}));
  connect(terUniCon2.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{760,
            207.667},{574,207.667},{574,210},{382,210},{382,213.667},{408,
            213.667}},                                        color={255,127,0}));
  connect(terUniCon2.TZonCooSet, TZonSet[3].TZonCooSet) annotation (Line(points={{760,
            222.667},{222,222.667},{222,490}},                color={0,0,127}));
  connect(terUniCon2.TZonHeaSet, TZonSet[3].TZonHeaSet) annotation (Line(points={{760,
            224.333},{750,224.333},{750,482},{222,482}},
                                                    color={0,0,127}));
  connect(terUniCon2.yZonTemResReq, TZonResReq.u[3]) annotation (Line(points={{784,
            217.667},{444,217.667},{444,414}},
                                     color={255,127,0}));
  connect(terUniCon2.yZonPreResReq, PZonResReq.u[3]) annotation (Line(points={{784,
            214.333},{784,378},{444,378}},
                                     color={255,127,0}));
  connect(terUniCon3.yDam, damPerimeter3.y) annotation (Line(points={{924,
            214.333},{940,214.333},{940,190},{956,190}},
                                         color={0,0,127}));
  connect(terUniCon3.yVal, reheatElec4.u) annotation (Line(points={{924,211},{
            930,211},{930,206},{936,206},{936,134},{962,134}},
                                                         color={0,0,127}));
  connect(terUniCon3.TDis, senTemPerimeter3.T) annotation (Line(points={{900,201},
            {896,201},{896,188},{957,188},{957,268}},
                                                    color={0,0,127}));
  connect(terUniCon3.yDam_actual, damPerimeter3.y_actual) annotation (Line(
        points={{900,202.667},{894,202.667},{894,192},{950,192},{950,195},{961,
            195}},
        color={0,0,127}));
  connect(terUniCon3.VDis_flow, senVolPerimeter3.V_flow) annotation (Line(
        points={{900,204.333},{892,204.333},{892,194},{957,194},{957,228}},
                                                                    color={0,0,127}));
  connect(terUniCon3.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{900,
            197.667},{756,197.667},{756,206},{574,206},{574,210},{382,210},{382,
            213.667},{408,213.667}},
        color={255,127,0}));
  connect(terUniCon3.TZonHeaSet, TZonSet[4].TZonHeaSet)
    annotation (Line(points={{900,214.333},{222,214.333},{222,482}},
                                                             color={0,0,127}));
  connect(TZonSet[4].TZonCooSet, terUniCon3.TZonCooSet) annotation (Line(points={{222,490},
            {878,490},{878,212.667},{900,212.667}}, color={0,0,127}));
  connect(terUniCon3.yZonTemResReq, TZonResReq.u[4]) annotation (Line(points={{924,
            207.667},{930,207.667},{930,411.2},{444,411.2}},
                                                   color={255,127,0}));
  connect(terUniCon3.yZonPreResReq, PZonResReq.u[4]) annotation (Line(points={{924,
            204.333},{924,375.2},{444,375.2}},
                                         color={255,127,0}));
  connect(terUniCon4.yVal, reheatElec5.u) annotation (Line(points={{1076,207},{
            1080,207},{1080,204},{1092,204},{1092,126},{1108,126},{1108,132}},
                                                                        color={0,
          0,127}));
  connect(terUniCon4.yDam, damPerimeter4.y) annotation (Line(points={{1076,
            210.333},{1094,210.333},{1094,190},{1100,190}},
                                             color={0,0,127}));
  connect(terUniCon4.yDam_actual, damPerimeter4.y_actual) annotation (Line(
        points={{1052,198.667},{1046,198.667},{1046,180},{1098,180},{1098,195},
            {1105,195}},
        color={0,0,127}));
  connect(terUniCon4.TDis, senTemPerimeter4.T) annotation (Line(points={{1052,
            197},{1048,197},{1048,182},{1101,182},{1101,266}},
                                                        color={0,0,127}));
  connect(terUniCon4.VDis_flow, senVolPerimeter4.V_flow) annotation (Line(
        points={{1052,200.333},{1042,200.333},{1042,184},{1101,184},{1101,228}},
                                                                         color={
          0,0,127}));
  connect(terUniCon4.yZonTemResReq, TZonResReq.u[5]) annotation (Line(points={{1076,
            203.667},{1084,203.667},{1084,408.4},{444,408.4}},
                                                     color={255,127,0}));
  connect(terUniCon4.yZonPreResReq, PZonResReq.u[5]) annotation (Line(points={{1076,
            200.333},{1080,200.333},{1080,192},{1092,192},{1092,372.4},{444,
            372.4}},
        color={255,127,0}));
  connect(terUniCon4.TZonCooSet, TZonSet[5].TZonCooSet) annotation (Line(points={{1052,
            208.667},{1030,208.667},{1030,490},{222,490}},
                                                       color={0,0,127}));
  connect(terUniCon4.TZonHeaSet, TZonSet[5].TZonHeaSet) annotation (Line(points={{1052,
            210.333},{1052,482},{222,482}}, color={0,0,127}));
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
    connect(senTemSup.T, terUniCon1.TSupAHU) annotation (Line(points={{410,75},
            {410,170},{596,170},{596,213.333}},
                                       color={0,0,127}));
    connect(terUniCon2.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{760,
            209.333},{732,209.333},{732,170},{596,170},{596,213.333}},
                                                           color={0,0,127}));
    connect(terUniCon3.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{900,
            199.333},{892,199.333},{892,170},{596,170},{596,213.333}},
                                                           color={0,0,127}));
    connect(terUniCon4.TSupAHU, terUniCon1.TSupAHU) annotation (Line(points={{1052,
            195.333},{1002,195.333},{1002,170},{596,170},{596,213.333}},
                                                             color={0,0,127}));
    connect(terUniCon4.uOpeMod, terUniCon.uOpeMod) annotation (Line(points={{1052,
            193.667},{880,193.667},{880,196},{756,196},{756,206},{574,206},{574,
            210},{382,210},{382,213.667},{408,213.667}},
                                       color={255,127,0}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false, extent={{-200,0},{1160,640}})),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-200,0},{1160,
            640}})),
    uses(Modelica(version="3.2.3"), Buildings(version="8.0.0")));
  end PackagedMZVAVReheat;

  PackagedMZVAVReheat packagedMZVAVReheat(
    reheaNomPow1=36038.79,
    reheaNomPow2=13485.04,
    reheaNomPow3=9651.58,
    reheaNomPow4=13352.1,
    reheaNomPow5=11226.96,
    heaNomPow=34745.84)
    annotation (Placement(transformation(extent={{-50,-26},{86,38}})));
  Buildings.Fluid.Sources.Outside out(redeclare package Medium = Medium, nPorts=
       6)
    annotation (Placement(transformation(extent={{-290,-24},{-270,-4}})));
  inner Buildings.ThermalZones.EnergyPlus.Building building(
    idfName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefmediumoffice/RefBldgMediumOffice_BOULDER.idf"),
    epwName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefmediumoffice/USA_CO_Boulder.724699_TMY2.epw"),
    weaName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefmediumoffice/USA_CO_Boulder.724699_TMY2.mos"))
    annotation (Placement(transformation(extent={{-368,2},{-348,22}})));

  Buildings.ThermalZones.EnergyPlus.ThermalZone Core_bottom(
    zoneName="Core_bottom",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{-70,72},{-30,112}})));
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
    annotation (Placement(transformation(extent={{-278,492},{-258,512}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k=0) "Latent heat gain"
    annotation (Placement(transformation(extent={{-340,470},{-320,490}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k=0) "Convective heat gain"
    annotation (Placement(transformation(extent={{-340,502},{-320,522}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k=0) "Radiative heat gain"
    annotation (Placement(transformation(extent={{-332,534},{-312,554}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
        transformation(extent={{-302,-4},{-262,36}}), iconTransformation(extent={{-8,-172},
            {12,-152}})));
  PackagedMZVAVReheat packagedMZVAVReheat1(
    reheaNomPow1=34944.45,
    reheaNomPow2=14311.97,
    reheaNomPow3=11464.52,
    reheaNomPow4=14173.32,
    reheaNomPow5=12849.71,
    heaNomPow=33850.15,
    CCNomPowS1=-43517.23,
    CCmass_flow_nomS1=3.14,
    CCNomPowS2=-130564.75,
    CCmass_flow_nomS2=9.5,
    VFRCore=3.4699,
    VFRP1=1.1845,
    VFRP2=1.1384,
    VFRP3=0.8186,
    VFRP4=1.276,
    fanMaxVFR=7.88)
    annotation (Placement(transformation(extent={{-34,-230},{102,-166}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Core_mid(
    zoneName="Core_mid",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{-54,-124},{-14,-84}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_mid_ZN_1(
    zoneName="Perimeter_mid_ZN_1",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{-2,-126},{38,-86}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_mid_ZN_2(
    zoneName="Perimeter_mid_ZN_2",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{58,-124},{98,-84}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_mid_ZN_3(
    zoneName="Perimeter_mid_ZN_3",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{110,-122},{150,-82}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_mid_ZN_4(
    zoneName="Perimeter_mid_ZN_4",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{166,-118},{206,-78}})));
Modelica.Blocks.Routing.Multiplex5 TRooms1
                                          "Discharge air temperatures"
    annotation (Placement(transformation(extent={{-92,-146},{-72,-126}})));
  PackagedMZVAVReheat packagedMZVAVReheat2(
    heaNomPow=33993.76243,
    CCNomPowS1=-43102.68529,
    CCmass_flow_nomS1=3.108,
    CCNomPowS2=-129320.98797,
    CCmass_flow_nomS2=9.324,
    VFRCore=3.2904,
    VFRP1=1.1755,
    VFRP2=1.0727,
    VFRP3=0.9108,
    VFRP4=1.3253,
    fanMaxVFR=7.77)
    annotation (Placement(transformation(extent={{-12,-450},{124,-386}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Core_top(
    zoneName="Core_top",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{-32,-344},{8,-304}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_top_ZN_1(
    zoneName="Perimeter_top_ZN_1",
    redeclare package Medium = Medium,
    nPorts=2) annotation (Placement(transformation(extent={{20,-346},{60,-306}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_top_ZN_2(
    zoneName="Perimeter_top_ZN_2",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{80,-344},{120,-304}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_top_ZN_3(
    zoneName="Perimeter_top_ZN_3",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{132,-342},{172,-302}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone Perimeter_top_ZN_4(
    zoneName="Perimeter_top_ZN_4",
    redeclare package Medium = Medium,
    nPorts=2)
    annotation (Placement(transformation(extent={{188,-338},{228,-298}})));
Modelica.Blocks.Routing.Multiplex5 TRooms2
                                          "Discharge air temperatures"
    annotation (Placement(transformation(extent={{-70,-366},{-50,-346}})));
  Modelica.Blocks.Sources.CombiTimeTable GainsFromCSV(
    tableOnFile=true,
    fileName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefmediumoffice/dataFromModel4spawn.csv"),
    columns={62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,
        84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,
        106},
    tableName="csv",
    timeScale=3600) "Reader for gains"
    annotation (Placement(transformation(extent={{-392,236},{-372,256}})));
  Modelica.Blocks.Routing.DeMultiplex demux(n=45)
    annotation (Placement(transformation(extent={{-332,236},{-312,256}})));
  Modelica.Blocks.Routing.Multiplex3 coreBottomGains "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,476},{-174,496}})));
  Modelica.Blocks.Routing.Multiplex3 coreMidGains "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,450},{-174,470}})));
  Modelica.Blocks.Routing.Multiplex3 coreTopGains "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,424},{-174,444}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterBotGains1 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,398},{-174,418}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterBotGains2 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,372},{-174,392}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterBotGains3 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,344},{-174,364}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterBotGains4 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,318},{-174,338}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterMidGains1 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,292},{-174,312}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterMidGains2 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,264},{-174,284}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterMidGains3 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,238},{-174,258}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterMidGains4 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,212},{-174,232}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterTopGains1 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,186},{-174,206}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterTopGains2 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,158},{-174,178}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterTopGains3 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,130},{-174,150}})));
  Modelica.Blocks.Routing.Multiplex3 perimeterTopGains4 "Multiplex for gains"
    annotation (Placement(transformation(extent={{-194,104},{-174,124}})));
equation
  connect(out.weaBus, building.weaBus) annotation (Line(
      points={{-290,-13.8},{-348,-13.8},{-348,12}},
      color={255,204,51},
      thickness=0.5));
  connect(packagedMZVAVReheat.vavReturnCore, Core_bottom.ports[1]) annotation (
      Line(points={{-9,40},{-30,40},{-30,72.9},{-52,72.9}}, color={0,127,255}));
  connect(packagedMZVAVReheat.vavCoreOut, Core_bottom.ports[2]) annotation (
      Line(points={{-2,39.8},{-28,39.8},{-28,72.9},{-48,72.9}}, color={0,127,
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
  connect(Core_bottom.TAir, TRooms.u1[1]) annotation (Line(points={{-29,110},{
          -28,110},{-28,132},{-110,132},{-110,78}}, color={0,0,127}));
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
  connect(mul.u3[1],qLatGai_flow. y) annotation (Line(points={{-280,495},{-300,
          495},{-300,480},{-319,480}},
                                color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qConGai_flow.y,mul. u2[1]) annotation (Line(
      points={{-319,512},{-304,512},{-304,502},{-280,502}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qRadGai_flow.y,mul. u1[1]) annotation (Line(
      points={{-311,544},{-300,544},{-300,509},{-280,509}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(Perimeter_bot_ZN_1.qGai_flow, mul.y) annotation (Line(points={{-20,108},
          {-104,108},{-104,502},{-257,502}},      color={0,0,127}));
  connect(Perimeter_bot_ZN_2.qGai_flow, mul.y) annotation (Line(points={{40,110},
          {-72,110},{-72,502},{-257,502}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_3.qGai_flow, mul.y) annotation (Line(points={{92,112},
          {-46,112},{-46,502},{-257,502}}, color={0,0,127}));
  connect(Perimeter_bot_ZN_4.qGai_flow, mul.y) annotation (Line(points={{148,116},
          {-20,116},{-20,502},{-257,502}},      color={0,0,127}));
  connect(TRooms.y, packagedMZVAVReheat.u) annotation (Line(points={{-87,68},{
          -70,68},{-70,33.2},{-51.8,33.2}}, color={0,0,127}));
  connect(building.weaBus, weaBus.TDryBul) annotation (Line(
      points={{-348,12},{-304,12},{-304,16},{-282,16}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{6,3},{6,3}},
      horizontalAlignment=TextAlignment.Left));
  connect(packagedMZVAVReheat.senTOut, weaBus.TDryBul.TDryBul) annotation (Line(
        points={{-51.4,24.6},{-282,24.6},{-282,16}}, color={0,0,127}), Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(packagedMZVAVReheat1.vavReturnCore, Core_mid.ports[1]) annotation (
      Line(points={{7,-164},{-14,-164},{-14,-123.1},{-36,-123.1}}, color={0,127,
          255}));
  connect(packagedMZVAVReheat1.vavCoreOut, Core_mid.ports[2]) annotation (Line(
        points={{14,-164.2},{-12,-164.2},{-12,-123.1},{-32,-123.1}}, color={0,
          127,255}));
  connect(packagedMZVAVReheat1.vavReturnPerimeter1, Perimeter_mid_ZN_1.ports[1])
    annotation (Line(points={{25.4,-164.2},{25.4,-146.1},{16,-146.1},{16,-125.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavPerimeter1Out, Perimeter_mid_ZN_1.ports[2])
    annotation (Line(points={{35.2,-164.2},{35.2,-145.1},{20,-145.1},{20,-125.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavReturnPerimeter2, Perimeter_mid_ZN_2.ports[1])
    annotation (Line(points={{49.4,-163.6},{49.4,-142.8},{76,-142.8},{76,-123.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavPerimeter2Out, Perimeter_mid_ZN_2.ports[2])
    annotation (Line(points={{56.6,-163.8},{56.6,-143.9},{80,-143.9},{80,-123.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavReturnPerimeter3, Perimeter_mid_ZN_3.ports[1])
    annotation (Line(points={{69.6,-164},{100,-164},{100,-121.1},{128,-121.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavPerimeter3Out, Perimeter_mid_ZN_3.ports[2])
    annotation (Line(points={{78.6,-164.2},{105.3,-164.2},{105.3,-121.1},{132,
          -121.1}}, color={0,127,255}));
  connect(packagedMZVAVReheat1.vavReturnPerimeter4, Perimeter_mid_ZN_4.ports[1])
    annotation (Line(points={{88,-164},{136,-164},{136,-117.1},{184,-117.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavPerimeter4Out, Perimeter_mid_ZN_4.ports[2])
    annotation (Line(points={{97.6,-164.2},{141.8,-164.2},{141.8,-117.1},{188,
          -117.1}}, color={0,127,255}));
  connect(Core_mid.TAir, TRooms1.u1[1]) annotation (Line(points={{-13,-86},{-12,
          -86},{-12,-72},{-94,-72},{-94,-126}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_1.TAir, TRooms1.u2[1]) annotation (Line(points={{39,
          -88},{40,-88},{40,-72},{42,-72},{42,-74},{-114,-74},{-114,-131},{-94,
          -131}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_2.TAir, TRooms1.u3[1]) annotation (Line(points={{99,
          -86},{94,-86},{94,-56},{-82,-56},{-82,-116},{-88,-116},{-88,-136},{
          -94,-136}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_3.TAir, TRooms1.u4[1]) annotation (Line(points={{151,
          -84},{151,-74},{-114,-74},{-114,-141},{-94,-141}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_4.TAir, TRooms1.u5[1]) annotation (Line(points={{207,
          -80},{212,-80},{212,-74},{-122,-74},{-122,-146},{-94,-146}}, color={0,
          0,127}));
  connect(mul.y, Core_mid.qGai_flow) annotation (Line(points={{-257,502},{-112,
          502},{-112,-94},{-56,-94}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_1.qGai_flow, mul.y) annotation (Line(points={{-4,-96},
          {-88,-96},{-88,502},{-257,502}},        color={0,0,127}));
  connect(Perimeter_mid_ZN_2.qGai_flow, mul.y) annotation (Line(points={{56,-94},
          {-56,-94},{-56,502},{-257,502}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_3.qGai_flow, mul.y) annotation (Line(points={{108,-92},
          {-30,-92},{-30,502},{-257,502}}, color={0,0,127}));
  connect(Perimeter_mid_ZN_4.qGai_flow, mul.y) annotation (Line(points={{164,-88},
          {-4,-88},{-4,502},{-257,502}},        color={0,0,127}));
  connect(TRooms1.y, packagedMZVAVReheat1.u) annotation (Line(points={{-71,-136},
          {-54,-136},{-54,-170.8},{-35.8,-170.8}}, color={0,0,127}));
  connect(packagedMZVAVReheat1.senTOut, weaBus.TDryBul.TDryBul) annotation (
      Line(points={{-35.4,-179.4},{-282,-179.4},{-282,16}}, color={0,0,127}),
      Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(packagedMZVAVReheat2.vavReturnCore, Core_top.ports[1]) annotation (
      Line(points={{29,-384},{8,-384},{8,-343.1},{-14,-343.1}}, color={0,127,
          255}));
  connect(packagedMZVAVReheat2.vavCoreOut, Core_top.ports[2]) annotation (Line(
        points={{36,-384.2},{10,-384.2},{10,-343.1},{-10,-343.1}}, color={0,127,
          255}));
  connect(packagedMZVAVReheat2.vavReturnPerimeter1, Perimeter_top_ZN_1.ports[1])
    annotation (Line(points={{47.4,-384.2},{47.4,-366.1},{38,-366.1},{38,-345.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavPerimeter1Out, Perimeter_top_ZN_1.ports[2])
    annotation (Line(points={{57.2,-384.2},{57.2,-365.1},{42,-365.1},{42,-345.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavReturnPerimeter2, Perimeter_top_ZN_2.ports[1])
    annotation (Line(points={{71.4,-383.6},{71.4,-362.8},{98,-362.8},{98,-343.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavPerimeter2Out, Perimeter_top_ZN_2.ports[2])
    annotation (Line(points={{78.6,-383.8},{78.6,-363.9},{102,-363.9},{102,
          -343.1}}, color={0,127,255}));
  connect(packagedMZVAVReheat2.vavReturnPerimeter3, Perimeter_top_ZN_3.ports[1])
    annotation (Line(points={{91.6,-384},{122,-384},{122,-341.1},{150,-341.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavPerimeter3Out, Perimeter_top_ZN_3.ports[2])
    annotation (Line(points={{100.6,-384.2},{127.3,-384.2},{127.3,-341.1},{154,
          -341.1}}, color={0,127,255}));
  connect(packagedMZVAVReheat2.vavReturnPerimeter4, Perimeter_top_ZN_4.ports[1])
    annotation (Line(points={{110,-384},{158,-384},{158,-337.1},{206,-337.1}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavPerimeter4Out, Perimeter_top_ZN_4.ports[2])
    annotation (Line(points={{119.6,-384.2},{163.8,-384.2},{163.8,-337.1},{210,
          -337.1}}, color={0,127,255}));
  connect(Core_top.TAir, TRooms2.u1[1]) annotation (Line(points={{9,-306},{10,
          -306},{10,-292},{-72,-292},{-72,-346}}, color={0,0,127}));
  connect(Perimeter_top_ZN_1.TAir, TRooms2.u2[1]) annotation (Line(points={{61,
          -308},{62,-308},{62,-292},{64,-292},{64,-294},{-92,-294},{-92,-351},{
          -72,-351}}, color={0,0,127}));
  connect(Perimeter_top_ZN_2.TAir, TRooms2.u3[1]) annotation (Line(points={{121,
          -306},{116,-306},{116,-276},{-60,-276},{-60,-336},{-66,-336},{-66,
          -356},{-72,-356}}, color={0,0,127}));
  connect(Perimeter_top_ZN_3.TAir, TRooms2.u4[1]) annotation (Line(points={{173,
          -304},{173,-294},{-92,-294},{-92,-361},{-72,-361}}, color={0,0,127}));
  connect(Perimeter_top_ZN_4.TAir, TRooms2.u5[1]) annotation (Line(points={{229,
          -300},{234,-300},{234,-294},{-100,-294},{-100,-366},{-72,-366}},
        color={0,0,127}));
  connect(mul.y, Core_top.qGai_flow) annotation (Line(points={{-257,502},{-90,
          502},{-90,-314},{-34,-314}}, color={0,0,127}));
  connect(Perimeter_top_ZN_1.qGai_flow, mul.y) annotation (Line(points={{18,-316},
          {-66,-316},{-66,502},{-257,502}},       color={0,0,127}));
  connect(Perimeter_top_ZN_2.qGai_flow, mul.y) annotation (Line(points={{78,-314},
          {-34,-314},{-34,502},{-257,502}},       color={0,0,127}));
  connect(Perimeter_top_ZN_3.qGai_flow, mul.y) annotation (Line(points={{130,
          -312},{-8,-312},{-8,502},{-257,502}},   color={0,0,127}));
  connect(Perimeter_top_ZN_4.qGai_flow, mul.y) annotation (Line(points={{186,
          -308},{18,-308},{18,502},{-257,502}}, color={0,0,127}));
  connect(TRooms2.y, packagedMZVAVReheat2.u) annotation (Line(points={{-49,-356},
          {-32,-356},{-32,-390.8},{-13.8,-390.8}}, color={0,0,127}));
  connect(packagedMZVAVReheat2.senTOut, weaBus.TDryBul.TDryBul) annotation (
      Line(points={{-13.4,-399.4},{-282,-399.4},{-282,16}}, color={0,0,127}),
      Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(packagedMZVAVReheat2.vavOAoutlet, out.ports[1]) annotation (Line(
        points={{-12.2,-432.4},{-190,-432.4},{-190,-10.6667},{-270,-10.6667}},
        color={0,127,255}));
  connect(packagedMZVAVReheat2.vavOAinlet, out.ports[2]) annotation (Line(
        points={{-12,-443.6},{-62,-443.6},{-62,-444},{-208,-444},{-208,-12},{
          -270,-12}}, color={0,127,255}));
  connect(packagedMZVAVReheat1.vavOAinlet, out.ports[3]) annotation (Line(
        points={{-34,-223.6},{-170,-223.6},{-170,-13.3333},{-270,-13.3333}},
        color={0,127,255}));
  connect(packagedMZVAVReheat1.vavOAoutlet, out.ports[4]) annotation (Line(
        points={{-34.2,-212.4},{-152,-212.4},{-152,-14.6667},{-270,-14.6667}},
        color={0,127,255}));
  connect(packagedMZVAVReheat.vavOAinlet, out.ports[5]) annotation (Line(points=
         {{-50,-19.6},{-270,-19.6},{-270,-16}}, color={0,127,255}));
  connect(packagedMZVAVReheat.vavOAoutlet, out.ports[6]) annotation (Line(
        points={{-50.2,-8.4},{-270,-8.4},{-270,-17.3333}}, color={0,127,255}));
  connect(demux.u, GainsFromCSV.y)
    annotation (Line(points={{-334,246},{-371,246}}, color={0,0,127}));
  connect(coreBottomGains.u1, demux.y[1:1]) annotation (Line(points={{-196,493},
          {-256,493},{-256,252.844},{-312,252.844}}, color={0,0,127}));
  connect(coreBottomGains.u2, demux.y[2:2]) annotation (Line(points={{-196,486},
          {-258,486},{-258,252.533},{-312,252.533}}, color={0,0,127}));
  connect(coreBottomGains.u3, demux.y[3:3]) annotation (Line(points={{-196,479},
          {-256,479},{-256,252.222},{-312,252.222}}, color={0,0,127}));
  connect(coreMidGains.u1, demux.y[4:4]) annotation (Line(points={{-196,467},{
          -254,467},{-254,251.911},{-312,251.911}}, color={0,0,127}));
  connect(coreMidGains.u2, demux.y[5:5]) annotation (Line(points={{-196,460},{
          -250,460},{-250,242},{-312,242},{-312,251.6}}, color={0,0,127}));
  connect(coreMidGains.u3, demux.y[6:6]) annotation (Line(points={{-196,453},{
          -254,453},{-254,251.289},{-312,251.289}}, color={0,0,127}));
  connect(coreTopGains.u1, demux.y[7:7]) annotation (Line(points={{-196,441},{
          -254,441},{-254,250.978},{-312,250.978}}, color={0,0,127}));
  connect(coreTopGains.u2, demux.y[8:8]) annotation (Line(points={{-196,434},{
          -254,434},{-254,250.667},{-312,250.667}}, color={0,0,127}));
  connect(coreTopGains.u3, demux.y[9:9]) annotation (Line(points={{-196,427},{
          -246,427},{-246,250.356},{-312,250.356}}, color={0,0,127}));
  connect(perimeterBotGains1.u1, demux.y[10:10]) annotation (Line(points={{-196,
          415},{-232,415},{-232,250.044},{-312,250.044}}, color={0,0,127}));
  connect(perimeterBotGains1.u2, demux.y[11:11]) annotation (Line(points={{-196,
          408},{-312,408},{-312,249.733}}, color={0,0,127}));
  connect(perimeterBotGains1.u3, demux.y[12:12]) annotation (Line(points={{-196,
          401},{-312,401},{-312,249.422}}, color={0,0,127}));
  connect(perimeterBotGains2.u1, demux.y[13:13]) annotation (Line(points={{-196,
          389},{-312,389},{-312,249.111}}, color={0,0,127}));
  connect(perimeterBotGains2.u2, demux.y[14:14]) annotation (Line(points={{-196,
          382},{-312,382},{-312,248.8}}, color={0,0,127}));
  connect(perimeterBotGains2.u3, demux.y[15:15]) annotation (Line(points={{-196,
          375},{-312,375},{-312,248.489}}, color={0,0,127}));
  connect(perimeterBotGains3.u1, demux.y[16:16]) annotation (Line(points={{-196,
          361},{-312,361},{-312,248.178}}, color={0,0,127}));
  connect(perimeterBotGains3.u2, demux.y[17:17]) annotation (Line(points={{-196,
          354},{-204,354},{-204,352},{-312,352},{-312,247.867}}, color={0,0,127}));
  connect(perimeterBotGains3.u3, demux.y[18:18]) annotation (Line(points={{-196,
          347},{-312,347},{-312,247.556}}, color={0,0,127}));
  connect(perimeterBotGains4.u1, demux.y[19:19]) annotation (Line(points={{-196,
          335},{-206,335},{-206,336},{-312,336},{-312,247.244}}, color={0,0,127}));
  connect(perimeterBotGains4.u2, demux.y[20:20]) annotation (Line(points={{-196,
          328},{-202,328},{-202,326},{-312,326},{-312,246.933}}, color={0,0,127}));
  connect(perimeterBotGains4.u3, demux.y[21:21]) annotation (Line(points={{-196,
          321},{-202,321},{-202,320},{-312,320},{-312,246.622}}, color={0,0,127}));
  connect(perimeterMidGains1.u1, demux.y[22:22]) annotation (Line(points={{-196,
          309},{-200,309},{-200,308},{-312,308},{-312,246.311}}, color={0,0,127}));
  connect(perimeterMidGains1.u2, demux.y[23:23]) annotation (Line(points={{-196,
          302},{-312,302},{-312,246}}, color={0,0,127}));
  connect(perimeterMidGains1.u3, demux.y[24:24]) annotation (Line(points={{-196,
          295},{-312,295},{-312,245.689}}, color={0,0,127}));
  connect(perimeterMidGains2.u1, demux.y[25:25]) annotation (Line(points={{-196,
          281},{-312,281},{-312,245.378}}, color={0,0,127}));
  connect(perimeterMidGains2.u2, demux.y[26:26]) annotation (Line(points={{-196,
          274},{-312,274},{-312,245.067}}, color={0,0,127}));
  connect(perimeterMidGains2.u3, demux.y[27:27]) annotation (Line(points={{-196,
          267},{-255,267},{-255,244.756},{-312,244.756}}, color={0,0,127}));
  connect(perimeterMidGains3.u1, demux.y[28:28]) annotation (Line(points={{-196,
          255},{-254,255},{-254,244.444},{-312,244.444}}, color={0,0,127}));
  connect(perimeterMidGains3.u2, demux.y[29:29]) annotation (Line(points={{-196,
          248},{-254,248},{-254,244.133},{-312,244.133}}, color={0,0,127}));
  connect(perimeterMidGains3.u3, demux.y[30:30]) annotation (Line(points={{-196,
          241},{-256,241},{-256,243.822},{-312,243.822}}, color={0,0,127}));
  connect(perimeterMidGains4.u1, demux.y[31:31]) annotation (Line(points={{-196,
          229},{-312,229},{-312,243.511}}, color={0,0,127}));
  connect(perimeterMidGains4.u2, demux.y[32:32]) annotation (Line(points={{-196,
          222},{-254,222},{-254,243.2},{-312,243.2}}, color={0,0,127}));
  connect(perimeterMidGains4.u3, demux.y[33:33]) annotation (Line(points={{-196,
          215},{-254,215},{-254,242.889},{-312,242.889}}, color={0,0,127}));
  connect(perimeterTopGains1.u1, demux.y[34:34]) annotation (Line(points={{-196,
          203},{-254,203},{-254,242.578},{-312,242.578}}, color={0,0,127}));
  connect(perimeterTopGains1.u2, demux.y[35:35]) annotation (Line(points={{-196,
          196},{-254,196},{-254,242.267},{-312,242.267}}, color={0,0,127}));
  connect(perimeterTopGains1.u3, demux.y[36:36]) annotation (Line(points={{-196,
          189},{-254,189},{-254,241.956},{-312,241.956}}, color={0,0,127}));
  connect(perimeterTopGains2.u1, demux.y[37:37]) annotation (Line(points={{-196,
          175},{-254,175},{-254,241.644},{-312,241.644}}, color={0,0,127}));
  connect(perimeterTopGains2.u2, demux.y[38:38]) annotation (Line(points={{-196,
          168},{-254,168},{-254,241.333},{-312,241.333}}, color={0,0,127}));
  connect(perimeterTopGains2.u3, demux.y[39:39]) annotation (Line(points={{-196,
          161},{-254,161},{-254,241.022},{-312,241.022}}, color={0,0,127}));
  connect(perimeterTopGains3.u1, demux.y[40:40]) annotation (Line(points={{-196,
          147},{-254,147},{-254,240.711},{-312,240.711}}, color={0,0,127}));
  connect(perimeterTopGains3.u2, demux.y[41:41]) annotation (Line(points={{-196,
          140},{-254,140},{-254,240.4},{-312,240.4}}, color={0,0,127}));
  connect(perimeterTopGains3.u3, demux.y[42:42]) annotation (Line(points={{-196,
          133},{-254,133},{-254,240.089},{-312,240.089}}, color={0,0,127}));
  connect(perimeterTopGains4.u1, demux.y[43:43]) annotation (Line(points={{-196,
          121},{-196,182.5},{-312,182.5},{-312,239.778}}, color={0,0,127}));
  connect(perimeterTopGains4.u2, demux.y[44:44]) annotation (Line(points={{-196,
          114},{-254,114},{-254,239.467},{-312,239.467}}, color={0,0,127}));
  connect(perimeterTopGains4.u3, demux.y[45:45]) annotation (Line(points={{-196,
          107},{-254,107},{-254,239.156},{-312,239.156}}, color={0,0,127}));
  connect(Core_bottom.qGai_flow, coreBottomGains.y) annotation (Line(points={{
          -72,102},{-98,102},{-98,106},{-118,106},{-118,486},{-173,486}}, color
        ={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    uses(                            Modelica(version="3.2.3"), Buildings(
          version="9.0.0")),
    experiment(
      StopTime=604800,
      Interval=600,
      __Dymola_Algorithm="Dassl"),
    version="1");
end dev_mzvav;
