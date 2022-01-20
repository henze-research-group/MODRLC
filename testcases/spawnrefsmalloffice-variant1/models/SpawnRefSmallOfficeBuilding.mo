within ;
model SpawnRefSmallOfficeBuildingvariant1
  "Spawn replica of the Reference Small Office Building"

  //Parameters//
  Real OAInfCore = 0.121 "OA infiltration in the core zone";
  Real OAInfP1 = 0.089 "OA infiltration in the perimeter zone 1";
  Real OAInfP2 = 0.101 "OA infiltration in the perimeter zone 2";
  Real OAInfP3 = 0.089 "OA infiltration in the perimeter zone 3";
  Real OAInfP4 = 0.101 "OA infiltration in the perimeter zone 4";

  package Medium = Buildings.Media.Air "Moist Air"; // Moist air
model controller
  "Spawn reference small office building PSZACcontroller"
  parameter Real heaOccSet = 273.15 + 21 "Heating setpoint, occupied";
  parameter Real heaUnoSet = 273.15 + 15.6 "Heating setpoint, unoccupied";
  parameter Real cooOccSet = 273.15 + 24 "Cooling setpoint, occupied";
  parameter Real cooUnoSet = 273.15 + 26.7 "Cooling setpoint, unoccupied";
  parameter Real freProOn = 273.15 + 4 "Freeze protection start";
  parameter Real freProOff = 273.15 + 7 "Freeze protection stop";
  parameter Real heaCooOAVFR = 0.11 "OA volumetric vol. flow rate when coils are activated";
  parameter Real minOAVFR = 0.08 "Minimum OA vol. flow rate";
  parameter Real heaPIDk = 0.1 "Gain of heating coil PI control";
  parameter Real heaPIDTi = 200 "Integral term of heating coil PI control";
  parameter Real occDenCore = 0.0538 "Core zone occupant density";
  parameter Real areaCore = 149.657 "Core zone area";
  parameter Real occDenP1 = 0.0538 "Perimeter zone 1 occupant density";
  parameter Real areaP1 = 113.45 "Perimeter zone 1 area";
  parameter Real occDenP2 = 0.0538 "Perimeter zone 2 occupant density";
  parameter Real areaP2 = 67.3 "Perimeter zone 2 area";
  parameter Real occDenP3 = 0.0538 "Perimeter zone 3 occupant density";
  parameter Real areaP3 = 113.45 "Perimeter zone 3 area";
  parameter Real occDenP4 = 0.0538 "Perimeter zone 4 occupant density";
  parameter Real areaP4 = 67.3 "Perimeter zone 4 area";
  parameter Real pid_r=1 "typical range of control error for the pid block";
  parameter Real pid_ni = 0.9 "Anti-windup compensation";
  parameter Real PIDyMax = 1;
  parameter Real PIDyMin = 0;

  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSelCore(
    numZon=1,
    TZonFreProOn=freProOn,
    TZonFreProOff=freProOff)
    annotation (Placement(transformation(extent={{26,38},{46,70}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus corZonSta(
    THeaSetOcc=heaOccSet,
    THeaSetUno=heaUnoSet,
    TCooSetOcc=cooOccSet,
    TCooSetUno=cooUnoSet)
    annotation (Placement(transformation(extent={{-82,40},{-62,68}})));
  Modelica.Blocks.Sources.RealExpression cooWarTim(y=1800)
    "cooldown and warmup time"
    annotation (Placement(transformation(extent={{-158,86},{-138,106}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSetCore(
    have_occSen=false,
    have_winSen=false,
      ignDemLim=true)
    annotation (Placement(transformation(extent={{104,40},{124,68}})));
  Modelica.Blocks.Interfaces.RealInput uNextOcc annotation (Placement(
        transformation(extent={{-180,114},{-156,136}}), iconTransformation(
          extent={{-180,114},{-156,136}})));
  Modelica.Blocks.Interfaces.BooleanInput uOcc annotation (Placement(
        transformation(extent={{-182,154},{-156,178}}), iconTransformation(
          extent={{-182,154},{-156,178}})));
  Modelica.Blocks.Interfaces.RealInput uTCore annotation (Placement(
        transformation(extent={{-240,94},{-216,116}}), iconTransformation(
          extent={{-180,26},{-156,48}})));
  Modelica.Blocks.Interfaces.RealInput uTPer1 annotation (Placement(
        transformation(extent={{-240,72},{-216,94}}), iconTransformation(extent={{-180,
            -20},{-156,2}})));
  Modelica.Blocks.Interfaces.RealInput uTPer2 annotation (Placement(
        transformation(extent={{-240,48},{-216,70}}), iconTransformation(extent={{-180,
            -64},{-156,-42}})));
  Modelica.Blocks.Interfaces.RealInput uTPer3 annotation (Placement(
        transformation(extent={{-240,24},{-216,46}}), iconTransformation(extent={{-180,
            -108},{-156,-86}})));
  Modelica.Blocks.Interfaces.RealInput uTPer4 annotation (Placement(
        transformation(extent={{-240,2},{-216,24}}), iconTransformation(extent={{-178,
            -154},{-154,-132}})));
  Modelica.Blocks.Sources.IntegerExpression integerExpression
    annotation (Placement(transformation(extent={{-156,76},{-142,90}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSelP1(
    numZon=1,
    TZonFreProOn=freProOn,
    TZonFreProOff=freProOff)
    annotation (Placement(transformation(extent={{26,-32},{46,0}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus ZonStaP1(
    THeaSetOcc=heaOccSet,
    THeaSetUno=heaUnoSet,
    TCooSetOcc=cooOccSet,
    TCooSetUno=cooUnoSet)
    annotation (Placement(transformation(extent={{-80,-30},{-60,-2}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSetP1(
    have_occSen=false,
    have_winSen=false,
      ignDemLim=true)
    annotation (Placement(transformation(extent={{104,-30},{124,-2}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSelP2(
    numZon=1,
    TZonFreProOn=freProOn,
    TZonFreProOff=freProOff)
    annotation (Placement(transformation(extent={{26,-104},{46,-72}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus ZonStaP2(
    THeaSetOcc=heaOccSet,
    THeaSetUno=heaUnoSet,
    TCooSetOcc=cooOccSet,
    TCooSetUno=cooUnoSet)
    annotation (Placement(transformation(extent={{-80,-102},{-60,-74}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSetP2(
    have_occSen=false,
    have_winSen=false,
      ignDemLim=true)
    annotation (Placement(transformation(extent={{104,-102},{124,-74}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSelP3(
    numZon=1,
    TZonFreProOn=freProOn,
    TZonFreProOff=freProOff)
    annotation (Placement(transformation(extent={{26,-174},{46,-142}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus ZonStaP3(
    THeaSetOcc=heaOccSet,
    THeaSetUno=heaUnoSet,
    TCooSetOcc=cooOccSet,
    TCooSetUno=cooUnoSet)
    annotation (Placement(transformation(extent={{-80,-172},{-60,-144}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSetP3(
    have_occSen=false,
    have_winSen=false,
      ignDemLim=true)
    annotation (Placement(transformation(extent={{104,-172},{124,-144}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.OperationMode
    opeModSelP4(
    numZon=1,
    TZonFreProOn=freProOn,
    TZonFreProOff=freProOff)
    annotation (Placement(transformation(extent={{26,-244},{46,-212}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.Generic.SetPoints.ZoneStatus ZonStaP4(
    THeaSetOcc=heaOccSet,
    THeaSetUno=heaUnoSet,
    TCooSetOcc=cooOccSet,
    TCooSetUno=cooUnoSet)
    annotation (Placement(transformation(extent={{-80,-242},{-60,-214}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.TerminalUnits.SetPoints.ZoneTemperatures
    TZonSetP4(
    have_occSen=false,
    have_winSen=false,
      ignDemLim=true)
    annotation (Placement(transformation(extent={{104,-242},{124,-214}})));
  Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
    k=heaPIDk,
    Ti=heaPIDTi,
    r=pid_r,
    yMax=PIDyMax,
    yMin=PIDyMin,
    Ni=pid_ni,
      y_reset=0)
    annotation (Placement(transformation(extent={{156,60},{168,72}})));
  Buildings.Controls.OBC.CDL.Continuous.Greater gre1(h=0.01)
    annotation (Placement(transformation(extent={{192,54},{202,64}})));
  Modelica.Blocks.Sources.RealExpression zero(y=0.02)
                                                   "cooldown and warmup time"
    annotation (Placement(transformation(extent={{164,30},{182,48}})));
  Buildings.Controls.OBC.CDL.Logical.Or or1
    annotation (Placement(transformation(extent={{218,76},{228,86}})));
  Modelica.Blocks.Interfaces.RealOutput yHeaCor annotation (Placement(
        transformation(extent={{388,200},{408,220}}), iconTransformation(extent={{388,200},
            {408,220}})));
  Modelica.Blocks.Interfaces.BooleanOutput yCooCor annotation (Placement(
        transformation(extent={{388,230},{408,250}}), iconTransformation(extent={{388,230},
            {408,250}})));
  Modelica.Blocks.Interfaces.BooleanOutput yFanCor annotation (Placement(
        transformation(extent={{386,262},{406,282}}), iconTransformation(extent={{386,262},
            {406,282}})));
  Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID1(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
                                                             k=heaPIDk, Ti=
        heaPIDTi,
    r=pid_r,
    yMax=PIDyMax,
    yMin=PIDyMin,
    Ni=pid_ni,
      y_reset=0)
    annotation (Placement(transformation(extent={{156,-8},{168,4}})));
  Buildings.Controls.OBC.CDL.Continuous.Greater gre3(h=0.01)
    annotation (Placement(transformation(extent={{192,-14},{202,-4}})));
  Modelica.Blocks.Sources.RealExpression zero1(y=0.02)
                                                    "cooldown and warmup time"
    annotation (Placement(transformation(extent={{164,-38},{182,-20}})));
  Buildings.Controls.OBC.CDL.Logical.Or or3
    annotation (Placement(transformation(extent={{218,8},{228,18}})));
  Modelica.Blocks.Interfaces.RealOutput yHeaPer1 annotation (Placement(
        transformation(extent={{392,-4},{412,16}}), iconTransformation(extent={{
            160,66},{180,86}})));
  Modelica.Blocks.Interfaces.BooleanOutput yCooPer1 annotation (Placement(
        transformation(extent={{390,94},{410,114}}), iconTransformation(extent={{390,94},
            {410,114}})));
  Modelica.Blocks.Interfaces.BooleanOutput yFanPer1 annotation (Placement(
        transformation(extent={{390,124},{410,144}}), iconTransformation(extent={{390,124},
            {410,144}})));
  Modelica.Blocks.Interfaces.RealOutput yDamCor annotation (Placement(
        transformation(extent={{390,22},{410,42}}), iconTransformation(extent={{
            158,170},{178,190}})));
  Modelica.Blocks.Interfaces.RealOutput yDamPer1 annotation (Placement(
        transformation(extent={{390,-56},{410,-36}}), iconTransformation(extent=
           {{162,36},{182,56}})));
  Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID2(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
                                                             k=heaPIDk, Ti=
        heaPIDTi,
    r=pid_r,
    yMax=PIDyMax,
    yMin=PIDyMin,
    Ni=pid_ni,
      y_reset=0)
    annotation (Placement(transformation(extent={{154,-94},{166,-82}})));
  Buildings.Controls.OBC.CDL.Continuous.Greater gre5(h=0.01)
    annotation (Placement(transformation(extent={{190,-98},{200,-88}})));
  Modelica.Blocks.Sources.RealExpression zero2(y=0.02)
                                                    "cooldown and warmup time"
    annotation (Placement(transformation(extent={{162,-122},{180,-104}})));
  Buildings.Controls.OBC.CDL.Logical.Or or8
    annotation (Placement(transformation(extent={{216,-76},{226,-66}})));
  Modelica.Blocks.Interfaces.RealOutput yHeaPer2 annotation (Placement(
        transformation(extent={{388,-88},{408,-68}}), iconTransformation(extent=
           {{162,-70},{182,-50}})));
  Modelica.Blocks.Interfaces.BooleanOutput yCooPer2 annotation (Placement(
        transformation(extent={{390,-34},{410,-14}}), iconTransformation(extent={{390,-34},
            {410,-14}})));
  Modelica.Blocks.Interfaces.BooleanOutput yFanPer2 annotation (Placement(
        transformation(extent={{392,10},{412,30}}), iconTransformation(extent={{392,10},
            {412,30}})));
  Modelica.Blocks.Interfaces.RealOutput yDamPer2 annotation (Placement(
        transformation(extent={{388,-142},{408,-122}}), iconTransformation(
          extent={{160,-98},{180,-78}})));
  Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID3(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
                                                             k=heaPIDk, Ti=
        heaPIDTi,
    r=pid_r,
    yMax=PIDyMax,
    yMin=PIDyMin,
    Ni=pid_ni,
      y_reset=0)
    annotation (Placement(transformation(extent={{154,-172},{166,-160}})));
  Buildings.Controls.OBC.CDL.Continuous.Greater gre7(h=0.01)
    annotation (Placement(transformation(extent={{190,-178},{200,-168}})));
  Modelica.Blocks.Sources.RealExpression zero3(y=0.02)
                                                    "cooldown and warmup time"
    annotation (Placement(transformation(extent={{162,-202},{180,-184}})));
  Buildings.Controls.OBC.CDL.Logical.Or or10
    annotation (Placement(transformation(extent={{216,-156},{226,-146}})));
  Modelica.Blocks.Interfaces.RealOutput yHeaPer3 annotation (Placement(
        transformation(extent={{388,-170},{408,-150}}), iconTransformation(
          extent={{166,-198},{186,-178}})));
  Modelica.Blocks.Interfaces.BooleanOutput yCooPer3 annotation (Placement(
        transformation(extent={{388,-182},{408,-162}}), iconTransformation(
          extent={{388,-182},{408,-162}})));
  Modelica.Blocks.Interfaces.BooleanOutput yFanPer3 annotation (Placement(
        transformation(extent={{388,-154},{408,-134}}), iconTransformation(
          extent={{388,-154},{408,-134}})));
  Modelica.Blocks.Interfaces.RealOutput yDamPer3 annotation (Placement(
        transformation(extent={{388,-220},{408,-200}}), iconTransformation(
          extent={{166,-226},{186,-206}})));
  Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID4(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
                                                             k=heaPIDk, Ti=
        heaPIDTi,
    r=pid_r,
    yMax=PIDyMax,
    yMin=PIDyMin,
    Ni=pid_ni,
      y_reset=0)
    annotation (Placement(transformation(extent={{156,-260},{168,-248}})));
  Buildings.Controls.OBC.CDL.Continuous.Greater gre9(h=0.01)
    annotation (Placement(transformation(extent={{192,-266},{202,-256}})));
  Modelica.Blocks.Sources.RealExpression zero4(y=0.02)
                                                    "cooldown and warmup time"
    annotation (Placement(transformation(extent={{164,-290},{182,-272}})));
  Buildings.Controls.OBC.CDL.Logical.Or or13
    annotation (Placement(transformation(extent={{218,-244},{228,-234}})));
  Modelica.Blocks.Interfaces.RealOutput yHeaPer4 annotation (Placement(
        transformation(extent={{390,-258},{410,-238}}), iconTransformation(
          extent={{166,-326},{186,-306}})));
  Modelica.Blocks.Interfaces.BooleanOutput yCooPer4 annotation (Placement(
        transformation(extent={{392,-288},{412,-268}}), iconTransformation(
          extent={{392,-288},{412,-268}})));
  Modelica.Blocks.Interfaces.BooleanOutput yFanPer4 annotation (Placement(
        transformation(extent={{392,-268},{412,-248}}), iconTransformation(
          extent={{392,-268},{412,-248}})));
  Modelica.Blocks.Interfaces.RealOutput yDamPer4 annotation (Placement(
        transformation(extent={{392,-308},{412,-288}}), iconTransformation(
          extent={{166,-358},{186,-338}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaCor(description="Core zone heating coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{174,60},{184,70}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaPer1(description="Perimeter zone 1 heating coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{174,-8},{184,2}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaPer2(description="Perimeter zone 2 heating coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{170,-94},{180,-84}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaPer3(description="Perimeter zone 3 heating coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{170,-172},{180,-162}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaPer4(description="Perimeter zone 1 heating coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{172,-262},{182,-252}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea
    annotation (Placement(transformation(extent={{166,76},{176,86}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooCor(description="Core zone cooling coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{182,76},{192,86}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean
    annotation (Placement(transformation(extent={{198,78},{208,86}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea1
    annotation (Placement(transformation(extent={{166,8},{176,18}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooPer1(description="Perimeter zone 1 cooling coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{182,8},{192,18}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean1
    annotation (Placement(transformation(extent={{198,10},{208,18}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea2
    annotation (Placement(transformation(extent={{158,-76},{168,-66}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooPer2(description="Perimeter zone 2 cooling coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{174,-76},{184,-66}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean2
    annotation (Placement(transformation(extent={{190,-74},{200,-66}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea3
    annotation (Placement(transformation(extent={{158,-156},{168,-146}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooPer3(description="Perimeter zone 3 cooling coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{174,-156},{184,-146}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean3
    annotation (Placement(transformation(extent={{190,-154},{200,-146}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea4
    annotation (Placement(transformation(extent={{162,-244},{172,-234}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooPer4(description="Perimeter zone 4 cooling coil override", u(min=0.0, max=1.0, unit="1"))
    annotation (Placement(transformation(extent={{178,-244},{188,-234}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean4
    annotation (Placement(transformation(extent={{194,-242},{204,-234}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaStpPer4(description="Perimeter zone 4 heating setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{132,-256},{142,-246}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooStpPer4(description="Perimeter zone 4 cooling setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{132,-226},{142,-216}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooStpPer1(description="Perimeter zone 1 cooling setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{130,4},{140,14}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaStpPer1(description="Perimeter zone 1 heating setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{140,-8},{150,2}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaStpPer2(description="Perimeter zone 2 heating setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{134,-100},{144,-90}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooStpPer2(description="Perimeter zone 2 cooling setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{130,-84},{140,-74}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaStpPer3(description="Perimeter zone 3 heating setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{130,-168},{140,-158}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooStpPer3(description="Perimeter zone 3 cooling setpoint override",u( min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{126,-156},{136,-146}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveHeaStpCor(description="Core zone heating setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{130,42},{140,52}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveCooStpCor(description="Core zone cooling setpoint override", u(min=250.0, max=330.0, unit="K"))
    annotation (Placement(transformation(extent={{130,58},{140,68}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDamCor(description="Core zone damper override", u(min=0, max=0.5, unit="m3/s"))
    annotation (Placement(transformation(extent={{332,28},{340,36}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDamP1(description="Perimeter zone 1 damper override", u(min=0, max=0.5, unit="m3/s"))
    annotation (Placement(transformation(extent={{332,-50},{340,-42}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDamP2(description="Perimeter zone 2 damper override", u(min=0, max=0.5, unit="m3/s"))
    annotation (Placement(transformation(extent={{334,-138},{342,-130}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDamP3(description="Perimeter zone 3 damper override", u(min=0, max=0.5, unit="m3/s"))
    annotation (Placement(transformation(extent={{334,-214},{342,-206}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDamP4(description="Perimeter zone 4 damper override", u(min=0, max=0.5, unit="m3/s"))
    annotation (Placement(transformation(extent={{338,-302},{346,-294}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.SingleZone.VAV.SetPoints.OutsideAirFlow
    outAirSetPoiCor(
    AFlo=areaCore,
    have_occSen=false,
    occDen=occDenCore,
    zonDisEffHea=1)
    annotation (Placement(transformation(extent={{294,22},{314,42}})));
  Modelica.Blocks.Interfaces.RealInput uTDisCore annotation (Placement(
        transformation(extent={{-240,-26},{-216,-4}}), iconTransformation(
          extent={{-54,20},{-30,42}})));
  Modelica.Blocks.Interfaces.RealInput uTDisP1 annotation (Placement(
        transformation(extent={{-240,-50},{-216,-28}}), iconTransformation(
          extent={{-52,-20},{-28,2}})));
  Modelica.Blocks.Interfaces.RealInput uTDisP2 annotation (Placement(
        transformation(extent={{-240,-74},{-216,-52}}), iconTransformation(
          extent={{-54,-60},{-30,-38}})));
  Modelica.Blocks.Interfaces.RealInput uTDisP3 annotation (Placement(
        transformation(extent={{-240,-98},{-216,-76}}), iconTransformation(
          extent={{-56,-106},{-32,-84}})));
  Modelica.Blocks.Interfaces.RealInput uTDisP4 annotation (Placement(
        transformation(extent={{-240,-122},{-216,-100}}), iconTransformation(
          extent={{-54,-154},{-30,-132}})));
  Modelica.Blocks.Sources.BooleanConstant booleanConstant1(k=false)
    annotation (Placement(transformation(extent={{170,94},{182,106}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.SingleZone.VAV.SetPoints.OutsideAirFlow
    outAirSetPoiP1(
    AFlo=areaP1,
    have_occSen=false,
    occDen=occDenP1,
    zonDisEffHea=1)
    annotation (Placement(transformation(extent={{298,-56},{318,-36}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.SingleZone.VAV.SetPoints.OutsideAirFlow
    outAirSetPoiP2(
    AFlo=areaP2,
    have_occSen=false,
    occDen=occDenP2,
    zonDisEffHea=1)
    annotation (Placement(transformation(extent={{240,-140},{260,-120}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.SingleZone.VAV.SetPoints.OutsideAirFlow
    outAirSetPoiP3(
    AFlo=areaP3,
    have_occSen=false,
    occDen=occDenP3,
    zonDisEffHea=1)
    annotation (Placement(transformation(extent={{306,-208},{326,-188}})));
  Buildings.Controls.OBC.ASHRAE.G36_PR1.AHUs.SingleZone.VAV.SetPoints.OutsideAirFlow
    outAirSetPoiP4(
    AFlo=areaP4,
    have_occSen=false,
    occDen=occDenP4,
    zonDisEffHea=1)
    annotation (Placement(transformation(extent={{304,-308},{324,-288}})));
  Buildings.Controls.OBC.CDL.Logical.Or or2
    annotation (Placement(transformation(extent={{252,80},{262,90}})));
  Buildings.Controls.OBC.CDL.Logical.Or or4
    annotation (Placement(transformation(extent={{262,10},{272,20}})));
  Buildings.Controls.OBC.CDL.Logical.Or or5
    annotation (Placement(transformation(extent={{258,126},{268,136}})));
  Buildings.Controls.OBC.CDL.Logical.Or or6
    annotation (Placement(transformation(extent={{256,-154},{266,-144}})));
  Buildings.Controls.OBC.CDL.Logical.Or or7
    annotation (Placement(transformation(extent={{244,-240},{254,-230}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt
    annotation (Placement(transformation(extent={{-30,-112},{-22,-104}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt1
    annotation (Placement(transformation(extent={{-30,-122},{-22,-114}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt2
    annotation (Placement(transformation(extent={{-32,-186},{-24,-178}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt3
    annotation (Placement(transformation(extent={{-32,-196},{-24,-188}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt4
    annotation (Placement(transformation(extent={{-30,-254},{-22,-246}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt5
    annotation (Placement(transformation(extent={{-30,-264},{-22,-256}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt6
    annotation (Placement(transformation(extent={{-26,-44},{-18,-36}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt7
    annotation (Placement(transformation(extent={{-26,-54},{-18,-46}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt8
    annotation (Placement(transformation(extent={{-28,32},{-20,40}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt9
    annotation (Placement(transformation(extent={{-28,20},{-20,28}})));
  Buildings.Utilities.IO.SignalExchange.Overwrite oveDemandLimitLevel(
      description="Demand limit level", u(
      min=0,
      max=5,
      unit="1"))
    annotation (Placement(transformation(extent={{58,106},{68,116}})));
  Buildings.Controls.OBC.CDL.Conversions.RealToInteger reaToInt
    annotation (Placement(transformation(extent={{82,100},{102,120}})));
  Modelica.Blocks.Sources.RealExpression zero5(y=0)
                                                   "cooldown and warmup time"
    annotation (Placement(transformation(extent={{28,102},{46,120}})));
    Buildings.Controls.OBC.CDL.Logical.OnOffController onOffCon(bandwidth=1)
      annotation (Placement(transformation(extent={{146,88},{156,98}})));
    Buildings.Controls.OBC.CDL.Logical.Not not1
      annotation (Placement(transformation(extent={{158,90},{166,98}})));
    Buildings.Controls.OBC.CDL.Logical.OnOffController onOffCon1(bandwidth=1)
      annotation (Placement(transformation(extent={{144,8},{154,18}})));
    Buildings.Controls.OBC.CDL.Logical.Not not2
      annotation (Placement(transformation(extent={{154,10},{162,18}})));
    Buildings.Controls.OBC.CDL.Logical.OnOffController onOffCon2(bandwidth=1)
      annotation (Placement(transformation(extent={{134,-68},{144,-58}})));
    Buildings.Controls.OBC.CDL.Logical.Not not3
      annotation (Placement(transformation(extent={{150,-68},{158,-60}})));
    Buildings.Controls.OBC.CDL.Logical.OnOffController onOffCon3(bandwidth=1)
      annotation (Placement(transformation(extent={{136,-140},{146,-130}})));
    Buildings.Controls.OBC.CDL.Logical.Not not4
      annotation (Placement(transformation(extent={{148,-138},{156,-130}})));
    Buildings.Controls.OBC.CDL.Logical.OnOffController onOffCon4(bandwidth=1)
      annotation (Placement(transformation(extent={{156,-230},{166,-220}})));
    Buildings.Controls.OBC.CDL.Logical.Not not5
      annotation (Placement(transformation(extent={{172,-226},{180,-218}})));
equation
  connect(corZonSta.cooDowTim, cooWarTim.y) annotation (Line(points={{-84,62},{
            -114,62},{-114,96},{-137,96}},
                                    color={0,0,127}));
  connect(corZonSta.warUpTim, cooWarTim.y) annotation (Line(points={{-84,58},{
            -114,58},{-114,96},{-137,96}},
                                    color={0,0,127}));
  connect(uNextOcc, opeModSelCore.tNexOcc) annotation (Line(points={{-168,125},{
          -16,125},{-16,66},{24,66}}, color={0,0,127}));
  connect(uOcc, opeModSelCore.uOcc) annotation (Line(points={{-169,166},{-12,166},
          {-12,68},{24,68}}, color={255,0,255}));
  connect(uTCore, corZonSta.TZon) annotation (Line(points={{-228,105},{-162,105},
            {-162,46},{-84,46}},
                               color={0,0,127}));
  connect(opeModSelCore.yOpeMod, TZonSetCore.uOpeMod) annotation (Line(points={{
          48,54},{76,54},{76,67},{102,67}}, color={255,127,0}));
  connect(corZonSta.yCooTim, opeModSelCore.maxCooDowTim) annotation (Line(
        points={{-60,67},{-54,67},{-54,66},{24,66},{24,64}}, color={0,0,127}));
  connect(corZonSta.yHigOccCoo, opeModSelCore.uHigOccCoo) annotation (Line(
        points={{-60,55},{-20,55},{-20,62},{24,62}}, color={255,0,255}));
  connect(corZonSta.yWarTim, opeModSelCore.maxWarUpTim) annotation (Line(points={{-60,65},
            {-18,65},{-18,60},{24,60}},        color={0,0,127}));
  connect(corZonSta.yOccHeaHig, opeModSelCore.uOccHeaHig) annotation (Line(
        points={{-60,60},{-18,60},{-18,58},{24,58}}, color={255,0,255}));
  connect(corZonSta.yUnoHeaHig, opeModSelCore.uSetBac) annotation (Line(points={{-60,50},
            {-18,50},{-18,52},{24,52}},        color={255,0,255}));
  connect(corZonSta.yEndSetBac, opeModSelCore.uEndSetBac) annotation (Line(
        points={{-60,48},{-18,48},{-18,50},{24,50}}, color={255,0,255}));
  connect(corZonSta.yHigUnoCoo, opeModSelCore.uSetUp) annotation (Line(points={{-60,43},
            {-18,43},{-18,42},{24,42}},       color={255,0,255}));
  connect(corZonSta.yEndSetUp, opeModSelCore.uEndSetUp) annotation (Line(points={{-60,41},
            {-18,41},{-18,40},{24,40}},        color={255,0,255}));
  connect(integerExpression.y, opeModSelCore.uOpeWin) annotation (Line(points={{
          -141.3,83},{8,83},{8,56},{24,56}}, color={255,127,0}));
  connect(opeModSelCore.TZonMax, corZonSta.TZon) annotation (Line(points={{24,48},
            {-14,48},{-14,40},{-84,40},{-84,46}},        color={0,0,127}));
  connect(opeModSelCore.TZonMin, corZonSta.TZon) annotation (Line(points={{24,46},
            {20,46},{20,48},{-14,48},{-14,40},{-84,40},{-84,46}},        color={
          0,0,127}));
  connect(corZonSta.TCooSetOn, TZonSetCore.TZonCooSetOcc) annotation (Line(
        points={{-60,57},{-6,57},{-6,74},{92,74},{92,63},{102,63}}, color={0,0,127}));
  connect(corZonSta.TCooSetOff, TZonSetCore.TZonCooSetUno) annotation (Line(
        points={{-60,45},{-34,45},{-34,46},{-2,46},{-2,72},{88,72},{88,61},{102,
            61}},
                color={0,0,127}));
  connect(corZonSta.THeaSetOn, TZonSetCore.TZonHeaSetOcc) annotation (Line(
        points={{-60,62},{14,62},{14,36},{80,36},{80,58},{102,58}}, color={0,0,127}));
  connect(corZonSta.THeaSetOff, TZonSetCore.TZonHeaSetUno) annotation (Line(
        points={{-60,52},{12,52},{12,34},{82,34},{82,56},{102,56}}, color={0,0,127}));
  connect(uNextOcc, opeModSelP1.tNexOcc) annotation (Line(points={{-168,125},{-16,
          125},{-16,-4},{24,-4}}, color={0,0,127}));
  connect(uOcc, opeModSelP1.uOcc) annotation (Line(points={{-169,166},{-12,166},
          {-12,-2},{24,-2}}, color={255,0,255}));
  connect(opeModSelP1.yOpeMod, TZonSetP1.uOpeMod) annotation (Line(points={{48,-16},
          {76,-16},{76,-3},{102,-3}},
                                    color={255,127,0}));
  connect(ZonStaP1.yCooTim, opeModSelP1.maxCooDowTim) annotation (Line(points={{-58,-3},
          {-54,-3},{-54,-4},{24,-4},{24,-6}},         color={0,0,127}));
  connect(ZonStaP1.yHigOccCoo, opeModSelP1.uHigOccCoo) annotation (Line(points={{-58,-15},
          {-20,-15},{-20,-8},{24,-8}},       color={255,0,255}));
  connect(ZonStaP1.yWarTim, opeModSelP1.maxWarUpTim) annotation (Line(points={{-58,-5},
          {-18,-5},{-18,-10},{24,-10}},   color={0,0,127}));
  connect(ZonStaP1.yOccHeaHig, opeModSelP1.uOccHeaHig) annotation (Line(points={{-58,-10},
          {-18,-10},{-18,-12},{24,-12}},     color={255,0,255}));
  connect(ZonStaP1.yUnoHeaHig, opeModSelP1.uSetBac) annotation (Line(points={{-58,-20},
          {-18,-20},{-18,-18},{24,-18}},
                                      color={255,0,255}));
  connect(ZonStaP1.yEndSetBac, opeModSelP1.uEndSetBac) annotation (Line(points={{-58,-22},
          {-18,-22},{-18,-20},{24,-20}},     color={255,0,255}));
  connect(ZonStaP1.yHigUnoCoo, opeModSelP1.uSetUp) annotation (Line(points={{-58,-27},
          {-18,-27},{-18,-28},{24,-28}},  color={255,0,255}));
  connect(ZonStaP1.yEndSetUp, opeModSelP1.uEndSetUp) annotation (Line(points={{-58,-29},
          {-18,-29},{-18,-30},{24,-30}},    color={255,0,255}));
  connect(integerExpression.y, opeModSelP1.uOpeWin) annotation (Line(points={{-141.3,
          83},{8,83},{8,-14},{24,-14}},
                                    color={255,127,0}));
  connect(opeModSelP1.TZonMax, ZonStaP1.TZon) annotation (Line(points={{24,-22},
          {-14,-22},{-14,-30},{-84,-30},{-84,-24},{-82,-24}},
                                                          color={0,0,127}));
  connect(opeModSelP1.TZonMin, ZonStaP1.TZon) annotation (Line(points={{24,-24},
          {20,-24},{20,-22},{-14,-22},{-14,-30},{-84,-30},{-84,-24},{-82,-24}},
                                                                          color=
         {0,0,127}));
  connect(ZonStaP1.TCooSetOn, TZonSetP1.TZonCooSetOcc) annotation (Line(points={{-58,-13},
          {-6,-13},{-6,4},{92,4},{92,-7},{102,-7}},         color={0,0,127}));
  connect(ZonStaP1.TCooSetOff, TZonSetP1.TZonCooSetUno) annotation (Line(points={{-58,-25},
          {-34,-25},{-34,-24},{-2,-24},{-2,2},{88,2},{88,-9},{102,-9}},
        color={0,0,127}));
  connect(ZonStaP1.THeaSetOn, TZonSetP1.TZonHeaSetOcc) annotation (Line(points={{-58,-8},
          {14,-8},{14,-34},{80,-34},{80,-12},{102,-12}},      color={0,0,127}));
  connect(ZonStaP1.THeaSetOff, TZonSetP1.TZonHeaSetUno) annotation (Line(points={{-58,-18},
          {12,-18},{12,-36},{82,-36},{82,-14},{102,-14}},   color={0,0,127}));
  connect(uNextOcc, opeModSelP2.tNexOcc) annotation (Line(points={{-168,125},{-16,
          125},{-16,-76},{24,-76}}, color={0,0,127}));
  connect(uOcc, opeModSelP2.uOcc) annotation (Line(points={{-169,166},{-12,166},
          {-12,-74},{24,-74}}, color={255,0,255}));
  connect(opeModSelP2.yOpeMod, TZonSetP2.uOpeMod) annotation (Line(points={{48,-88},
          {76,-88},{76,-75},{102,-75}}, color={255,127,0}));
  connect(ZonStaP2.yCooTim, opeModSelP2.maxCooDowTim) annotation (Line(points={{-58,-75},
          {-54,-75},{-54,-76},{24,-76},{24,-78}},          color={0,0,127}));
  connect(ZonStaP2.yHigOccCoo, opeModSelP2.uHigOccCoo) annotation (Line(points={{-58,-87},
          {-20,-87},{-20,-80},{24,-80}},           color={255,0,255}));
  connect(ZonStaP2.yWarTim, opeModSelP2.maxWarUpTim) annotation (Line(points={{-58,-77},
          {-18,-77},{-18,-82},{24,-82}},      color={0,0,127}));
  connect(ZonStaP2.yOccHeaHig, opeModSelP2.uOccHeaHig) annotation (Line(points={{-58,-82},
          {-18,-82},{-18,-84},{24,-84}},           color={255,0,255}));
  connect(ZonStaP2.yUnoHeaHig, opeModSelP2.uSetBac) annotation (Line(points={{-58,-92},
          {-18,-92},{-18,-90},{24,-90}},      color={255,0,255}));
  connect(ZonStaP2.yEndSetBac, opeModSelP2.uEndSetBac) annotation (Line(points={{-58,-94},
          {-18,-94},{-18,-92},{24,-92}},           color={255,0,255}));
  connect(ZonStaP2.yHigUnoCoo, opeModSelP2.uSetUp) annotation (Line(points={{-58,-99},
          {-18,-99},{-18,-100},{24,-100}},    color={255,0,255}));
  connect(ZonStaP2.yEndSetUp, opeModSelP2.uEndSetUp) annotation (Line(points={{-58,
          -101},{-18,-101},{-18,-102},{24,-102}},
                                              color={255,0,255}));
  connect(integerExpression.y, opeModSelP2.uOpeWin) annotation (Line(points={{-141.3,
          83},{8,83},{8,-86},{24,-86}}, color={255,127,0}));
  connect(opeModSelP2.TZonMax, ZonStaP2.TZon) annotation (Line(points={{24,-94},
          {-14,-94},{-14,-102},{-84,-102},{-84,-96},{-82,-96}},
                                                              color={0,0,127}));
  connect(opeModSelP2.TZonMin, ZonStaP2.TZon) annotation (Line(points={{24,-96},
          {20,-96},{20,-94},{-14,-94},{-14,-102},{-84,-102},{-84,-96},{-82,-96}},
        color={0,0,127}));
  connect(ZonStaP2.TCooSetOn, TZonSetP2.TZonCooSetOcc) annotation (Line(points={{-58,-85},
          {-6,-85},{-6,-68},{92,-68},{92,-79},{102,-79}},           color={0,0,127}));
  connect(ZonStaP2.TCooSetOff, TZonSetP2.TZonCooSetUno) annotation (Line(points={{-58,-97},
          {-34,-97},{-34,-96},{-2,-96},{-2,-70},{88,-70},{88,-81},{102,-81}},
                 color={0,0,127}));
  connect(ZonStaP2.THeaSetOn, TZonSetP2.TZonHeaSetOcc) annotation (Line(points={{-58,-80},
          {14,-80},{14,-106},{80,-106},{80,-84},{102,-84}},         color={0,0,127}));
  connect(ZonStaP2.THeaSetOff, TZonSetP2.TZonHeaSetUno) annotation (Line(points={{-58,-90},
          {12,-90},{12,-108},{82,-108},{82,-86},{102,-86}},         color={0,0,127}));
  connect(uNextOcc, opeModSelP3.tNexOcc) annotation (Line(points={{-168,125},{-16,
          125},{-16,-146},{24,-146}},
                                    color={0,0,127}));
  connect(uOcc, opeModSelP3.uOcc) annotation (Line(points={{-169,166},{-12,166},
          {-12,-144},{24,-144}},
                               color={255,0,255}));
  connect(opeModSelP3.yOpeMod, TZonSetP3.uOpeMod) annotation (Line(points={{48,-158},
          {76,-158},{76,-145},{102,-145}},
                                        color={255,127,0}));
  connect(ZonStaP3.yCooTim, opeModSelP3.maxCooDowTim) annotation (Line(points={{-58,
          -145},{-54,-145},{-54,-146},{24,-146},{24,-148}},color={0,0,127}));
  connect(ZonStaP3.yHigOccCoo, opeModSelP3.uHigOccCoo) annotation (Line(points={{-58,
          -157},{-20,-157},{-20,-150},{24,-150}},  color={255,0,255}));
  connect(ZonStaP3.yWarTim, opeModSelP3.maxWarUpTim) annotation (Line(points={{-58,
          -147},{-18,-147},{-18,-152},{24,-152}},
                                              color={0,0,127}));
  connect(ZonStaP3.yOccHeaHig, opeModSelP3.uOccHeaHig) annotation (Line(points={{-58,
          -152},{-18,-152},{-18,-154},{24,-154}},  color={255,0,255}));
  connect(ZonStaP3.yUnoHeaHig, opeModSelP3.uSetBac) annotation (Line(points={{-58,
          -162},{-18,-162},{-18,-160},{24,-160}},
                                              color={255,0,255}));
  connect(ZonStaP3.yEndSetBac, opeModSelP3.uEndSetBac) annotation (Line(points={{-58,
          -164},{-18,-164},{-18,-162},{24,-162}},  color={255,0,255}));
  connect(ZonStaP3.yHigUnoCoo, opeModSelP3.uSetUp) annotation (Line(points={{-58,
          -169},{-18,-169},{-18,-170},{24,-170}}, color={255,0,255}));
  connect(ZonStaP3.yEndSetUp, opeModSelP3.uEndSetUp) annotation (Line(points={{-58,
          -171},{-18,-171},{-18,-172},{24,-172}}, color={255,0,255}));
  connect(integerExpression.y, opeModSelP3.uOpeWin) annotation (Line(points={{-141.3,
          83},{8,83},{8,-156},{24,-156}},
                                        color={255,127,0}));
  connect(opeModSelP3.TZonMax, ZonStaP3.TZon) annotation (Line(points={{24,-164},
          {-14,-164},{-14,-172},{-84,-172},{-84,-166},{-82,-166}},
                                                                color={0,0,127}));
  connect(opeModSelP3.TZonMin, ZonStaP3.TZon) annotation (Line(points={{24,-166},
          {20,-166},{20,-164},{-14,-164},{-14,-172},{-84,-172},{-84,-166},{-82,-166}},
        color={0,0,127}));
  connect(ZonStaP3.TCooSetOn, TZonSetP3.TZonCooSetOcc) annotation (Line(points={{-58,
          -155},{-6,-155},{-6,-138},{92,-138},{92,-149},{102,-149}},color={0,0,127}));
  connect(ZonStaP3.TCooSetOff, TZonSetP3.TZonCooSetUno) annotation (Line(points={{-58,
          -167},{-34,-167},{-34,-166},{-2,-166},{-2,-140},{88,-140},{88,-151},{102,
          -151}},color={0,0,127}));
  connect(ZonStaP3.THeaSetOn, TZonSetP3.TZonHeaSetOcc) annotation (Line(points={{-58,
          -150},{14,-150},{14,-176},{80,-176},{80,-154},{102,-154}},  color={0,0,
          127}));
  connect(ZonStaP3.THeaSetOff, TZonSetP3.TZonHeaSetUno) annotation (Line(points={{-58,
          -160},{12,-160},{12,-178},{82,-178},{82,-156},{102,-156}},  color={0,0,
          127}));
  connect(uNextOcc, opeModSelP4.tNexOcc) annotation (Line(points={{-168,125},{-16,
          125},{-16,-216},{24,-216}}, color={0,0,127}));
  connect(uOcc, opeModSelP4.uOcc) annotation (Line(points={{-169,166},{-12,166},
          {-12,-214},{24,-214}}, color={255,0,255}));
  connect(opeModSelP4.yOpeMod, TZonSetP4.uOpeMod) annotation (Line(points={{48,-228},
          {76,-228},{76,-215},{102,-215}}, color={255,127,0}));
  connect(ZonStaP4.yCooTim, opeModSelP4.maxCooDowTim) annotation (Line(points={{-58,
          -215},{-54,-215},{-54,-216},{24,-216},{24,-218}},     color={0,0,127}));
  connect(ZonStaP4.yHigOccCoo, opeModSelP4.uHigOccCoo) annotation (Line(points={{-58,
          -227},{-20,-227},{-20,-220},{24,-220}},      color={255,0,255}));
  connect(ZonStaP4.yWarTim, opeModSelP4.maxWarUpTim) annotation (Line(points={{-58,
          -217},{-18,-217},{-18,-222},{24,-222}}, color={0,0,127}));
  connect(ZonStaP4.yOccHeaHig, opeModSelP4.uOccHeaHig) annotation (Line(points={{-58,
          -222},{-18,-222},{-18,-224},{24,-224}},      color={255,0,255}));
  connect(ZonStaP4.yUnoHeaHig, opeModSelP4.uSetBac) annotation (Line(points={{-58,
          -232},{-18,-232},{-18,-230},{24,-230}}, color={255,0,255}));
  connect(ZonStaP4.yEndSetBac, opeModSelP4.uEndSetBac) annotation (Line(points={{-58,
          -234},{-18,-234},{-18,-232},{24,-232}},      color={255,0,255}));
  connect(ZonStaP4.yHigUnoCoo, opeModSelP4.uSetUp) annotation (Line(points={{-58,
          -239},{-18,-239},{-18,-240},{24,-240}}, color={255,0,255}));
  connect(ZonStaP4.yEndSetUp, opeModSelP4.uEndSetUp) annotation (Line(points={{-58,
          -241},{-18,-241},{-18,-242},{24,-242}}, color={255,0,255}));
  connect(integerExpression.y, opeModSelP4.uOpeWin) annotation (Line(points={{-141.3,
          83},{8,83},{8,-226},{24,-226}}, color={255,127,0}));
  connect(opeModSelP4.TZonMax, ZonStaP4.TZon) annotation (Line(points={{24,-234},
          {-14,-234},{-14,-242},{-84,-242},{-84,-236},{-82,-236}}, color={0,0,127}));
  connect(opeModSelP4.TZonMin, ZonStaP4.TZon) annotation (Line(points={{24,-236},
          {20,-236},{20,-234},{-14,-234},{-14,-242},{-84,-242},{-84,-236},{-82,-236}},
        color={0,0,127}));
  connect(ZonStaP4.TCooSetOn, TZonSetP4.TZonCooSetOcc) annotation (Line(points={{-58,
          -225},{-6,-225},{-6,-208},{92,-208},{92,-219},{102,-219}},      color=
         {0,0,127}));
  connect(ZonStaP4.TCooSetOff, TZonSetP4.TZonCooSetUno) annotation (Line(points={{-58,
          -237},{-34,-237},{-34,-236},{-2,-236},{-2,-210},{88,-210},{88,-221},{102,
          -221}},      color={0,0,127}));
  connect(ZonStaP4.THeaSetOn, TZonSetP4.TZonHeaSetOcc) annotation (Line(points={{-58,
          -220},{14,-220},{14,-246},{80,-246},{80,-224},{102,-224}},      color=
         {0,0,127}));
  connect(ZonStaP4.THeaSetOff, TZonSetP4.TZonHeaSetUno) annotation (Line(points={{-58,
          -230},{12,-230},{12,-248},{82,-248},{82,-226},{102,-226}},      color=
         {0,0,127}));
  connect(uTPer1, ZonStaP1.TZon) annotation (Line(points={{-228,83},{-166,83},{-166,
          -24},{-82,-24}},
                         color={0,0,127}));
  connect(uTPer2, ZonStaP2.TZon) annotation (Line(points={{-228,59},{-176,59},{-176,
          -96},{-82,-96}}, color={0,0,127}));
  connect(uTPer3, ZonStaP3.TZon) annotation (Line(points={{-228,35},{-188,35},{-188,
          -166},{-82,-166}},
                           color={0,0,127}));
  connect(uTPer4, ZonStaP4.TZon) annotation (Line(points={{-228,13},{-200,13},{-200,
          -236},{-82,-236}}, color={0,0,127}));
  connect(ZonStaP1.cooDowTim, cooWarTim.y) annotation (Line(points={{-82,-8},{-88,
          -8},{-88,14},{-114,14},{-114,96},{-137,96}}, color={0,0,127}));
  connect(ZonStaP1.warUpTim, cooWarTim.y) annotation (Line(points={{-82,-12},{-86,
          -12},{-86,14},{-114,14},{-114,96},{-137,96}},
                                                      color={0,0,127}));
  connect(ZonStaP2.cooDowTim, cooWarTim.y) annotation (Line(points={{-82,-80},{-114,
          -80},{-114,96},{-137,96}}, color={0,0,127}));
  connect(ZonStaP2.warUpTim, cooWarTim.y) annotation (Line(points={{-82,-84},{-86,
          -84},{-86,-34},{-114,-34},{-114,96},{-137,96}}, color={0,0,127}));
  connect(ZonStaP3.cooDowTim, cooWarTim.y) annotation (Line(points={{-82,-150},{
          -114,-150},{-114,96},{-137,96}},
                                     color={0,0,127}));
  connect(ZonStaP3.warUpTim, cooWarTim.y) annotation (Line(points={{-82,-154},{-86,
          -154},{-86,-82},{-114,-82},{-114,96},{-137,96}},color={0,0,127}));
  connect(ZonStaP4.cooDowTim, cooWarTim.y) annotation (Line(points={{-82,-220},{
          -114,-220},{-114,96},{-137,96}}, color={0,0,127}));
  connect(ZonStaP4.warUpTim, cooWarTim.y) annotation (Line(points={{-82,-224},{-86,
          -224},{-86,-136},{-114,-136},{-114,96},{-137,96}}, color={0,0,127}));
  connect(conPID.u_m, corZonSta.TZon) annotation (Line(points={{162,58.8},{162,
            34},{-84,34},{-84,46}},    color={0,0,127}));
  connect(zero.y, gre1.u2) annotation (Line(points={{182.9,39},{188,39},{188,55},
          {191,55}}, color={0,0,127}));
  connect(gre1.y, or1.u2) annotation (Line(points={{203,59},{210.5,59},{210.5,77},
          {217,77}}, color={255,0,255}));
  connect(yHeaCor, gre1.u1) annotation (Line(points={{398,210},{238,210},{238,66},
          {186,66},{186,59},{191,59}}, color={0,0,127}));
  connect(yCooCor, or1.u1) annotation (Line(points={{398,240},{204,240},{204,81},
          {217,81}}, color={255,0,255}));
  connect(zero1.y, gre3.u2) annotation (Line(points={{182.9,-29},{188,-29},{188,
          -13},{191,-13}}, color={0,0,127}));
  connect(gre3.y, or3.u2) annotation (Line(points={{203,-9},{210.5,-9},{210.5,9},
          {217,9}}, color={255,0,255}));
  connect(yHeaPer1, gre3.u1) annotation (Line(points={{402,6},{238,6},{238,-2},{
          186,-2},{186,-9},{191,-9}}, color={0,0,127}));
  connect(yCooPer1, or3.u1) annotation (Line(points={{400,104},{212,104},{212,13},
          {217,13}}, color={255,0,255}));
  connect(conPID1.u_m, ZonStaP1.TZon) annotation (Line(points={{162,-9.2},{162,-16},
          {142,-16},{142,13},{-82,13},{-82,-24}}, color={0,0,127}));
  connect(zero2.y, gre5.u2) annotation (Line(points={{180.9,-113},{186,-113},{186,
          -97},{189,-97}}, color={0,0,127}));
  connect(gre5.y, or8.u2) annotation (Line(points={{201,-93},{208.5,-93},{208.5,
          -75},{215,-75}}, color={255,0,255}));
  connect(yHeaPer2, gre5.u1) annotation (Line(points={{398,-78},{236,-78},{236,-86},
          {184,-86},{184,-93},{189,-93}}, color={0,0,127}));
  connect(yCooPer2, or8.u1) annotation (Line(points={{400,-24},{202,-24},{202,-71},
          {215,-71}}, color={255,0,255}));
  connect(zero3.y, gre7.u2) annotation (Line(points={{180.9,-193},{186,-193},{186,
          -177},{189,-177}}, color={0,0,127}));
  connect(gre7.y, or10.u2) annotation (Line(points={{201,-173},{208.5,-173},{208.5,
          -155},{215,-155}}, color={255,0,255}));
  connect(yHeaPer3, gre7.u1) annotation (Line(points={{398,-160},{236,-160},{236,
          -166},{184,-166},{184,-173},{189,-173}}, color={0,0,127}));
  connect(yCooPer3, or10.u1) annotation (Line(points={{398,-172},{202,-172},{202,
          -151},{215,-151}}, color={255,0,255}));
  connect(conPID3.u_m, ZonStaP3.TZon) annotation (Line(points={{160,-173.2},{150,
          -173.2},{150,-176},{-84,-176},{-84,-166},{-82,-166}}, color={0,0,127}));
  connect(zero4.y, gre9.u2) annotation (Line(points={{182.9,-281},{188,-281},{188,
          -265},{191,-265}}, color={0,0,127}));
  connect(gre9.y, or13.u2) annotation (Line(points={{203,-261},{210.5,-261},{210.5,
          -243},{217,-243}}, color={255,0,255}));
  connect(yHeaPer4, gre9.u1) annotation (Line(points={{400,-248},{238,-248},{238,
          -254},{186,-254},{186,-261},{191,-261}}, color={0,0,127}));
  connect(yCooPer4, or13.u1) annotation (Line(points={{402,-278},{204,-278},{204,
          -239},{217,-239}}, color={255,0,255}));
  connect(TZonSetCore.uHeaDemLimLev, TZonSetCore.uCooDemLimLev) annotation (
      Line(points={{102,46},{96,46},{96,48},{102,48}}, color={255,127,0}));
  connect(TZonSetP2.uCooDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}}, color=
         {255,127,0}));
  connect(TZonSetP1.uCooDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-22},{98,-22},{98,48},{102,48}}, color={255,127,0}));
  connect(TZonSetP1.uHeaDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-24},{100,-24},{100,-22},{98,-22},{98,48},{102,48}}, color=
         {255,127,0}));
  connect(TZonSetP2.uHeaDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-96},{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}},
        color={255,127,0}));
  connect(TZonSetP3.uCooDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-164},{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}},
        color={255,127,0}));
  connect(TZonSetP3.uHeaDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-166},{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}},
        color={255,127,0}));
  connect(TZonSetP4.uCooDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-234},{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}},
        color={255,127,0}));
  connect(TZonSetP4.uHeaDemLimLev, TZonSetCore.uCooDemLimLev) annotation (Line(
        points={{102,-236},{102,-94},{100,-94},{100,-22},{98,-22},{98,48},{102,48}},
        color={255,127,0}));
  connect(conPID.y, oveHeaCor.u) annotation (Line(points={{169.2,66},{172,66},{
            172,65},{173,65}},
                         color={0,0,127}));
  connect(oveHeaCor.y, gre1.u1) annotation (Line(points={{184.5,65},{186,65},{186,
          59},{191,59}}, color={0,0,127}));
  connect(conPID1.y, oveHeaPer1.u) annotation (Line(points={{169.2,-2},{172,-2},
            {172,-3},{173,-3}},
                              color={0,0,127}));
  connect(oveHeaPer1.y, gre3.u1) annotation (Line(points={{184.5,-3},{186,-3},{
            186,-9},{191,-9}},
                         color={0,0,127}));
  connect(conPID2.y, oveHeaPer2.u) annotation (Line(points={{167.2,-88},{168,-88},
          {168,-89},{169,-89}}, color={0,0,127}));
  connect(oveHeaPer2.y, gre5.u1) annotation (Line(points={{180.5,-89},{184,-89},
          {184,-93},{189,-93}}, color={0,0,127}));
  connect(conPID3.y, oveHeaPer3.u) annotation (Line(points={{167.2,-166},{168,-166},
          {168,-167},{169,-167}}, color={0,0,127}));
  connect(oveHeaPer3.y, gre7.u1) annotation (Line(points={{180.5,-167},{184,-168},
          {184,-173},{189,-173}}, color={0,0,127}));
  connect(oveHeaPer4.u, conPID4.y) annotation (Line(points={{171,-257},{171,-254},
          {169.2,-254}}, color={0,0,127}));
  connect(oveHeaPer4.y, gre9.u1) annotation (Line(points={{182.5,-257},{186,-258},
          {186,-261},{191,-261}}, color={0,0,127}));
  connect(booToRea.y, oveCooCor.u)
    annotation (Line(points={{177,81},{181,81}}, color={0,0,127}));
  connect(oveCooCor.y, realToBoolean.u) annotation (Line(points={{192.5,81},{192,
          81},{192,82},{197,82}}, color={0,0,127}));
  connect(realToBoolean.y, or1.u1) annotation (Line(points={{208.5,82},{210,82},
          {210,81},{217,81}}, color={255,0,255}));
  connect(booToRea1.y, oveCooPer1.u)
    annotation (Line(points={{177,13},{181,13}}, color={0,0,127}));
  connect(oveCooPer1.y, realToBoolean1.u) annotation (Line(points={{192.5,13},{
            186,13},{186,14},{197,14}},
                                  color={0,0,127}));
  connect(realToBoolean1.y, or3.u1) annotation (Line(points={{208.5,14},{204,14},
            {204,13},{217,13}},
                              color={255,0,255}));
  connect(booToRea2.y, oveCooPer2.u)
    annotation (Line(points={{169,-71},{173,-71}}, color={0,0,127}));
  connect(oveCooPer2.y, realToBoolean2.u) annotation (Line(points={{184.5,-71},{
          184,-71},{184,-70},{189,-70}}, color={0,0,127}));
  connect(realToBoolean2.y, or8.u1) annotation (Line(points={{200.5,-70},{202,-70},
          {202,-71},{215,-71}}, color={255,0,255}));
  connect(booToRea3.y, oveCooPer3.u)
    annotation (Line(points={{169,-151},{173,-151}}, color={0,0,127}));
  connect(oveCooPer3.y, realToBoolean3.u) annotation (Line(points={{184.5,-151},
          {184,-151},{184,-150},{189,-150}}, color={0,0,127}));
  connect(realToBoolean3.y, or10.u1) annotation (Line(points={{200.5,-150},{202,
          -150},{202,-151},{215,-151}}, color={255,0,255}));
  connect(booToRea4.y, oveCooPer4.u)
    annotation (Line(points={{173,-239},{177,-239}}, color={0,0,127}));
  connect(oveCooPer4.y, realToBoolean4.u) annotation (Line(points={{188.5,-239},
          {188,-239},{188,-238},{193,-238}}, color={0,0,127}));
  connect(realToBoolean4.y, or13.u1) annotation (Line(points={{204.5,-238},{206,
          -238},{206,-240},{208,-240},{208,-239},{217,-239}}, color={255,0,255}));
  connect(oveHeaStpPer4.u, TZonSetP4.TZonHeaSet) annotation (Line(points={{131,-251},
          {131,-238.5},{126,-238.5},{126,-228}}, color={0,0,127}));
  connect(TZonSetP4.TZonCooSet, oveCooStpPer4.u) annotation (Line(points={{126,-220},
          {128,-220},{128,-221},{131,-221}}, color={0,0,127}));
  connect(TZonSetP1.TZonCooSet, oveCooStpPer1.u) annotation (Line(points={{126,-8},
          {128,-8},{128,9},{129,9}}, color={0,0,127}));
  connect(TZonSetP1.TZonHeaSet, oveHeaStpPer1.u) annotation (Line(points={{126,-16},
          {132,-16},{132,-3},{139,-3}}, color={0,0,127}));
  connect(oveCooStpPer2.u, TZonSetP2.TZonCooSet) annotation (Line(points={{129,-79},
          {127.5,-79},{127.5,-80},{126,-80}}, color={0,0,127}));
  connect(TZonSetP2.TZonHeaSet, oveHeaStpPer2.u) annotation (Line(points={{126,-88},
            {132,-88},{132,-95},{133,-95}},
                                          color={0,0,127}));
  connect(oveCooStpPer3.u, TZonSetP3.TZonCooSet) annotation (Line(points={{125,-151},
          {127.5,-151},{127.5,-150},{126,-150}}, color={0,0,127}));
  connect(TZonSetP3.TZonHeaSet, oveHeaStpPer3.u) annotation (Line(points={{126,-158},
          {128,-158},{128,-163},{129,-163}}, color={0,0,127}));
  connect(oveCooStpCor.u, TZonSetCore.TZonCooSet) annotation (Line(points={{129,
          63},{127.5,63},{127.5,62},{126,62}}, color={0,0,127}));
  connect(oveHeaStpCor.u, TZonSetCore.TZonHeaSet) annotation (Line(points={{129,
          47},{129,50.5},{126,50.5},{126,54}}, color={0,0,127}));
  connect(yDamCor, oveDamCor.y)
    annotation (Line(points={{400,32},{340.4,32}}, color={0,0,127}));
  connect(yDamPer1, oveDamP1.y) annotation (Line(points={{400,-46},{340.4,-46}},
                             color={0,0,127}));
  connect(yDamPer2, oveDamP2.y) annotation (Line(points={{398,-132},{280,-132},{
          280,-134},{342.4,-134}}, color={0,0,127}));
  connect(yDamPer3, oveDamP3.y) annotation (Line(points={{398,-210},{342.4,-210}},
                                   color={0,0,127}));
  connect(yDamPer4, oveDamP4.y) annotation (Line(points={{402,-298},{346.4,-298}},
                                   color={0,0,127}));
  connect(outAirSetPoiCor.VOutMinSet_flow, oveDamCor.u)
    annotation (Line(points={{316,32},{268,32},{268,36},{272,36},{272,32},{331.2,
          32}},                                    color={0,0,127}));
  connect(outAirSetPoiCor.uOpeMod, TZonSetCore.uOpeMod) annotation (Line(points={{292,23},
          {152,23},{152,24},{76,24},{76,67},{102,67}},          color={255,127,0}));
  connect(uTDisCore, outAirSetPoiCor.TDis) annotation (Line(points={{-228,-15},{
          -132,-15},{-132,29},{292,29}}, color={0,0,127}));
  connect(outAirSetPoiCor.TZon, corZonSta.TZon) annotation (Line(points={{292,32},
          {158,32},{158,34},{-84,34},{-84,46}},          color={0,0,127}));
  connect(booleanConstant1.y, outAirSetPoiCor.uWin) annotation (Line(points={{182.6,
          100},{218,100},{218,36},{292,36}}, color={255,0,255}));
  connect(oveDamP1.u, outAirSetPoiP1.VOutMinSet_flow)
    annotation (Line(points={{331.2,-46},{270,-46},{270,-42},{268,-42},{268,-46},
          {320,-46}},                                color={0,0,127}));
  connect(outAirSetPoiP1.uWin, outAirSetPoiCor.uWin) annotation (Line(points={{296,-42},
          {226,-42},{226,36},{292,36}},      color={255,0,255}));
  connect(outAirSetPoiP1.TZon, ZonStaP1.TZon) annotation (Line(points={{296,-46},
          {162,-46},{162,-16},{142,-16},{142,13},{-82,13},{-82,-24}}, color={0,0,
          127}));
  connect(outAirSetPoiP1.TDis, uTDisP1) annotation (Line(points={{296,-49},{-228,
          -49},{-228,-39}}, color={0,0,127}));
  connect(outAirSetPoiP1.uOpeMod, TZonSetP1.uOpeMod) annotation (Line(points={{296,-55},
          {76,-55},{76,-3},{102,-3}},      color={255,127,0}));
  connect(oveDamP2.u, outAirSetPoiP2.VOutMinSet_flow) annotation (Line(points={{333.2,
            -134},{258,-134},{258,-130},{262,-130}},     color={0,0,127}));
  connect(outAirSetPoiP2.TDis, uTDisP2) annotation (Line(points={{238,-133},{
            -228,-133},{-228,-63}},
                             color={0,0,127}));
  connect(outAirSetPoiP2.uWin, outAirSetPoiCor.uWin) annotation (Line(points={{238,
            -126},{226,-126},{226,36},{292,36}},
                                               color={255,0,255}));
  connect(outAirSetPoiP2.uOpeMod, TZonSetP2.uOpeMod) annotation (Line(points={{238,
            -139},{210,-139},{210,-140},{76,-140},{76,-75},{102,-75}},
                                                                     color={255,
          127,0}));
  connect(oveDamP3.u, outAirSetPoiP3.VOutMinSet_flow) annotation (Line(points={{333.2,
          -210},{258,-210},{258,-198},{328,-198}},       color={0,0,127}));
  connect(outAirSetPoiP3.uWin, outAirSetPoiCor.uWin) annotation (Line(points={{304,
          -194},{226,-194},{226,36},{292,36}}, color={255,0,255}));
  connect(outAirSetPoiP3.TZon, ZonStaP3.TZon) annotation (Line(points={{304,-198},
          {150,-198},{150,-176},{-84,-176},{-84,-166},{-82,-166}}, color={0,0,127}));
  connect(outAirSetPoiP3.TDis, uTDisP3) annotation (Line(points={{304,-201},{224,
          -201},{224,-204},{-228,-204},{-228,-87}}, color={0,0,127}));
  connect(outAirSetPoiP3.uOpeMod, TZonSetP3.uOpeMod) annotation (Line(points={{304,
          -207},{228,-207},{228,-212},{76,-212},{76,-145},{102,-145}}, color={255,
          127,0}));
  connect(oveDamP4.u, outAirSetPoiP4.VOutMinSet_flow)
    annotation (Line(points={{337.2,-298},{326,-298}}, color={0,0,127}));
  connect(outAirSetPoiP4.uWin, outAirSetPoiCor.uWin) annotation (Line(points={{302,
          -294},{302,-198},{226,-198},{226,36},{292,36}}, color={255,0,255}));
  connect(outAirSetPoiP4.TDis, uTDisP4) annotation (Line(points={{302,-301},{222,
          -301},{222,-306},{-228,-306},{-228,-111}}, color={0,0,127}));
  connect(outAirSetPoiP4.uOpeMod, TZonSetP4.uOpeMod) annotation (Line(points={{302,
          -307},{216,-307},{216,-312},{74,-312},{74,-228},{76,-228},{76,-215},{102,
          -215}}, color={255,127,0}));
  connect(or1.y, or2.u2)
    annotation (Line(points={{229,81},{251,81}}, color={255,0,255}));
  connect(or2.u1, opeModSelCore.uOcc) annotation (Line(points={{251,85},{251,150},
          {-12,150},{-12,68},{24,68}}, color={255,0,255}));
  connect(yFanCor, or2.y) annotation (Line(points={{396,272},{268,272},{268,85},
          {263,85}}, color={255,0,255}));
  connect(outAirSetPoiCor.uSupFan, or2.y) annotation (Line(points={{292,26},{248,
          26},{248,84},{268,84},{268,85},{263,85}}, color={255,0,255}));
  connect(yFanPer2, or4.y) annotation (Line(points={{402,20},{282,20},{282,15},{
          273,15}}, color={255,0,255}));
  connect(or4.u1, opeModSelCore.uOcc) annotation (Line(points={{261,15},{261,112},
          {251,112},{251,150},{-12,150},{-12,68},{24,68}}, color={255,0,255}));
  connect(or4.u2, or8.y) annotation (Line(points={{261,11},{256,11},{256,-71},{227,
          -71}}, color={255,0,255}));
  connect(outAirSetPoiP2.uSupFan, or4.y) annotation (Line(points={{238,-136},{
            238,-102},{274,-102},{274,15},{273,15}},      color={255,0,255}));
  connect(yFanPer1, or5.y) annotation (Line(points={{400,134},{278,134},{278,131},
          {269,131}}, color={255,0,255}));
  connect(or5.u2, or3.y)
    annotation (Line(points={{257,127},{257,13},{229,13}}, color={255,0,255}));
  connect(or5.u1, opeModSelCore.uOcc) annotation (Line(points={{257,131},{252,130},
          {251,130},{251,150},{-12,150},{-12,68},{24,68}}, color={255,0,255}));
  connect(outAirSetPoiP1.uSupFan, or5.y) annotation (Line(points={{296,-52},{236,
          -52},{236,-24},{272,-24},{272,131},{269,131}}, color={255,0,255}));
  connect(yFanPer3, or6.y) annotation (Line(points={{398,-144},{276,-144},{276,-149},
          {267,-149}}, color={255,0,255}));
  connect(or6.u1, or10.y) annotation (Line(points={{255,-149},{238.5,-149},{238.5,
          -151},{227,-151}}, color={255,0,255}));
  connect(or6.u2, opeModSelCore.uOcc) annotation (Line(points={{255,-153},{252,-153},
          {252,126},{251,126},{251,150},{-12,150},{-12,68},{24,68}}, color={255,
          0,255}));
  connect(outAirSetPoiP3.uSupFan, or6.y) annotation (Line(points={{304,-204},{228,
          -204},{228,-182},{268,-182},{268,-149},{267,-149}}, color={255,0,255}));
  connect(or13.y, or7.u2)
    annotation (Line(points={{229,-239},{243,-239}}, color={255,0,255}));
  connect(or7.y, yFanPer4) annotation (Line(points={{255,-235},{269.5,-235},{269.5,
          -258},{402,-258}}, color={255,0,255}));
  connect(outAirSetPoiP4.uSupFan, yFanPer4) annotation (Line(points={{302,-304},
          {252,-304},{252,-258},{402,-258}}, color={255,0,255}));
  connect(or7.u1, opeModSelCore.uOcc) annotation (Line(points={{243,-235},{252,-235},
          {252,128},{251,128},{251,150},{-12,150},{-12,68},{24,68}}, color={255,
          0,255}));
  connect(oveHeaStpPer4.y, conPID4.u_s) annotation (Line(points={{142.5,-251},{149.25,
          -251},{149.25,-254},{154.8,-254}}, color={0,0,127}));
  connect(oveHeaStpPer3.y, conPID3.u_s) annotation (Line(points={{140.5,-163},{147.25,
          -163},{147.25,-166},{152.8,-166}}, color={0,0,127}));
  connect(oveHeaStpPer2.y, conPID2.u_s) annotation (Line(points={{144.5,-95},{
            147.25,-95},{147.25,-88},{152.8,-88}},
                                          color={0,0,127}));
  connect(oveHeaStpPer1.y, conPID1.u_s) annotation (Line(points={{150.5,-3},{153.25,
          -3},{153.25,-2},{154.8,-2}}, color={0,0,127}));
  connect(oveHeaStpCor.y, conPID.u_s) annotation (Line(points={{140.5,47},{
            140.5,56.5},{154.8,56.5},{154.8,66}},
                                          color={0,0,127}));
  connect(booToInt.u, opeModSelP2.uSetUp) annotation (Line(points={{-30.8,-108},
          {-36,-108},{-36,-100},{-40,-100},{-40,-99},{-18,-99},{-18,-100},{24,-100}},
        color={255,0,255}));
  connect(booToInt.y, opeModSelP2.totHotZon) annotation (Line(points={{-21.2,-108},
          {0,-108},{0,-98},{24,-98}}, color={255,127,0}));
  connect(booToInt1.y, opeModSelP2.totColZon) annotation (Line(points={{-21.2,-118},
          {16,-118},{16,-88},{24,-88}}, color={255,127,0}));
  connect(booToInt2.u, opeModSelP3.uSetUp) annotation (Line(points={{-32.8,-182},
          {-44,-182},{-44,-169},{-18,-169},{-18,-170},{24,-170}}, color={255,0,255}));
  connect(booToInt2.y, opeModSelP3.totHotZon) annotation (Line(points={{-23.2,-182},
          {16,-182},{16,-168},{24,-168}}, color={255,127,0}));
  connect(booToInt3.u, opeModSelP3.uSetBac) annotation (Line(points={{-32.8,-192},
          {-50,-192},{-50,-162},{-18,-162},{-18,-160},{24,-160}}, color={255,0,255}));
  connect(booToInt3.y, opeModSelP3.totColZon) annotation (Line(points={{-23.2,-192},
          {16,-192},{16,-158},{24,-158}}, color={255,127,0}));
  connect(booToInt1.u, opeModSelP2.uSetBac) annotation (Line(points={{-30.8,-118},
          {-44,-118},{-44,-92},{-18,-92},{-18,-90},{24,-90}}, color={255,0,255}));
  connect(booToInt4.u, opeModSelP4.uSetUp) annotation (Line(points={{-30.8,-250},
          {-48,-250},{-48,-239},{-18,-239},{-18,-240},{24,-240}}, color={255,0,255}));
  connect(booToInt4.y, opeModSelP4.totHotZon) annotation (Line(points={{-21.2,-250},
          {18,-250},{18,-238},{24,-238}}, color={255,127,0}));
  connect(booToInt5.u, opeModSelP4.uSetBac) annotation (Line(points={{-30.8,-260},
          {-50,-260},{-50,-232},{-18,-232},{-18,-230},{24,-230}}, color={255,0,255}));
  connect(booToInt5.y, opeModSelP4.totColZon) annotation (Line(points={{-21.2,-260},
          {10,-260},{10,-228},{24,-228}}, color={255,127,0}));
  connect(booToInt6.u, opeModSelP1.uSetUp) annotation (Line(points={{-26.8,-40},
          {-40,-40},{-40,-27},{-18,-27},{-18,-28},{24,-28}}, color={255,0,255}));
  connect(booToInt6.y, opeModSelP1.totHotZon) annotation (Line(points={{-17.2,-40},
          {16,-40},{16,-26},{24,-26}}, color={255,127,0}));
  connect(booToInt7.u, opeModSelP1.uSetBac) annotation (Line(points={{-26.8,-50},
          {-50,-50},{-50,-20},{-18,-20},{-18,-18},{24,-18}}, color={255,0,255}));
  connect(booToInt7.y, opeModSelP1.totColZon) annotation (Line(points={{-17.2,-50},
          {18,-50},{18,-16},{24,-16}}, color={255,127,0}));
  connect(booToInt8.u, opeModSelCore.uSetUp) annotation (Line(points={{-28.8,36},
          {-44,36},{-44,43},{-18,43},{-18,42},{24,42}}, color={255,0,255}));
  connect(booToInt8.y, opeModSelCore.totHotZon) annotation (Line(points={{-19.2,
          36},{16,36},{16,44},{24,44}}, color={255,127,0}));
  connect(booToInt9.u, opeModSelCore.uSetBac) annotation (Line(points={{-28.8,24},
          {-48,24},{-48,50},{-18,50},{-18,52},{24,52}}, color={255,0,255}));
  connect(booToInt9.y, opeModSelCore.totColZon) annotation (Line(points={{-19.2,
          24},{18,24},{18,54},{24,54}}, color={255,127,0}));
  connect(reaToInt.u, oveDemandLimitLevel.y) annotation (Line(points={{80,110},{
          74,110},{74,111},{68.5,111}}, color={0,0,127}));
  connect(oveDemandLimitLevel.u, zero5.y)
    annotation (Line(points={{57,111},{46.9,111}}, color={0,0,127}));
  connect(reaToInt.y, TZonSetCore.uCooDemLimLev) annotation (Line(points={{104,110},
          {106,110},{106,86},{96,86},{96,48},{102,48}}, color={255,127,0}));
    connect(conPID.trigger, opeModSelCore.uOcc) annotation (Line(points={{158.4,
            58.8},{158.4,150},{-12,150},{-12,68},{24,68}}, color={255,0,255}));
    connect(conPID1.trigger, opeModSelCore.uOcc) annotation (Line(points={{
            158.4,-9.2},{158.4,-12},{158,-12},{158,148},{158.4,148},{158.4,150},
            {-12,150},{-12,68},{24,68}}, color={255,0,255}));
    connect(conPID2.trigger, opeModSelCore.uOcc) annotation (Line(points={{
            156.4,-95.2},{156.4,-12},{158,-12},{158,148},{158.4,148},{158.4,150},
            {-12,150},{-12,68},{24,68}}, color={255,0,255}));
    connect(oveCooStpCor.y, onOffCon.reference) annotation (Line(points={{140.5,
            63},{144,63},{144,96},{145,96}}, color={0,0,127}));
    connect(onOffCon.u, corZonSta.TZon) annotation (Line(points={{145,90},{146,
            90},{146,34},{-84,34},{-84,46}}, color={0,0,127}));
    connect(onOffCon.y, not1.u) annotation (Line(points={{157,93},{158,93},{158,
            94},{157.2,94}}, color={255,0,255}));
    connect(booToRea.u, not1.y) annotation (Line(points={{165,81},{166,81},{166,
            94},{166.8,94}}, color={255,0,255}));
    connect(not2.y, booToRea1.u) annotation (Line(points={{162.8,14},{164,14},{
            164,13},{165,13}}, color={255,0,255}));
    connect(not2.u, onOffCon1.y) annotation (Line(points={{153.2,14},{155,14},{
            155,13}}, color={255,0,255}));
    connect(onOffCon1.reference, oveCooStpPer1.y) annotation (Line(points={{143,
            16},{142,16},{142,9},{140.5,9}}, color={0,0,127}));
    connect(onOffCon1.u, ZonStaP1.TZon) annotation (Line(points={{143,10},{152,
            10},{152,-22},{162,-22},{162,-16},{142,-16},{142,13},{-82,13},{-82,
            -24}}, color={0,0,127}));
    connect(onOffCon2.y, not3.u) annotation (Line(points={{145,-63},{148,-63},{
            148,-64},{149.2,-64}}, color={255,0,255}));
    connect(booToRea2.u, not3.y) annotation (Line(points={{157,-71},{158,-71},{
            158,-64},{158.8,-64}}, color={255,0,255}));
    connect(onOffCon2.reference, oveCooStpPer2.y) annotation (Line(points={{133,
            -60},{136,-60},{136,-79},{140.5,-79}}, color={0,0,127}));
    connect(onOffCon2.u, conPID2.u_m) annotation (Line(points={{133,-66},{146,
            -66},{146,-102},{160,-102},{160,-95.2}}, color={0,0,127}));
    connect(outAirSetPoiP2.TZon, ZonStaP2.TZon) annotation (Line(points={{238,
            -130},{212,-130},{212,-128},{-176,-128},{-176,-96},{-82,-96}},
          color={0,0,127}));
    connect(conPID2.u_m, ZonStaP2.TZon) annotation (Line(points={{160,-95.2},{
            160,-128},{-176,-128},{-176,-96},{-82,-96}}, color={0,0,127}));
    connect(onOffCon3.reference, oveCooStpPer3.y) annotation (Line(points={{135,
            -132},{136.5,-132},{136.5,-151}}, color={0,0,127}));
    connect(onOffCon3.u, ZonStaP3.TZon) annotation (Line(points={{135,-138},{
            142,-138},{142,-176},{-84,-176},{-84,-166},{-82,-166}}, color={0,0,
            127}));
    connect(onOffCon3.y, not4.u) annotation (Line(points={{147,-135},{147.5,
            -135},{147.5,-134},{147.2,-134}}, color={255,0,255}));
    connect(not4.y, booToRea3.u) annotation (Line(points={{156.8,-134},{157,
            -134},{157,-151}}, color={255,0,255}));
    connect(onOffCon4.reference, oveCooStpPer4.y) annotation (Line(points={{155,
            -222},{148,-222},{148,-221},{142.5,-221}}, color={0,0,127}));
    connect(onOffCon4.y, not5.u) annotation (Line(points={{167,-225},{170,-225},
            {170,-222},{171.2,-222}}, color={255,0,255}));
    connect(not5.y, booToRea4.u) annotation (Line(points={{180.8,-222},{172,
            -222},{172,-239},{161,-239}}, color={255,0,255}));
    connect(onOffCon4.u, ZonStaP4.TZon) annotation (Line(points={{155,-228},{
            -84,-228},{-84,-236},{-82,-236}}, color={0,0,127}));
    connect(conPID4.u_m, ZonStaP4.TZon) annotation (Line(points={{162,-261.2},{
            158,-261.2},{158,-264},{148,-264},{148,-228},{-84,-228},{-84,-236},
            {-82,-236}}, color={0,0,127}));
    connect(outAirSetPoiP4.TZon, ZonStaP4.TZon) annotation (Line(points={{302,
            -298},{148,-298},{148,-228},{-84,-228},{-84,-236},{-82,-236}},
          color={0,0,127}));
    connect(conPID3.trigger, opeModSelCore.uOcc) annotation (Line(points={{
            156.4,-173.2},{156.4,-182},{156,-182},{156,-76},{156.4,-76},{156.4,
            -12},{158,-12},{158,148},{158.4,148},{158.4,150},{-12,150},{-12,68},
            {24,68}}, color={255,0,255}));
    connect(conPID4.trigger, opeModSelCore.uOcc) annotation (Line(points={{
            158.4,-261.2},{158.4,-182},{156,-182},{156,-76},{156.4,-76},{156.4,
            -12},{158,-12},{158,148},{158.4,148},{158.4,150},{-12,150},{-12,68},
            {24,68}}, color={255,0,255}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false, extent={{-160,-160},{100,180}})),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-160,-160},{100,
            180}})),
    uses(Buildings(version="8.0.0"), Modelica(version="3.2.3")));
end controller;

  //Spawn//

  inner Buildings.ThermalZones.EnergyPlus.Building building(
    idfName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefsmalloffice-variant1/RefBldgSmallOfficeNew2004_v2.idf"),
    weaName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefsmalloffice-variant1/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos"),
    epwName=Modelica.Utilities.Files.loadResource(
        "/SpawnResources/spawnrefsmalloffice-variant1/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"),
    computeWetBulbTemperature=false)
    annotation (Placement(transformation(extent={{-322,72},{-302,92}})));

  Buildings.ThermalZones.EnergyPlus.ThermalZone corZon(
    zoneName="Core_ZN",                                redeclare final package
      Medium =                                                                          Medium,
      nPorts=2) "\"Core zone\""
    annotation (Placement(transformation(extent={{60,64},{100,104}})));

    // Fluids - non HVAC //
  Buildings.Fluid.Sources.Outside Outside(redeclare final package Medium = Medium,
      nPorts=10)
    "Outside environment boundary condition that uses the weather data from Spawn"
    annotation (Placement(transformation(extent={{-254,-190},{-234,-170}})));

    // Fluids - HVAC //
    model BaselineSystem3
    "PSZ-AC Constant Air Volume, Packaged Single Zone Rooftop Unit"

      //Parameters - Fluids//
      parameter Modelica.SIunits.MassFlowRate mass_flow_nominal = 0.5 "Nominal Mass Flow Rate (kg/s)";
      parameter Modelica.SIunits.Pressure dp_nominal = 0 "Nominal Pressure Drop (Pa)";
      parameter Modelica.SIunits.Power heaNomPow = 100 "Gas Heater Nominal Power (W)";
      parameter Modelica.SIunits.Power CCNomPow = 100 "Cooling coil Nominal Power (W)";
      parameter String zonenb = "1" "zone number";
      parameter Modelica.SIunits.VolumeFlowRate fanVFR = 0.44 "Fan volumetric flow rate";
      parameter Boolean fromDp = false;

      //HVAC Components//

      Buildings.Fluid.HeatExchangers.DXCoils.AirCooled.SingleSpeed sinSpeDX(
        redeclare final package Medium = Medium,
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
                TConInMin=173.15,
                TConInMax=373.15,
                TEvaInMin=173.15,
                TEvaInMax=373.15,
                ffMin=0.0,
                ffMax=1.5))}),
        allowFlowReversal=true,
        m_flow_small=1E-3,
        show_T=false,
        from_dp=fromDp,
        dp_nominal=dp_nominal,
        energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
      T_start=Medium.T_default,
      computeReevaporation=true,
        dxCoo(wetCoi(TADP(min=233.15), appDewPt(TADP(min=233.15, nominal=273.15 + 2)))))
                        "Single Speed DX cooling coil"
        annotation (Placement(transformation(extent={{-48,-208},{10,-150}})));

      Buildings.Fluid.HeatExchangers.HeaterCooler_u hea(
        redeclare final package Medium = Medium,
        allowFlowReversal=true,
        m_flow_nominal=mass_flow_nominal,
        from_dp=fromDp,
        dp_nominal=dp_nominal,
        energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
        T_start=Medium.T_default,
        Q_flow_nominal=heaNomPow)
        annotation (Placement(transformation(extent={{62,-200},{100,-158}})));

      // TO DO: replace fan characteristics values by variable parameters//

      Buildings.Fluid.Movers.FlowControlled_m_flow fan(
        redeclare final package Medium = Medium,
        energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
        T_start=Medium.T_default,
        allowFlowReversal=true,
        m_flow_nominal=mass_flow_nominal,
        per(
          pressure(V_flow={0,0.88}, dp={2*622,0}),
          use_powerCharacteristic=false,
          hydraulicEfficiency(V_flow={0.44}, eta={0.65}),
          motorEfficiency(V_flow={0.44}, eta={0.825})),
      use_inputFilter=false,
      riseTime=120,
        dp_nominal=dp_nominal)
        annotation (Placement(transformation(extent={{228,-198},{270,-156}})));

      // Ports //

      Modelica.Fluid.Interfaces.FluidPort_a OAInlPor(redeclare final package Medium =
          Medium) "Port to the outside air source" annotation (Placement(
          transformation(extent={{-410,-210},{-390,-190}}),
                                                        iconTransformation(
            extent={{-516,268},{-496,288}})));

      Modelica.Fluid.Interfaces.FluidPort_b OAOutPor(redeclare final package Medium =
          Medium) "Port to the outside air sink" annotation (Placement(
          transformation(extent={{-410,-248},{-390,-228}}),
                                                         iconTransformation(
            extent={{-516,-38},{-496,-18}})));

      Modelica.Fluid.Interfaces.FluidPort_b zonSupPort(redeclare final package
          Medium =
          Medium) "Outlet to the zone air supply" annotation (Placement(
          transformation(extent={{436,-188},{456,-168}}),
                                                      iconTransformation(extent={{514,-36},
              {534,-16}})));

      Modelica.Fluid.Interfaces.FluidPort_a zonRetPor(redeclare final package
          Medium =
          Medium) "Inlet for the zone return air" annotation (Placement(
          transformation(extent={{442,-248},{462,-228}}),
                                                       iconTransformation(
            extent={{510,268},{530,288}})));

     //Controls//

      Buildings.Fluid.Sensors.VolumeFlowRate volSenSup(
        redeclare final package Medium = Medium,
        m_flow_nominal=0.5,
      T_start=288.65)   "Volumetric flow rate sensor, supply side"
        annotation (Placement(transformation(extent={{346,-188},{366,-168}})));

      Buildings.Fluid.Sensors.VolumeFlowRate volSenOA(
        redeclare final package Medium = Medium,
        m_flow_nominal=0.5,
        T_start=288.65) "Volumetric flow rate sensor, outside air"
        annotation (Placement(transformation(extent={{-324,-210},{-304,-190}})));

      //Output //

      Modelica.Blocks.Interfaces.RealOutput yFanPow "Fan power demand" annotation (
          Placement(transformation(extent={{446,54},{490,98}}), iconTransformation(
            extent={{-22,-22},{22,22}},
            rotation=90,
            origin={340,320})));

      Modelica.Blocks.Interfaces.RealOutput yHeaPow "Heating coil power demand"
        annotation (Placement(transformation(extent={{446,120},{490,164}}),
            iconTransformation(
            extent={{-22,-22},{22,22}},
            rotation=90,
            origin={-38,322})));

      Modelica.Blocks.Interfaces.RealOutput yCooPow "Cooling coil power demand"
        annotation (Placement(transformation(extent={{446,182},{490,226}}),
            iconTransformation(
            extent={{-22,-22},{22,22}},
            rotation=90,
            origin={140,322})));

      // Signal Exchange blocks - BOPTEST //

      Modelica.Blocks.Interfaces.RealInput senTemOA
        "Outside air temperature sensor for cooling coil model"
                                                    annotation (Placement(
            transformation(extent={{-20,-20},{20,20}},
            rotation=270,
            origin={-134,256}),                             iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={-348,320})));

      Buildings.Fluid.Sensors.RelativeHumidityTwoPort senRelHum(redeclare
        final package
                  Medium =                                                                     Medium,
        allowFlowReversal=true,
          m_flow_nominal=0.5,
        m_flow_small=0.0001)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}},
            rotation=180,
            origin={248,-238})));
      Modelica.Blocks.Interfaces.RealInput uDamper "OA damper VFR setpoint"
        annotation (Placement(transformation(extent={{-472,22},{-432,62}}),
            iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={-460,386})));
      Modelica.Blocks.Interfaces.RealInput uHeatingCoil annotation (Placement(
            transformation(extent={{-472,98},{-432,138}}), iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={-118,320})));
      Modelica.Blocks.Interfaces.BooleanInput uCoolingCoil
        "Cooling coil on/off signal" annotation (Placement(transformation(extent={{58,
                308},{98,348}}), iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={62,320})));
      Modelica.Blocks.Interfaces.RealOutput yReturnRH
      "Return air relative humidity"   annotation (Placement(transformation(
            extent={{-22,-22},{22,22}},
            rotation=270,
            origin={248,-292}), iconTransformation(
            extent={{-22,-22},{22,22}},
            rotation=90,
            origin={-278,320})));
      Modelica.Blocks.Interfaces.BooleanInput uFan "Fan on/off signal" annotation (
          Placement(transformation(extent={{262,308},{302,348}}),
            iconTransformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={266,318})));
      Modelica.Blocks.Sources.RealExpression fanOn(y=fanVFR)
        annotation (Placement(transformation(extent={{-290,210},{-270,230}})));
      Modelica.Blocks.Sources.RealExpression fanOff(y=0.01)
        annotation (Placement(transformation(extent={{-290,148},{-270,168}})));
      Modelica.Blocks.Logical.Switch fanControl
        annotation (Placement(transformation(extent={{-222,176},{-202,196}})));
    Buildings.Fluid.Sensors.TemperatureTwoPort senTemDis(redeclare package Medium =
                 Medium, m_flow_nominal=mass_flow_nominal)
      annotation (Placement(transformation(extent={{396,-188},{416,-168}})));
      Modelica.Blocks.Interfaces.RealOutput yDischargeTem
      "Discharge air temperature" annotation (Placement(transformation(
          extent={{-22,-22},{22,22}},
          rotation=270,
          origin={382,-296}), iconTransformation(
          extent={{-22,-22},{22,22}},
          rotation=90,
          origin={-202,322})));
    Buildings.Fluid.Actuators.Dampers.MixingBox eco(
        riseTime=120,
      redeclare package Medium = Medium,
        mOut_flow_nominal=mass_flow_nominal,
        dpDamOut_nominal=0.1,
        dpFixOut_nominal=1,
        mRec_flow_nominal=mass_flow_nominal,
        dpDamRec_nominal=0.1,
        dpFixRec_nominal=1,
        mExh_flow_nominal=mass_flow_nominal,
        dpDamExh_nominal=0.1,
        dpFixExh_nominal=1,
        from_dp=fromDp)
      annotation (Placement(transformation(extent={{-254,-244},{-194,-188}})));
      Buildings.Controls.OBC.CDL.Continuous.Greater gre7(h=0)
        annotation (Placement(transformation(extent={{-372,22},{-362,32}})));
      Modelica.Blocks.Sources.RealExpression zero3(y=0) "cooldown and warmup time"
        annotation (Placement(transformation(extent={{-400,-2},{-382,16}})));
      Buildings.Controls.OBC.CDL.Continuous.PIDWithReset conPID1(
      controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.PI,
        k=10,
        Ti=15) annotation (Placement(transformation(extent={{-348,32},{-328,52}})));
      Buildings.Controls.OBC.CDL.Logical.Not not1
        annotation (Placement(transformation(extent={{-374,-40},{-354,-20}})));
    Buildings.Fluid.FixedResistances.PressureDrop res(
      redeclare package Medium = Medium,
      m_flow_nominal=mass_flow_nominal,
      dp_nominal=200 + 200 + 100)
      annotation (Placement(transformation(extent={{-130,-188},{-110,-168}})));
    Buildings.Controls.OBC.CDL.Continuous.Greater gre
      annotation (Placement(transformation(extent={{-260,102},{-240,122}})));
      Modelica.Blocks.Logical.Switch fanControl1
        annotation (Placement(transformation(extent={{-190,102},{-170,122}})));
      Modelica.Blocks.Sources.RealExpression fanOff1(y=0)
        annotation (Placement(transformation(extent={{-230,78},{-210,98}})));
      Modelica.Blocks.Sources.RealExpression fanOff2(y=fanVFR*0.2)
        annotation (Placement(transformation(extent={{-306,94},{-286,114}})));
    Buildings.Controls.OBC.CDL.Continuous.PID conPID(controllerType=Buildings.Controls.OBC.CDL.Types.SimpleController.P,
        k=20)
      annotation (Placement(transformation(extent={{-80,176},{-60,196}})));
    Buildings.Controls.OBC.CDL.Logical.TrueFalseHold truFalHol(trueHoldDuration=
         300, falseHoldDuration=0)
      annotation (Placement(transformation(extent={{-282,176},{-262,196}})));
    equation

      connect(sinSpeDX.port_b, hea.port_a)
        annotation (Line(points={{10,-179},{62,-179}},         color={0,127,255}));
      connect(fan.P, yFanPow) annotation (Line(points={{272.1,-158.1},{272.1,76},{468,
              76}}, color={0,0,127}));
      connect(hea.Q_flow, yHeaPow) annotation (Line(points={{101.9,-166.4},{136,
            -166.4},{136,142},{468,142}},
                                    color={0,0,127}));
      connect(yCooPow, sinSpeDX.P) annotation (Line(points={{468,204},{22,204},{22,-152.9},
              {12.9,-152.9}},  color={0,0,127}));
      connect(OAInlPor, volSenOA.port_a)
        annotation (Line(points={{-400,-200},{-324,-200}}, color={0,127,255}));
      connect(senRelHum.port_a, zonRetPor) annotation (Line(points={{258,-238},{452,
              -238}},                            color={0,127,255}));
      connect(uCoolingCoil, sinSpeDX.on) annotation (Line(points={{78,328},{-50.9,328},
              {-50.9,-155.8}},  color={255,0,255}));
      connect(fanControl.u1, fanOn.y) annotation (Line(points={{-224,194},{-236,
            194},{-236,220},{-269,220}},
                                      color={0,0,127}));
      connect(fanControl.u3, fanOff.y) annotation (Line(points={{-224,178},{
            -234,178},{-234,158},{-269,158}},
                                      color={0,0,127}));
      connect(senRelHum.phi, yReturnRH) annotation (Line(points={{247.9,-249},{247.9,
              -258.5},{248,-258.5},{248,-292}}, color={0,0,127}));
    connect(volSenSup.port_b, senTemDis.port_a)
      annotation (Line(points={{366,-178},{396,-178}}, color={0,127,255}));
    connect(senTemDis.port_b, zonSupPort)
      annotation (Line(points={{416,-178},{446,-178}}, color={0,127,255}));
    connect(yDischargeTem, senTemDis.T) annotation (Line(points={{382,-296},{
            384,-296},{384,-150},{406,-150},{406,-167}}, color={0,0,127}));
    connect(sinSpeDX.TConIn, senTemOA) annotation (Line(points={{-50.9,-170.3},{-50.9,
              256},{-134,256}},       color={0,0,127}));
    connect(eco.port_Out, volSenOA.port_b) annotation (Line(points={{-254,
            -199.2},{-277,-199.2},{-277,-200},{-304,-200}}, color={0,127,255}));
    connect(eco.port_Exh, OAOutPor) annotation (Line(points={{-254,-232.8},{
            -326,-232.8},{-326,-238},{-400,-238}}, color={0,127,255}));
    connect(eco.port_Ret, senRelHum.port_b) annotation (Line(points={{-194,
            -232.8},{22,-232.8},{22,-238},{238,-238}}, color={0,127,255}));
      connect(fan.port_b, volSenSup.port_a) annotation (Line(points={{270,-177},{282,
              -177},{282,-178},{346,-178}}, color={0,127,255}));
      connect(zero3.y,gre7. u2) annotation (Line(points={{-381.1,7},{-376,7},{-376,23},
              {-373,23}},        color={0,0,127}));
      connect(conPID1.u_s, uDamper)
        annotation (Line(points={{-350,42},{-452,42}}, color={0,0,127}));
      connect(gre7.u1, uDamper)
        annotation (Line(points={{-373,27},{-373,42},{-452,42}}, color={0,0,127}));
      connect(conPID1.u_m, volSenOA.V_flow) annotation (Line(points={{-338,30},{-338,
              -10},{-314,-10},{-314,-189}}, color={0,0,127}));
      connect(conPID1.y, eco.y) annotation (Line(points={{-326,42},{-304,42},{-304,40},
              {-224,40},{-224,-182.4}}, color={0,0,127}));
      connect(not1.u, gre7.y) annotation (Line(points={{-376,-30},{-370,-30},{
            -370,27},{-361,27}},
                          color={255,0,255}));
      connect(not1.y, conPID1.trigger) annotation (Line(points={{-352,-30},{
            -348,-30},{-348,30},{-344,30}},
                                    color={255,0,255}));
      connect(hea.port_b, fan.port_a) annotation (Line(points={{100,-179},{166,-179},
              {166,-177},{228,-177}}, color={0,127,255}));
    connect(eco.port_Sup, res.port_a) annotation (Line(points={{-194,-199.2},{
            -162,-199.2},{-162,-178},{-130,-178}}, color={0,127,255}));
    connect(sinSpeDX.port_a, res.port_b) annotation (Line(points={{-48,-179},{
            -80,-179},{-80,-178},{-110,-178}}, color={0,127,255}));
    connect(gre.y, fanControl1.u2)
      annotation (Line(points={{-238,112},{-192,112}}, color={255,0,255}));
    connect(fanControl1.u3, fanOff1.y) annotation (Line(points={{-192,104},{
            -200,104},{-200,88},{-209,88}}, color={0,0,127}));
    connect(uHeatingCoil, fanControl1.u1) annotation (Line(points={{-452,118},{
            -318,118},{-318,126},{-192,126},{-192,120}}, color={0,0,127}));
    connect(gre.u1, volSenSup.V_flow) annotation (Line(points={{-262,112},{-30,
            112},{-30,142},{110,142},{110,-167},{356,-167}}, color={0,0,127}));
    connect(gre.u2, fanOff2.y)
      annotation (Line(points={{-262,104},{-285,104}}, color={0,0,127}));
    connect(fanControl1.y, hea.u) annotation (Line(points={{-169,112},{58.2,112},
            {58.2,-166.4}}, color={0,0,127}));
    connect(fanControl.y, conPID.u_s)
      annotation (Line(points={{-201,186},{-82,186}}, color={0,0,127}));
    connect(conPID.u_m, volSenSup.V_flow) annotation (Line(points={{-70,174},{
            -70,70},{356,70},{356,-167}}, color={0,0,127}));
    connect(conPID.y, fan.m_flow_in) annotation (Line(points={{-58,186},{249,
            186},{249,-151.8}}, color={0,0,127}));
    connect(fanControl.u2, truFalHol.y)
      annotation (Line(points={{-224,186},{-260,186}}, color={255,0,255}));
    connect(truFalHol.u, uFan) annotation (Line(points={{-284,186},{-320,186},{
            -320,362},{282,362},{282,328}}, color={255,0,255}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-420,-260},
                {440,220}}),     graphics={Bitmap(
            extent={{-678,-344},{682,362}},
            imageSource=
                "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"
                 +
                "afCHzcmTp3ShOIK8htN+SCdn+90iqZEH1xe4h1mky/R6OOmSBCYdxzkIeSkUeebLsqSQtywgejxiX0CjJYW9KPbcg/IOybtf3zkg9S5xZ7GkRTtR7cJpBfsMYM8RX0RtW844ogdcZS3zkQH7s/V7IFo0rgXezdjZEuSGVY/kYmeYvvMc0rIvSg1ssyjWWiimEOa2tTAB+D3JzyuJKQTYnainVVLpRNGSJ5KssuqrTGELdAZuUlJGX5mLzmS2Lql9Bc3wPhqFVMYPE07rkKa8hTYxtc5U6A1MYVfTXxdKBlgPtBPdHNtIbh/akIrvQbKdifM80lIMtZ1ZbISMmGOrf6+C1BbBAjofGemeQWqQekVnXk7YQ+E4kgPJkrA8Urdsie5jJFIp9EfcdwGSDJ5AXkEdOccBPdDViTKVechYlAZj0C7hi0hPOxRJTwvQgvYiEk8fRAbTWlib8AL4GunjPEYQtm+8QnoV3rqEDZEvkT5mJQva0HvdGgVFbYCY5CBkpFyIVHDPosOIghTwfRXrENbvzyW7y3QWDEJrxAS0RoxEC/7y6Pv6EEkFM9Hzf4x0Ubd23jYC76Odfl4MI6wW+5TiqiMXowl7NWWld22UQmQz9B0PrZaOal//QRvLx0k+m6blWJHwqWILaexRfiVKlChRwoOecjzh0YRFy+k0ZodZokSJEiV6OPoTNtx8St88MrFEiRIlSqTA2YSNH9e2lpwSJUqUWHbR7CjB9ei2dK8JHETY57cLGa9mNpmuEiVKlCjRAlxJsovURa0jrUSJEiVKNBtJTGEG4ROMSpQoUaJEk9Go8xTSIAgqehqFat9YvVaiRIkSJVqE/wNpVyFPOo2P4AAAAABJRU5ErkJggg==",
            fileName="modelica://SpawnRefSmallOfficeBuilding/../../../../../Pres/HVAC.png")}),
                                                                     Diagram(
          coordinateSystem(preserveAspectRatio=false, extent={{-420,-260},{440,220}})),
        Documentation(revisions="<html>
<ul>
<li>November 19, 2020 by Thibault Marzullo:<br>First implementation.</li>
</ul>
</html>", info="<html>
<p>Packaged Single-Zone Rooftop Unit following the specifications of ASHRAE&apos;s HVAC System 3 (PZS-AC).</p>
</html>"));
    end BaselineSystem3;
  Buildings.Utilities.Time.CalendarTime calTim(
      zerTim=Buildings.Utilities.Time.Types.ZeroTime.Custom,
      yearRef=2017,
      outputUnixTimeStamp=false)
                    "Calendar Time"
    annotation (Placement(transformation(extent={{-310,138},{-278,170}})));
  BaselineSystem3 HVAC(
    zonenb="1",
    mass_flow_nominal=0.45*1.2,
    heaNomPow=17161.57,
    CCNomPow=-7488.54,
    fanVFR=0.45) "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-14},{-42,16}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal
    annotation (Placement(transformation(extent={{-248,154},{-228,174}})));
  Modelica.Blocks.Math.IntegerToReal integerToReal1
    annotation (Placement(transformation(extent={{-250,128},{-230,148}})));
  Modelica.Blocks.Routing.Multiplex3 mul "Multiplex for gains"
    annotation (Placement(transformation(extent={{-30,84},{-10,104}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k=0) "Convective heat gain"
    annotation (Placement(transformation(extent={{-82,84},{-62,104}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k=0) "Radiative heat gain"
    annotation (Placement(transformation(extent={{-82,124},{-62,144}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k=0) "Latent heat gain"
    annotation (Placement(transformation(extent={{-82,52},{-62,72}})));
  Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
        transformation(extent={{-284,62},{-244,102}}),iconTransformation(extent={{-8,-172},
            {12,-152}})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow(y(min=0.0, max=15000.0, unit="W"), description=
          "Core Heating Coil Power",
        KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"Core heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={286,2})));
  BaselineSystem3 HVAC1(
    zonenb="2",
    mass_flow_nominal=0.37*1.2,
    heaNomPow=13514.14,
    CCNomPow=-6049.16,
    fanVFR=0.37,
    fan(per(
        pressure(V_flow={0.3702,0.3703}, dp={622.1,622}),
        use_powerCharacteristic=false,
        hydraulicEfficiency(V_flow={0.3703}, eta={0.65}),
        motorEfficiency(V_flow={0.3703}, eta={0.825}))))
    "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-94},{-40,-64}})));
  BaselineSystem3 HVAC2(
    zonenb="3",
    mass_flow_nominal=0.36*1.2,
    heaNomPow=11154.76,
    CCNomPow=-5901.43,
    fanVFR=0.36,
    fan(per(
        pressure(V_flow={0.3603,0.3604}, dp={622.1,622}),
        use_powerCharacteristic=false,
        hydraulicEfficiency(V_flow={0.3604}, eta={0.65}),
        motorEfficiency(V_flow={0.3604}, eta={0.825}))))
    "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-184},{-40,-154}})));
  BaselineSystem3 HVAC3(
    zonenb="4",
    mass_flow_nominal=0.36*1.2,
    heaNomPow=13285.35,
    CCNomPow=-5880.51,
    fanVFR=0.36,
    fan(per(
        pressure(V_flow={0.3823,0.3824}, dp={622.1,622}),
        use_powerCharacteristic=false,
        hydraulicEfficiency(V_flow={0.3824}, eta={0.65}),
        motorEfficiency(V_flow={0.3824}, eta={0.825}))))
    "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-98,-272},{-42,-242}})));
  BaselineSystem3 HVAC4(
    zonenb="5",
    mass_flow_nominal=0.33*1.2,
    heaNomPow=10594.79,
    CCNomPow=-5526.56,
    fanVFR=0.33,
    fan(per(
        pressure(V_flow={0.3522,0.3523}, dp={622.1,622}),
        use_powerCharacteristic=false,
        hydraulicEfficiency(V_flow={0.3523}, eta={0.65}),
        motorEfficiency(V_flow={0.3523}, eta={0.825}))))
    "Core zone HVAC system"
    annotation (Placement(transformation(extent={{-96,-350},{-40,-320}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon1(
      zoneName="Perimeter_ZN_1",
      redeclare final package Medium = Medium,
      nPorts=2) "Perimeter zone 1"
      annotation (Placement(transformation(extent={{62,-94},{102,-54}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon2(
      zoneName="Perimeter_ZN_2",
      redeclare final package Medium = Medium,
      nPorts=2) "Perimeter zone 2"
      annotation (Placement(transformation(extent={{56,-184},{96,-144}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon3(
      zoneName="Perimeter_ZN_3",
      redeclare final package Medium = Medium,
      nPorts=2) "Perimeter zone 3"
      annotation (Placement(transformation(extent={{54,-274},{94,-234}})));
  Buildings.ThermalZones.EnergyPlus.ThermalZone perZon4(
      zoneName="Perimeter_ZN_4",
      redeclare final package Medium = Medium,
      nPorts=2) "Perimeter zone 4"
      annotation (Placement(transformation(extent={{52,-352},{92,-312}})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow1(y(min=0.0, max=15000.0, unit="W"), description=
          "P1 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P1 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={286,-90})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow2(y(min=0.0, max=15000.0, unit="W"), description=
          "P2 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P2 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={288,-190})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow3(y(min=0.0, max=15000.0, unit="W"), description=
          "P3 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P3 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={288,-284})));
Buildings.Utilities.IO.SignalExchange.Read senHeaPow4(y(min=0.0, max=15000.0, unit="W"), description=
          "P4 Heating Coil Power", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.GasPower)
      "\"P4 heating coil power demand\""
  annotation (Placement(transformation(
      extent={{-10,-10},{10,10}},
      rotation=0,
      origin={290,-386})));
Buildings.Utilities.IO.SignalExchange.Read senDay(y(min=0.0, max=7, unit="1"), description=
          "Day of the week - 1 to 7", KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Day of the week - 1 to 7\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={374,138})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow4(y(min=0.0, max=2000.0, unit="W"), description="P4 Fan Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P4 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={290,-416})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow4(y(min=-9000, max=0, unit="W"), description="P4 Cooling Coil Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P4 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={290,-356})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow3(y(min=0.0, max=2000.0, unit="W"), description="P3 Fan Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P3 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={288,-314})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow3(y(min=-9000, max=0, unit="W"), description="P3 Cooling Coil Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P3 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={288,-254})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow2(y(min=0.0, max=2000.0, unit="W"), description="P2 Fan Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P2 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={288,-222})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow2(y(min=-9000, max=0, unit="W"), description="P2 Cooling Coil Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P2 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={288,-162})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow1(y(min=0.0, max=2000.0, unit="W"), description="P1 Fan Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P1 fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={286,-120})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow1(y(min=-9000, max=0, unit="W"), description="P1 Cooling Coil Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"P1 cooling coil power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={286,-62})));
Buildings.Utilities.IO.SignalExchange.Read senFanPow(y(min=0.0, max=2000.0, unit="W"), description="Core Fan Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Core zone fan power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={286,-24})));
Buildings.Utilities.IO.SignalExchange.Read senCCPow(y(min=-9000, max=0, unit="W"), description="Core Cooling Coil Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.ElectricPower)
      "\"Core zone cooling coil power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={286,28})));
Buildings.Utilities.IO.SignalExchange.Read senTemOA(y(min=240.0, max=320.0, unit="K"), description="OA Temperature",
      KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
    "Outside air temperature from weather file" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={372,76})));
    Modelica.Blocks.Math.MultiSum multiSum5(nu=3)
      annotation (Placement(transformation(extent={{328,-4},{340,8}})));
Buildings.Utilities.IO.SignalExchange.Read senPowCor(
      y(min=0.0,
        max=25000.0,
        unit="W"),
      description="Core AHU Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Core zone AHU power demand\"" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={370,2})));
    Modelica.Blocks.Math.MultiSum multiSum4(nu=3)
      annotation (Placement(transformation(extent={{326,-94},{338,-82}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer1(
      y(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 1 AHU Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Perimeter zone 1 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={370,-88})));
    Modelica.Blocks.Math.MultiSum multiSum3(nu=3)
      annotation (Placement(transformation(extent={{326,-198},{338,-186}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer2(
      y(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 2 AHU Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Perimeter zone 2 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={370,-192})));
    Modelica.Blocks.Math.MultiSum multiSum2(nu=3)
      annotation (Placement(transformation(extent={{328,-292},{340,-280}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer3(
      y(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 3 AHU Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Perimeter zone 3 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={370,-286})));
    Modelica.Blocks.Math.MultiSum multiSum(nu=3)
      annotation (Placement(transformation(extent={{328,-394},{340,-382}})));
Buildings.Utilities.IO.SignalExchange.Read senPowPer4(
      y(min=0.0,
        max=25000.0,
        unit="W"),
      description="Perimeter zone 4 AHU Power demand",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "\"Perimeter zone 4 AHU power demand\"" annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={376,-388})));
Buildings.Utilities.IO.SignalExchange.Read senTemRoom(
    y(min=240.0,
      max=320.0,
      unit="K"),
    description="Core temperature",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
    zone="core_zn")
              "Core zone air temperature" annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={370,348})));

Buildings.Utilities.IO.SignalExchange.Read senTemRoom1(
    y(min=240.0,
      max=320.0,
      unit="K"),
    description="Perimeter zone 1 temperature",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
    zone="perimeter_zn_1")
              "Perimeter zone 1 air temperature" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={370,316})));

Buildings.Utilities.IO.SignalExchange.Read senTemRoom2(
    y(min=240.0,
      max=320.0,
      unit="K"),
    description="Perimeter zone 2 temperature",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
    zone="perimeter_zn_2")
              "Perimeter zone 2 air temperature" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={370,286})));

Buildings.Utilities.IO.SignalExchange.Read senTemRoom3(
    y(min=240.0,
      max=320.0,
      unit="K"),
    description="Perimeter zone 3 temperature",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
    zone="perimeter_zn_3")
              "Perimeter zone 3 air temperature" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={370,254})));

Buildings.Utilities.IO.SignalExchange.Read senTemRoom4(
    y(min=240.0,
      max=320.0,
      unit="K"),
    description="Perimeter zone 4 temperature",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.AirZoneTemperature,
    zone="perimeter_zn_4")
              "Perimeter zone 4 air temperature" annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={370,224})));

  Buildings.Controls.SetPoints.OccupancySchedule occSchWeekdays(
    occupancy=3600*{33,43,57,67,81,91,105,115,129,139,153,154},
    firstEntryOccupied=true,
    period=7*24*3600)
    annotation (Placement(transformation(extent={{-284,310},{-264,330}})));
  controller PSZACcontroller(
    heaPIDk=10,
    heaPIDTi=20,
    pid_r=1,
    pid_ni=0.4,
    PIDyMax=1,
    PIDyMin=0)
    annotation (Placement(transformation(extent={{-58,260},{-28,324}})));
  Buildings.Controls.OBC.CDL.Continuous.Division div1
    annotation (Placement(transformation(extent={{-214,184},{-194,204}})));
  Buildings.Controls.OBC.CDL.Continuous.Add add2
    annotation (Placement(transformation(extent={{-176,176},{-156,196}})));
Buildings.Utilities.IO.SignalExchange.Read senHouDec(
    y(min=0,
      max=24,
      unit="1"),
    description="Time",
    KPIs=Buildings.Utilities.IO.SignalExchange.SignalTypes.SignalsForKPIs.None)
      "Minutes of the hour" annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={-134,186})));
  Modelica.Blocks.Sources.RealExpression minutes(y=60)
      annotation (Placement(transformation(extent={{-242,178},{-222,198}})));
equation

  connect(calTim.hour, integerToReal.u) annotation (Line(points={{-276.4,164.24},
          {-250,164.24},{-250,164}},                color={255,127,0}));
  connect(HVAC.zonRetPor, corZon.ports[1]) annotation (Line(points={{-36.7907,
          19.625},{76.6,19.625},{76.6,64.9},{78,64.9}},
                                               color={0,127,255}));
  connect(HVAC.OAInlPor, Outside.ports[1]) annotation (Line(points={{-103.6,19.625},
          {-130,19.625},{-130,-176.4},{-234,-176.4}},   color={0,127,255}));
  connect(HVAC.OAOutPor, Outside.ports[2]) annotation (Line(points={{-103.6,0.5},
          {-112,0.5},{-112,0},{-120,0},{-120,-177.2},{-234,-177.2}},
                                           color={0,127,255}));
  connect(mul.u3[1],qLatGai_flow. y) annotation (Line(points={{-32,87},{-42,87},
            {-42,62},{-61,62}}, color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qConGai_flow.y,mul. u2[1]) annotation (Line(
      points={{-61,94},{-32,94}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(qRadGai_flow.y,mul. u1[1]) annotation (Line(
      points={{-61,134},{-42,134},{-42,101},{-32,101}},
      color={0,140,72},
      pattern=LinePattern.Dot));
  connect(mul.y, corZon.qGai_flow) annotation (Line(points={{-9,94},{58,94}},
                        color={0,140,72},
      pattern=LinePattern.Dot));
  connect(Outside.weaBus, building.weaBus) annotation (Line(
      points={{-254,-179.8},{-254,-180},{-298,-180},{-298,82},{-302,82}},
      color={255,204,51},
      thickness=0.5));
  connect(building.weaBus, weaBus) annotation (Line(
      points={{-302,82},{-264,82}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{6,3},{6,3}},
      horizontalAlignment=TextAlignment.Left));
  connect(weaBus.TDryBul, HVAC.senTemOA) annotation (Line(
      points={{-264,82},{-264,22.25},{-93.3116,22.25}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
    connect(perZon1.qGai_flow, mul.y) annotation (Line(points={{60,-64},{60,-62},
          {46,-62},{46,94},{-9,94}},   color={0,140,72},
      pattern=LinePattern.Dot));
    connect(perZon2.qGai_flow, mul.y) annotation (Line(points={{54,-154},{36,-154},
          {36,94},{-9,94}},         color={0,140,72},
      pattern=LinePattern.Dot));
    connect(perZon3.qGai_flow, mul.y) annotation (Line(points={{52,-244},{22,-244},
          {22,94},{-9,94}},         color={0,140,72},
      pattern=LinePattern.Dot));
    connect(perZon4.qGai_flow, mul.y) annotation (Line(points={{50,-322},{12,-322},
          {12,94},{-9,94}},         color={0,140,72},
      pattern=LinePattern.Dot));
    connect(HVAC1.OAInlPor, Outside.ports[3]) annotation (Line(points={{-101.6,-60.375},
          {-130,-60.375},{-130,-184},{-234,-184},{-234,-178}},
                                color={0,127,255}));
    connect(HVAC1.OAOutPor, Outside.ports[4]) annotation (Line(points={{-101.6,-79.5},
          {-120,-79.5},{-120,-178.8},{-234,-178.8}},
                                   color={0,127,255}));
    connect(HVAC2.OAInlPor, Outside.ports[5]) annotation (Line(points={{-101.6,-150.375},
          {-101.6,-150},{-130,-150},{-130,-179.6},{-234,-179.6}},
          color={0,127,255}));
    connect(HVAC2.OAOutPor, Outside.ports[6]) annotation (Line(points={{-101.6,-169.5},
          {-120,-169.5},{-120,-180.4},{-234,-180.4}},          color={0,127,255}));
    connect(HVAC3.OAInlPor, Outside.ports[7]) annotation (Line(points={{-103.6,-238.375},
          {-130,-238.375},{-130,-181.2},{-234,-181.2}},                color={0,
            127,255}));
    connect(HVAC3.OAOutPor, Outside.ports[8]) annotation (Line(points={{-103.6,-257.5},
          {-120,-257.5},{-120,-182},{-234,-182}},          color={0,127,255}));
    connect(HVAC4.OAInlPor, Outside.ports[9]) annotation (Line(points={{-101.6,-316.375},
          {-130,-316.375},{-130,-182.8},{-234,-182.8}},                color={0,
            127,255}));
    connect(HVAC4.OAOutPor, Outside.ports[10]) annotation (Line(points={{-101.6,
          -335.5},{-120,-335.5},{-120,-183.6},{-234,-183.6}},  color={0,127,255}));
    connect(HVAC4.zonSupPort, perZon4.ports[1]) annotation (Line(points={{
          -34.5302,-335.375},{10,-335.375},{10,-360},{70,-360},{70,-351.1}},
          color={0,127,255}));
    connect(HVAC4.zonRetPor, perZon4.ports[2]) annotation (Line(points={{-34.7907,
          -316.375},{0,-316.375},{0,-366},{74,-366},{74,-351.1}},   color={0,
            127,255}));
    connect(HVAC3.zonSupPort, perZon3.ports[1]) annotation (Line(points={{
          -36.5302,-257.375},{8,-257.375},{8,-278},{72,-278},{72,-273.1}},
          color={0,127,255}));
    connect(HVAC3.zonRetPor, perZon3.ports[2]) annotation (Line(points={{-36.7907,
          -238.375},{-36.7907,-254},{2,-254},{2,-282},{76,-282},{76,-273.1}},
          color={0,127,255}));
    connect(HVAC2.zonSupPort, perZon2.ports[1]) annotation (Line(points={{
          -34.5302,-169.375},{2,-169.375},{2,-190},{74,-190},{74,-183.1}},
          color={0,127,255}));
    connect(HVAC2.zonRetPor, perZon2.ports[2]) annotation (Line(points={{-34.7907,
          -150.375},{-2,-150.375},{-2,-198},{78,-198},{78,-183.1}},   color={0,
            127,255}));
    connect(HVAC1.zonSupPort, perZon1.ports[1]) annotation (Line(points={{
          -34.5302,-79.375},{6,-79.375},{6,-98},{80,-98},{80,-93.1}},   color={
            0,127,255}));
    connect(HVAC1.zonRetPor, perZon1.ports[2]) annotation (Line(points={{-34.7907,
          -60.375},{0,-60.375},{0,-106},{84,-106},{84,-93.1}},   color={0,127,
            255}));
    connect(HVAC1.senTemOA, HVAC.senTemOA) annotation (Line(points={{-91.3116,
          -57.75},{-140,-57.75},{-140,22.25},{-93.3116,22.25}},
                                                      color={0,0,127},
      pattern=LinePattern.Dash));
    connect(HVAC2.senTemOA, HVAC.senTemOA) annotation (Line(points={{-91.3116,
          -147.75},{-140,-147.75},{-140,22.25},{-93.3116,22.25}},
                                                        color={0,0,127},
      pattern=LinePattern.Dash));
    connect(HVAC3.senTemOA, HVAC.senTemOA) annotation (Line(points={{-93.3116,
          -235.75},{-140,-235.75},{-140,22.25},{-93.3116,22.25}},
                                                        color={0,0,127},
      pattern=LinePattern.Dash));
    connect(HVAC4.senTemOA, HVAC.senTemOA) annotation (Line(points={{-91.3116,
          -313.75},{-118,-313.75},{-118,-314},{-140,-314},{-140,22.25},{
          -93.3116,22.25}},
          color={0,0,127},
      pattern=LinePattern.Dash));
    connect(calTim.weekDay, integerToReal1.u) annotation (Line(points={{-276.4,147.6},
          {-265.2,147.6},{-265.2,138},{-252,138}},          color={255,127,0}));
    connect(multiSum5.y,senPowCor. u)
      annotation (Line(points={{341.02,2},{358,2}},   color={238,46,47},
      pattern=LinePattern.Dash));
    connect(multiSum4.y,senPowPer1. u) annotation (Line(points={{339.02,-88},{358,
          -88}},                       color={238,46,47},
      pattern=LinePattern.Dash));
    connect(senCCPow.y, multiSum5.u[1]) annotation (Line(points={{297,28},{328,4.8}},
                                  color={238,46,47},
      pattern=LinePattern.Dash));
    connect(senHeaPow.y, multiSum5.u[2]) annotation (Line(points={{297,2},{328,2}},
                                                       color={238,46,47},
      pattern=LinePattern.Dash));
    connect(senFanPow.y, multiSum5.u[3]) annotation (Line(points={{297,-24},{328,
          -0.8}},                        color={238,46,47},
      pattern=LinePattern.Dash));
    connect(senCCPow1.y, multiSum4.u[1]) annotation (Line(points={{297,-62},{326,
          -85.2}},                         color={238,46,47},
      pattern=LinePattern.Dash));
    connect(senFanPow1.y, multiSum4.u[2]) annotation (Line(points={{297,-120},{326,
          -88}},                            color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senHeaPow1.y, multiSum4.u[3]) annotation (Line(
      points={{297,-90},{326,-90.8}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(multiSum3.y, senPowPer2.u) annotation (Line(
      points={{339.02,-192},{358,-192}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senCCPow2.y, multiSum3.u[1]) annotation (Line(
      points={{299,-162},{312,-162},{312,-189.2},{326,-189.2}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senHeaPow2.y, multiSum3.u[2]) annotation (Line(
      points={{299,-190},{314,-190},{314,-192},{326,-192}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senFanPow2.y, multiSum3.u[3]) annotation (Line(
      points={{299,-222},{312,-222},{312,-194.8},{326,-194.8}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senPowPer3.u, multiSum2.y) annotation (Line(
      points={{358,-286},{341.02,-286}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senCCPow3.y, multiSum2.u[1]) annotation (Line(
      points={{299,-254},{312,-254},{312,-283.2},{328,-283.2}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senHeaPow3.y, multiSum2.u[2]) annotation (Line(
      points={{299,-284},{314,-284},{314,-286},{328,-286}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senFanPow3.y, multiSum2.u[3]) annotation (Line(
      points={{299,-314},{314,-314},{314,-288.8},{328,-288.8}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senPowPer4.u, multiSum.y) annotation (Line(
      points={{364,-388},{341.02,-388}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senCCPow4.y, multiSum.u[1]) annotation (Line(
      points={{301,-356},{301,-373},{328,-373},{328,-385.2}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senHeaPow4.y, multiSum.u[2]) annotation (Line(
      points={{301,-386},{314,-386},{314,-388},{328,-388}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(senFanPow4.y, multiSum.u[3]) annotation (Line(
      points={{301,-416},{314,-416},{314,-390.8},{328,-390.8}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(HVAC.yHeaPow, senHeaPow.u) annotation (Line(
      points={{-73.1256,22.375},{-73.1256,30},{244,30},{244,2},{274,2}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(HVAC.yCooPow, senCCPow.u) annotation (Line(
      points={{-61.5349,22.375},{-61.5349,28},{274,28}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(HVAC.yFanPow, senFanPow.u) annotation (Line(
      points={{-48.5116,22.25},{242,22.25},{242,-24},{274,-24}},
      color={255,0,0},
      pattern=LinePattern.Dash));
  connect(HVAC1.yHeaPow, senHeaPow1.u) annotation (Line(
      points={{-71.1256,-57.625},{-71.1256,-48},{236,-48},{236,-90},{274,-90}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC1.yCooPow, senCCPow1.u) annotation (Line(
      points={{-59.5349,-57.625},{-59.5349,-46},{242,-46},{242,-62},{274,-62}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC1.yFanPow, senFanPow1.u) annotation (Line(
      points={{-46.5116,-57.75},{-46.5116,-52},{230,-52},{230,-120},{274,-120}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC2.yHeaPow, senHeaPow2.u) annotation (Line(
      points={{-71.1256,-147.625},{-71.1256,-132},{252,-132},{252,-190},{276,
          -190}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC2.yCooPow, senCCPow2.u) annotation (Line(
      points={{-59.5349,-147.625},{-59.5349,-136},{238,-136},{238,-162},{276,
          -162}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC2.yFanPow, senFanPow2.u) annotation (Line(
      points={{-46.5116,-147.75},{-46.5116,-140},{232,-140},{232,-222},{276,
          -222}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC3.yHeaPow, senHeaPow3.u) annotation (Line(
      points={{-73.1256,-235.625},{-73.1256,-218},{214,-218},{214,-284},{276,
          -284}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC3.yCooPow, senCCPow3.u) annotation (Line(
      points={{-61.5349,-235.625},{-61.5349,-222},{222,-222},{222,-254},{276,
          -254}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC3.yFanPow, senFanPow3.u) annotation (Line(
      points={{-48.5116,-235.75},{-48.5116,-228},{208,-228},{208,-314},{276,
          -314}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC4.yHeaPow, senHeaPow4.u) annotation (Line(
      points={{-71.1256,-313.625},{-71.1256,-302},{176,-302},{176,-386},{278,
          -386}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC4.yCooPow, senCCPow4.u) annotation (Line(
      points={{-59.5349,-313.625},{-59.5349,-310},{168,-310},{168,-356},{278,
          -356}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(HVAC4.yFanPow, senFanPow4.u) annotation (Line(
      points={{-46.5116,-313.75},{-46.5116,-306},{164,-306},{164,-416},{278,
          -416}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(senTemOA.u, HVAC.senTemOA) annotation (Line(
      points={{360,76},{202,76},{202,38},{-140,38},{-140,22.25},{-93.3116,22.25}},
      color={238,46,47},
      pattern=LinePattern.Dash));

  connect(corZon.TAir, senTemRoom.u) annotation (Line(
      points={{101,102},{112,102},{112,348},{358,348}},
      color={0,0,127},
      pattern=LinePattern.Dash));
  connect(perZon1.TAir, senTemRoom1.u) annotation (Line(
      points={{103,-56},{120,-56},{120,316},{358,316}},
      color={0,0,127},
      pattern=LinePattern.Dash));
  connect(perZon2.TAir, senTemRoom2.u) annotation (Line(
      points={{97,-146},{128,-146},{128,286},{358,286}},
      color={0,0,127},
      pattern=LinePattern.Dash));
  connect(perZon3.TAir, senTemRoom3.u) annotation (Line(
      points={{95,-236},{136,-236},{136,254},{358,254}},
      color={0,0,127},
      pattern=LinePattern.Dash));
  connect(perZon4.TAir, senTemRoom4.u) annotation (Line(
      points={{93,-314},{144,-314},{144,224},{358,224}},
      color={0,0,127},
      pattern=LinePattern.Dash));
  connect(PSZACcontroller.uTCore, senTemRoom.u) annotation (Line(points={{
          -58.9231,297.082},{-130,297.082},{-130,204},{112,204},{112,348},{358,
          348}},
        color={0,0,127}));
  connect(PSZACcontroller.uTPer1, senTemRoom1.u) annotation (Line(points={{
          -58.9231,288.424},{-122,288.424},{-122,210},{120,210},{120,316},{358,
          316}},
        color={0,0,127}));
  connect(PSZACcontroller.uTPer2, senTemRoom2.u) annotation (Line(points={{
          -58.9231,280.141},{-114,280.141},{-114,218},{128,218},{128,286},{358,
          286}},
        color={0,0,127}));
  connect(PSZACcontroller.uTPer3, senTemRoom3.u) annotation (Line(points={{
          -58.9231,271.859},{-102,271.859},{-102,222},{136,222},{136,254},{358,
          254}},
        color={0,0,127}));
  connect(PSZACcontroller.uTPer4, senTemRoom4.u) annotation (Line(points={{
          -58.6923,263.2},{-92,263.2},{-92,234},{144,234},{144,224},{358,224}},
                                                                       color={0,
          0,127}));
  connect(HVAC.uHeatingCoil, PSZACcontroller.yHeaCor) annotation (Line(points={{
          -78.3349,22.25},{-78.3349,42},{26,42},{26,329.647},{6.38462,329.647}},
        color={0,0,127}));
  connect(HVAC.uDamper, PSZACcontroller.yDamCor) annotation (Line(points={{
          -100.605,26.375},{-100.605,46},{22,46},{22,324},{-20.1538,324}},
                                                                  color={0,0,127}));
  connect(HVAC.uCoolingCoil, PSZACcontroller.yCooCor) annotation (Line(points={{-66.614,
          22.25},{-66.614,40},{30,40},{30,335.294},{6.38462,335.294}},
        color={255,0,255}));
  connect(HVAC.uFan, PSZACcontroller.yFanCor) annotation (Line(points={{
          -53.3302,22.125},{-53.3302,36},{34,36},{34,341.318},{6.15385,341.318}},
                                                                          color=
         {255,0,255}));
  connect(PSZACcontroller.yFanPer1, HVAC1.uFan) annotation (Line(points={{6.61538,
          315.341},{34,315.341},{34,-42},{-51.3302,-42},{-51.3302,-57.875}},
        color={255,0,255}));
  connect(PSZACcontroller.yCooPer1, HVAC1.uCoolingCoil) annotation (Line(points={{6.61538,
          309.694},{30,309.694},{30,-36},{-64.614,-36},{-64.614,-57.75}},
        color={255,0,255}));
  connect(PSZACcontroller.yHeaPer1, HVAC1.uHeatingCoil) annotation (Line(points={{
          -19.9231,304.424},{26,304.424},{26,-32},{-76.3349,-32},{-76.3349,
          -57.75}},
        color={0,0,127}));
  connect(PSZACcontroller.yDamPer1, HVAC1.uDamper) annotation (Line(points={{
          -19.6923,298.776},{22,298.776},{22,-28},{-98.6047,-28},{-98.6047,
          -53.625}},
        color={0,0,127}));
  connect(PSZACcontroller.yFanPer2, HVAC2.uFan) annotation (Line(points={{6.84615,
          293.882},{34,293.882},{34,-128},{-51.3302,-128},{-51.3302,-147.875}},
        color={255,0,255}));
  connect(PSZACcontroller.yCooPer2, HVAC2.uCoolingCoil) annotation (Line(points={{6.61538,
          285.6},{30,285.6},{30,-124},{-64.614,-124},{-64.614,-147.75}},
        color={255,0,255}));
  connect(PSZACcontroller.yHeaPer2, HVAC2.uHeatingCoil) annotation (Line(points={{
          -19.6923,278.824},{26,278.824},{26,-120},{-76.3349,-120},{-76.3349,
          -147.75}},
        color={0,0,127}));
  connect(PSZACcontroller.yDamPer2, HVAC2.uDamper) annotation (Line(points={{
          -19.9231,273.553},{22,273.553},{22,-116},{-98.6047,-116},{-98.6047,
          -143.625}},
        color={0,0,127}));
  connect(PSZACcontroller.yFanPer3, HVAC3.uFan) annotation (Line(points={{6.38462,
          263.012},{34,263.012},{34,-228},{-53.3302,-228},{-53.3302,-235.875}},
        color={255,0,255}));
  connect(PSZACcontroller.yCooPer3, HVAC3.uCoolingCoil) annotation (Line(points={{6.38462,
          257.741},{30,257.741},{30,-214},{-66.614,-214},{-66.614,-235.75}},
        color={255,0,255}));
  connect(PSZACcontroller.yHeaPer3, HVAC3.uHeatingCoil) annotation (Line(points={{
          -19.2308,254.729},{26,254.729},{26,-210},{-78.3349,-210},{-78.3349,
          -235.75}},
        color={0,0,127}));
  connect(PSZACcontroller.yDamPer3, HVAC3.uDamper) annotation (Line(points={{
          -19.2308,249.459},{22,249.459},{22,-206},{-100.605,-206},{-100.605,
          -231.625}},
        color={0,0,127}));
  connect(PSZACcontroller.yFanPer4, HVAC4.uFan) annotation (Line(points={{6.84615,
          241.553},{34,241.553},{34,-298},{-51.3302,-298},{-51.3302,-313.875}},
        color={255,0,255}));
  connect(PSZACcontroller.yCooPer4, HVAC4.uCoolingCoil) annotation (Line(points={{6.84615,
          237.788},{30,237.788},{30,-294},{-64.614,-294},{-64.614,-313.75}},
        color={255,0,255}));
  connect(PSZACcontroller.yHeaPer4, HVAC4.uHeatingCoil) annotation (Line(points={{
          -19.2308,230.635},{26,230.635},{26,-286},{-76.3349,-286},{-76.3349,
          -313.75}},
        color={0,0,127}));
  connect(PSZACcontroller.yDamPer4, HVAC4.uDamper) annotation (Line(points={{
          -19.2308,224.612},{22,224.612},{22,-280},{-98.6047,-280},{-98.6047,
          -309.625}},
        color={0,0,127}));
  connect(senDay.u, integerToReal1.y) annotation (Line(
      points={{362,138},{-229,138}},
      color={238,46,47},
      pattern=LinePattern.Dash));
  connect(HVAC.yDischargeTem, PSZACcontroller.uTDisCore) annotation (Line(
        points={{-83.8047,22.375},{-83.8047,34},{18,34},{18,200},{-52,200},{-52,
          295.953},{-44.3846,295.953}}, color={0,0,127}));
  connect(HVAC1.yDischargeTem, PSZACcontroller.uTDisP1) annotation (Line(points={{
          -81.8047,-57.625},{-81.8047,-24},{12,-24},{12,196},{-50,196},{-50,
          288.424},{-44.1538,288.424}}, color={0,0,127}));
  connect(HVAC2.yDischargeTem, PSZACcontroller.uTDisP2) annotation (Line(points={{
          -81.8047,-147.625},{-80,-147.625},{-80,-114},{10,-114},{10,192},{
          -44.3846,192},{-44.3846,280.894}}, color={0,0,127}));
  connect(HVAC3.yDischargeTem, PSZACcontroller.uTDisP3) annotation (Line(points={{
          -83.8047,-235.625},{-83.8047,-204},{6,-204},{6,188},{-44.6154,188},{
          -44.6154,272.235}}, color={0,0,127}));
  connect(HVAC4.yDischargeTem, PSZACcontroller.uTDisP4) annotation (Line(points={{
          -81.8047,-313.625},{-81.8047,-274},{2,-274},{2,184},{-44.3846,184},{
          -44.3846,263.2}}, color={0,0,127}));
  connect(occSchWeekdays.tNexOcc, PSZACcontroller.uNextOcc) annotation (Line(
        points={{-263,326},{-116,326},{-116,313.647},{-58.9231,313.647}}, color=
         {0,0,127}));
  connect(occSchWeekdays.occupied, PSZACcontroller.uOcc) annotation (Line(
        points={{-263,314},{-160,314},{-160,321.365},{-59.0385,321.365}}, color=
         {255,0,255}));
  connect(HVAC.zonSupPort, corZon.ports[2]) annotation (Line(points={{-36.5302,
          0.625},{82,0.625},{82,64.9}}, color={0,127,255}));
  connect(calTim.minute, div1.u1) annotation (Line(points={{-276.4,168.4},{-254,
          168.4},{-254,200},{-216,200}}, color={0,0,127}));
  connect(div1.y, add2.u1) annotation (Line(points={{-192,194},{-186,194},{-186,
          192},{-178,192}}, color={0,0,127}));
  connect(add2.u2, integerToReal.y) annotation (Line(points={{-178,180},{-204,
          180},{-204,164},{-227,164}}, color={0,0,127}));
  connect(add2.y, senHouDec.u)
    annotation (Line(points={{-154,186},{-146,186}}, color={0,0,127}));
  connect(div1.u2, minutes.y)
    annotation (Line(points={{-216,188},{-221,188}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-300,-440},
            {420,360}}),       graphics={Bitmap(
          extent={{-272,-98},{280,212}},
          imageSource=
              "iVBORw0KGgoAAAANSUhEUgAAAksAAADYCAYAAAD70KfGAAAABHNCSVQICAgIfAhkiAAAABl0RVh0U29mdHdhcmUAZ25vbWUtc2NyZWVuc2hvdO8Dvz4AAAAtdEVYdENyZWF0aW9uIFRpbWUAU3VuIDAyIE1heSAyMDIxIDAzOjEyOjIyIFBNIE1EVEAuZXQAACAASURBVHic7L35jyTnmef3eY+IyMzKqu6uqr7vgxSbFCVe0gwlUlqtpN3B2J7Z3dmRB2vAwAALeGEMYMAGxrD/gAVsYHf9i2EYXsNrwN4FfHtn5DmkOSRxxNFQEiVSpMgmRTb7rO7q7jrziIj3fR//8EZmZVU3u0lJza5mvx+gkFdUZlRUZMQ3nuP7qO9//2+ERCKRSCQSicQt0fd6BRKJRCKRSCS2M0ksJRKJRCKRSNyGJJYSiUQikUgkbkMSS4lEIpFIJBK3IYmlRCKRSCQSiduQxFIikUgkEonEbUhiKZFIJBKJROI2JLGUSCQSiUQicRuSWEokEolEIpG4DUksJRKJRCKRSNyGJJYSiUQikUgkbkMSS4lEIpFIJBK3IYmlRCKRSCQSiduQxFIikUgkEonEbUhiKZFIJBKJROI2JLGUSCQSiUQicRuSWEokEolEIpG4DfZer0AikUhsZ4zc/vUAOHOnd/F3/BxR8U3U1s+T5qpWQN3xXRKJxN0giaVEIpG4DeEDKBQbbv+6oO6odKQRSZNiSU8IJPmA65JIJH75JLGUSCQSt+EOOgiFQoc7VDQoEO4QoqIJT8mGSFITtwCVvXOEKpFI/PJJYimRSCRuxweICAV1+4Xi67dfRpSKqbZ4g9rywx3FViKRuFsksZRIJB4YRASlFNLkvJRS48chBLTW48fjZX1AKYWxhhBinEmCNJGimF4LekMKBRG0Uo20ie+jjSYED0qhFAQfUFoRgkQxpDUhhBil0gqlND6EDaEkEGNYjNfbe4/WqUcnkfgoSN+0RCLxQCEiGGPGt97H1Ja1dvz6SEwBZFmGMYa6qgnO42oHgNGmETJCCA7n65g/IxDE432N1qC1IrgKgkcFB8FjFGgEowStBC2BTCnamYXgca4CFfB4vA54I3gTxuvmvR+vbyKRuPukb1sikXhgMMbgnKOu67FQGgkn59w4UjOKMHnvCc6jtcKo+FqRW7z3iA9YYwAhQzAmw3uHNoaqqiisxVUVRiusD7i6Zm1tDeccNssY9PtUVUW/36csSzpFB2Mt+w4eYGbHDnzwOATvQlM3JRjsOBrmvUfdIf2XSCR+OSSxlEgkHhjquqbVagEQQqAsS7IsQymF1hqt9Th6IyIMh0Na2oLWaKVYWloa/473nuXlZerhkJ2dNlevXuXll19mZWUF7z1ra2u8/vrrLN5YYrYoIISxOLPWorVmZmaGoigIIWCDxiOcuXieRx89zW/+1t/n+EOnmN+/F5Pn5EVOp9Oh1+shImRZNk4LJhKJu4v6/vf/JlUNJhKJB4KLFy/y+uuvj1Nwr776KhcuXABiHdDS0hJra2tj8dTv9+nqbPz73W6XVqs1TtNprWlpTSc4RISiKDDGoJQa10ABdNHUZYVS6iaRM3ov6xUmy+i7itrAel3SdyWXF6+i8oxPPHqaf++3/xGPPfYYIYRxRCyRSNx9klhKJLYJo0JevcV80Jn3iR7Ixu/YSpHnOUEEr8Fkll45JMszXAj4ukYrxifvW51snbbj18aFzM3rxphx5KWqqk2rMXrPWPsj5NaO013r6+tMT08jIhs1QdSxmLlJJTnnaLVaaK0ZDocsLS1RSBQvZVmytrY2/qyrV6/y7rvvUg6HTHlYXV3lypUr9Pt9XBCMgsuXL9PtdsmCouz1qV1N0WrhnGeqO0VmLUYbBGF3cGRZFouwtSbPc4zZ7DB5Jw+lu8VIcFkb037XbyxxofRUrqa1a5qHH3uUX/3bX2T/iaPs2jMP1lA4i3GKelSHlWWslwOyPI//S6OZIVDWFcbmlMHhfEDbDB8rzQkKjDg2myY0xgcqxJr2oDAhJSYSDw5JLCUS24hbV6BsPlsruXk5J02nl9YYYwgITmJkI0iAEMiajqsQAq1Wi7IsxyLBWovz8b73nhDCuBtsJB6UUlC58cl7VDvjnCNvTsbVcMi1hQXOnz8/FiFvvPEGa2trZFnGcDhk8eKlcc1QCIFerzfu7BIR6rqm0/wdIkJVVTjv0U1UJs9zjNZ0mnUfCYpR6qzT6USx5wJFky7z3o8jOqM6nxACLYnF2pPdb1vrgN5Pq95tJtOBo/Ua+Axb5AxdzWo1YHXYx+cGMsPBQ4d44unP8JnP/ip79+1jbX2NrN2i9A5lNKIVXgJ509XnfcDqDMJon5ro91FuYk1u3gBNXO0ub4FEYvuQxFIisY1oOsSBDbfm0cl63DY+EVFSxGv+MhOUMO7s0gJ5nlOVJcYYMqWhiSYNh0OWl5fHYqQsS/r9PlKWtNttbty4wcrKyvhEvbq6yrVr18jznKIKLCwssLi4CMQOsnPnzrGyvo7RGgtk2lDkOaZpwZ+amkI34kdrzWzRpsgynIsn5KIoqOuNaFOe51DXm0TCSMQB4/VWdT1+fSTqqqoat/4bpaFJt4UQqOs6vvdoW4tQNqJg0kJgO4mlyUJzpRTWW2hEj0NQuaWWQEDoDwZc6vW4ur7G9FSHZ5/7PIeOHuHE6YfZvX8frakOQYSe0uQ2Q3ygsDm+clg0RjQK0EFT2yo29jWCaNJVXEnc59yd5sAkEh8jklhKJO4xUfBsCCUBRMWfTcvJxA8TgkkEryoMCqsNF86d49K5C/zwpe8z3Z1msL7OO2fO4OsagOFwSFVVm0REWZa0GjHVarXI8xxr7ViojO9Xnna7TVEU43TcSASFECNYthE9IYRxIfQoAqWUIg8K23SijWqHRmJntKy4evz8aLlJDyQFG/5HTeSrqqrxehpjKOsa5914Pay11M02GL2Xs3G9Jj9rq1i6aVbbR8ikH5QEYcpkOImF6e12m6rZTihFXdesB49ptzGZZaW3zvqgz1JvjazTYv/hQzz3heeZPXqK06dP45xvYkYKrW2z/42iRaPI0qRYintdvB8IOhWXJx4cklhKJO4hI1Exuu9DwGZ2U7qo1DEF5cqKzFis0litKQdDCML1a9e4euYMf/1X3+WFb38HHYRcG04eOcb0VBcJAYug71AMXPg7n/z8naZ6SBRLtyOgok317d7njkNG7kzgZsG5FVF3TiXdS7G0mbGkBm6RBJMYFVLEuqPQmGXWEhCj8RJYWV9jcbnP+auXeebpz/J3/t1fZ9/xo+zatxfbnSIYBdZg6gphVIwOg7Imzwtq5zA2i1FKcePuvmRhkPi4k8RSInEPUSamPryLdULWGDpFi16vh2pSaZIH+mvrtLIcLbB45Sr/9v/+f/jeiy/SW11nfnaWo91pxAeCc9T9Ia6u2Ts7j9WG4D3mA4zKsHJngVLfUSwJ+g6f5T7Q6I8PIpbuNGLkzu+g76Sm7vgpHx2C4HUTaWo2sd6yqXOvMM3fFJoopUcICKaxKwhOofOcxdUllvp9hiqwUg2ptOKZ557lt/79r3Fgfh6TWbKiReUDa4MhylqUtpg8py4rjHfjSF+yMUh83EliKZG4l1iD1RqC4J1DBUEHwWqDr2rWVte4vvAuf/1X3+XHP/oxK9dvYEUxMzXFdGeKVl5QDobs6nYohyW5zbhy+TKzO3fRyYsmGCEoJXAHMaQ+gCy4swDZHP245Xtg7qhAvLrzwFiNue3rH+TAdqdo23ZCEGRLmGvrZtRB3SwAFeOCfYDCWCofCAq81tRKwFrKELi2fIPVXh+0Z27PXn7lc5/j0Sef5OipU5DlKJvhUQQJSCOOrLWbDD0TiY8jSSwlEvcQRwCBVpYTnGdp8Rrf+fO/4Ccv/5gbVxfRKFrDFYoso2VzOkULak/LZgTnyLTF1TXLrs+ePXu4eP4CIOyenYvzyUTQSgPhjlPvwx3EB9wcybgZuWPeSgXNndSS17cXSwpQcvvW9Q8WEbqzKPsAwaePhqZWa/xw68sqDuwdLRW3Uax7ssYgzaw5rRyCbqKOAR+aQno0CDjncW1FWdcs9frURlOiCFnO/IEDfP4Lz/PZzz1La3qauq5TKi7xQJDEUiLB7aMQ73cKUEoR/Gg4qoono4kThmhFhcdoEwuftSE4H09YKJZv3GDh/FkunDvH22+c4cxPf8q1havMTe9g765ZOkWLUDk61LEepRnqmltLXVXkNocQUFqzLCUSAjeuX+fQ/gNYbaJmkdglJ0ruLJbUncXSnRqg7vQZ0AiuOygQuZMq29rqfpvlbssHSPdtH7F0ewEoxJqySbEEI+0aBwUbpUE5RFSMYqqmA07FiJQEwdqMXijRxhCUpkKogazVZmltjYuXL+MUHHzoJI8//jhHT5zg4NGjzO7Zgyly0AYXQqx/UqoReQqNQmuDq2qMjoLZhNj1iI7LxrikGv/bRI0E+uSeJZN/GEr0B4qKJhK/CEksJR48RI0PruOdX20+r45qZm4XJHGuplUUzdV5M2MsBJRqOq0I0DKsr62zszvN1YuXWbuxzI9efpmXvvsiVy5dZicVnSJnutNlqmiTa4OUNbYJ0Iw0wyj9NWpKChPrLAi6XXD54iU6rRY7uzNopTBj/5yNDrtE4udhq42BVzBUwrCquLa2St8F6izjU5/9DJ988ilOf/JxZvbNU3sXhZLS+DpeWHSKDtWwJC8KMtdHkJgSDBKFktJIEyETBCvNcOLx/jsq2Gq+o8GgJaUAE3eXJJYSDxwmKExQsT2fDRExFiQK3M1lHxtX6s2tp0Jr00RKGkPH2mGNoS4rVpeXubF4lTde+yn/5//2v7N6Y4mdU9McP3yEHTMz9Nd6dHMfZ4Y5F4ujBaw01TgTbt53EktBK86fP8+p4ydwVY3VBiNJLCV+OYy6Mzf9GE3lahyKYDNWhkN0a4prS0tcWLhEuzvF559/niefeZr5fXuZ27uX7q5ZVvs9ujt20C+HFFYQCTgXMAJamRgpmthZZZNFwa0igXduGEgkflGSWEo8cGR+owh2LD4aX6NRu3nVZKS2GkDCRst21tJUwyFT7Q7D9R6tvOAbf/TH/MH/+2+5dOEiuQin9uyhlRcE52hnBZk29FfX2LVjJ8F7qjCMmYog44JZo/T4M0bRpduLJTh74RxHDh6KIzuMRQXZ5Mk0Wj6R+HkYdbqNoksGaGmNDwEXYFDVeKUxRUHR7rDW69FutVjrrbNWDrnRX2dxbZWp+Tn+3j/6Gl/5d36dSjymnWOUoa4qrBh0iJlRLarZdxW1GdWV6c3mmIz27ZAuBBJ3nSSWEg8cOjS6YdIAklGBbFxGRnJFojiaFB4Qn3v3zCu8+uNX+NH3f8DVS5cZrg/Y1e2yoztDbi2FUpjhkFarxbA/YKpoIc6jhFiz4QOl8ijdCLfRaAuzOaVgwu3Fkvee1dVVdu/eDRJrU6zSSSwlfqlMGmRqEVoa6ioaenoREI3oaHSKaFABbS1D7/BGo9sF13trrNZDrq+tMdXtsvPoET796U/zycce5+DhQxStTvwsAHS0SzDS1N/p5tmN+xE/UeWUSNwdklhKfOwxxlA2Yz+89wQdxcfIeXrk4BxnqkFd17SCoEIc/qpFGKz3ef0nr/Gtv/hL3j5zhhACnXpAK8vp5AUtm5MpjQlN6kxACATTdCBN1KSOUmtxGTbVSwmNMJpIDWZ+s1gSBJTChThP7fyFC+zbu5epqSl81Thfp2914q4i6E0pMTWxz0Uh45qhu2MTUmkuQtTGMkveUdYVA+cpVcB0pzjx6CN88Stf5sQjD1O5mnaWE4LgJSCikKDI2x3KsiSzOdQVVsk4VThypk8kfpkksZR4IAghkOc5zjm8AbHNGI0QyJXBoCiHQzJjqYclqxfO897Zs5w7+x5vvfEmZ989ixXYPTfP9NQUSmBKPASBxhvJNCeMkVjyWhhmm00Ex5GpiRrVyciPTC7ErcUSCpz32DxjcXERAQ7u3jv20hnNTksk7hYBIehJKwONlsBkqqw0fjQgBS3RXdwE0Ohm3p6mVh6nhFprfGFYrUuWhwMuXFuktaPL45/+FAfm9/LwI5/g0JGjzO7ZS9Ca0geKVofaB6wIWsLYIDOEkDyfEr90klhKfOwZTaUfzUPDQJCA9oJFkxvDxXff481XX+P1V17lRz94Ge1WaRctdkzP0C4KdIBMaQqboXzAVTVimyvZpi16NLNslPryKJzZ3I5/c8QnbE6Pyc1jLLam4YIElNHUznF1cZHjx48j/TIuawx1E3FKJO4WUbTfah8LE/fivr1R96dRMqrH082FxRBlDUEpSufB2rj/5jkYzer6GlprFq5coVfW7D16lM889zxPfOYzzO7bhyjF1Mw0lXfjuX7G3NkCI5H4sCSxlPjYMxmer6qK3uoyq0tLvHPmbV789nd46YUXmetMs39uN3PTO9BBwK5HTxrnMWhaWQYu4MsKqzStLGfJbEysvyWiUBIP3O8nXUapiskCcrVFMG0VSz54TJZx/cZ18jxnx86d2CqeKEJT94RJYilxFxGFHpmCjq8AJtv7A6ZJhYlSBFRMf6MRpccNFVm9SpG3sSiG/RItYFAUNiezGc45BqGmCkIxPU0/BFad49yVRc4tXObA4UN8/te+ypGHTnHy5El2796dIquJu0ISS4mPhFhns3HVeauaGjPh7Czj7rTGjE4rvA8YG0d4BB9D/NYYcGHsVFy7GtcFqzVZAFV52kFz/eIC/+v/9D/znW/9JbtbOTtaGTMzO2i3WnF91FZbO2FjAIggYzEzasSfbMVXzbO3+iptNgi8ebvcmsnlTYA6eLAaJ7GOajgccmVhgcMHD6IEiixvakKa1EhyU07cTT7IjrtJsKhbdqyp5rsFzS77vu+7uYQ7unXEZ2qtWRuWvHv+PSoRTpx+hP/wn/xHnHrsMcrgcQoGNouRXy8YHQdRB+exaKwxVGWJUjVaazJjUSKIDxvp86YjtZ64CJlcn5FI1PL+3/XE/U0SS4mPBtlaEHqLOWNiN6RII5YUCucdoREJToM4DyIUNsPXjm6rjfjAcDCgKArOXfgZr7/6Gu+8eYZ3f3qGtWs3yJXhwOw8Rmk6RjDiNs3L2s5pK+UCZGZ8NY5SvHf2PQ4fPEh3qourqlg7lUg8iGhDQOEkMHSegXcsV0P6VY1qFzzy6GM8/sxnePTRx9g1OxutBoxGGYPNMpx3caB18FRlNR4MPFJxI+uQKO3uJIWSWvq4ksRS4iNhZLgYH8SbrWKpVlvGFjS/k9l4QAveY9qa4D0ahfKBXBsunb/AX/7Zn/PDl3/MyrVFpoLHKkOn1aJjc1o2Q9WeqVabuqzwoUJNRrm2eRTGoAgKhnWFLXLW19epyords3ME7wnO0yqKe72aicS9wQc0Gp1ZvAh9V2NabQZVBZmlrGvq0jOsKtbcgIPHjvGpp57g6c8/y8HjR1kZ9LBFjhWLD4HaOZTV45osmYgaZX7jomrTUaM5tgUVklj6mJLEUuKjoekSmwzFj/yNRtQ6jiEZFYRqYrdYqB25zVAinLt0hqtXrvDeu2d58yev8+6ZtxmsrbNzeoa987uxSjMTYvjc145MG7RSKC9477Da4FQgsNExIyLbWzDJhAeUVly8eJG9e/aSaRPbqr1PLjOJBxbtAxqFl3gBZIsCFwAThwFrbaAClRm8ViwPeyyuLbNaD+nO7+ITn3qcQ0cP89Cpxzhy9Cjt7hS1BAIbZrVxRp0ic7cWSyqJpY89SSwl7joio7ojHQdmNvVFilj8KdIYDmlAmhb8RiT1V1e5tnCVV15+mT//02+yfOMcnVabPXNzdFsdtBeyZrQHLqCVInMVxliMUpRlidKaIs+pqgoFmCyLs6j8xsT57SyWwsioUimuLF4lz3N2z88TKofyzYDe7bv6icRdJY4G2kip+xAAhc0ylFJUZUluWlE45ZZgNN4ohsFRiUcyy+raKpeur2OM4ejJ4zz35S/xyKOPMr1zB8VUG9EqRpomTNAEGXfBjlxuVSPYRseTbX8hlvjAJLGUuCs459Baj/2NbJHT9xVlU1/TnZqiHAyikApCKy9QdcXiwhV++tpr/PCl7/PmT15n6eo1dk3PcHj/QXbt2IFfWwQYmz+Of0ZmkApq7Tety82FpYr7aUq5aMVgOCQouLa4yOHDhzGNAaZpsolh+5ZcJRJ3FUGQLR0j44cqpvID9n1+d4PQ2UHpHMOqZOBrXn/zDWbmd3H05AmefPppHvn0p9h95DDtdhulNaN4rsksguCcp5u3GQ4GYxNca2/9uYn7jySWEneFsizx3pNlWTSDFE+lA0ZrMuKoj1A7cm34oz/8Ov/j//Avkd4aszM72L93H7nNcGVJt2iTobEoiqKA3grwPo7YxAPnINvYpTel/ZpbHaIv0v1CLQFtDctrq3S73SaSpuLg0Sbq75NYSjygeKWQcSvdqAS7mWXXfOudMuPaax2I3x2JFxsjV6bK5HiESjxBgcosFR6MYViWXF1Z5uzSEiazfOWrX+W3fudrzO/bi7aG9eEAtKJQORIE59w4qpR8nz4eJLGUuCt475Gmgw0gBMfa6g3efuMMb7/xJm+/+jqXzl2gpQw7Wh06RYt2FrN0WsU0nAoBgyIzFl/V8WpRy21TTtI4C98OJfdXZKlWQuUd58+f5/jx4xQmQwXByEaErU7H48QDimCi4eVorLQSolhqwq5K4jJx4U3t/ZPeZs450AqlNaIVQx+tBBwSn1cGpTMcwuLSDXp1ics0O3bPcewTp3jq6ad56LGnaHem4kc1bvqT6f7E/UsSS4m7wugA8cILL/DNb36T61cWMIM1MmuZzlp0TU5HZ2ROyJxgjcEzRGtF8CGOEFFqfGAb6Z9engETxeHNUFkZPye0/eYRIyPGQ2XVrVJz25daCecuXuD48eM456I3zCiyJEksJR5sdLBoMTT+9vFJFRC1IZhMsPE4oTbmLwYNfmIOY9vHaJAo8MQ6Qd/UWwYE4xUtlxGUIlhNpYXKQA9Hry7pVyULpcdkOUePHuPLX/7bPPvssymy9DEhiaX7GBs2TvqTB4Jx5xSbGzNuFXBR3pM1tUWjsSAhhM3DKFU0dBOtEK0ICB7Z9Jn10iKXz13g0tlzvPXKa1w7d5HFC5colGHPrjlamaGwabjl7RgdlIuiYL3Xo9VqUbma0C8ZDAYcPHiQwWCQDr6JxDbFqxYuCCv9HourS/R8xZGHTnLkE6c48tAJjpw4zvTBI0y1O9EvznuKrEC8R3zAKj2uh3LORbPc5qeu6zjYW2uC1CgVjXMjo4SjHj8Gdw+2wMeXJJbuY8y4XXXz1PpRqysCRuKXZzLKMlneUimPGIVWCu88Wohz1IYledNN0ndDcpthBIJzGFEM13v0VtZ458xbfOMb3+CN11+mZTPmZnayZ+csDCo6WYEVUF5QWvAqfXlvx+h/V9c1rXY7dvKZ6D6+d+9esizDe5/EUiKxTVHeoJRGmo47p4RSRaPMxRvXuXTjBp3WDJ9//jmeff45jpw4jsktebuNKTKcBFCKunQU7RYiwrCuMFlTKN5c2FrnseNj+oRAko2ju9fpePvLJIml+xgjW6bRs5GaGj3QE1+e0T0lGympfi4MdUB8INMagyZUNTNTXeqyoq4q8o7i2pWrXHrnPX7yg5d5/Qcvc+3cZfIA+2fn6eQt8umM3FqC8+A8UkVPo8JaxAfq4HHZR7JZ7ltGkaUQAroRRIvXrzGTt5mZmRlPU0/tyInE9iSvGKfyMAbRUHoH1qCtYVAOMbUlGMW13irnF6/QntvByU+e5rGnnuDhTz7K/kMHKXS0K3DBo7SmJuBH458UFMFgm6tkNRpNLJNRJfC6ujcb4WNKEkv3MUpurr3Z+s8M4xnfGwJpXOAoUFpPjcfqWAdTlyWFyWjbnDde/Qn/4p//c9752Rl2djIO7N7LrqlpOiZDlY6WNkzZgquXF9gxvxMRIYjgnWO622U4GOKdi0XeRuNuNRAuMWYklgBoPKKWV1c4smf/ODWaBoQmEtuXvCmgHB0LR99npTXa6Hh87EUnfsktQzzLZR/VyqlV4L1LF7mwsMTxY8f4vd/7PZ76lWcYOkfpa7JuB6V1nGaAiS5PwkQ0STelFk02QSWx9MskiaX7mCAB3VjyhxA25bcRwXuPzy0igq9rCm2jgWHw5CbD1TWZhkGvx6ULF3ntlVd49Yc/4tJ751FBaGc501NTTDHAGoNSKraqj1r1RSDIlvom4tBLCbHjbFRHdZ95G90LxvVmIWCzjPPnzzM7P8eOojOOJqWoUiKxfYnHvclx25vLHiC6vMm45jMeI4OKj0cDg/vesry2Sn/QJ1jN1I4ZPvXUkzzxmac59fBDmJkZ+iFEw1qlMMairaUqa7S1BC9kwY2j0aPzwuhiSyk1PmckPhhJLN3HhHgJA8SaI601VVmS5TnlcEirKBiGCq3jFUeuLSoIg/Ue773zLi9+97u8/sorDBYXyaxlpjtNjqaV5XFMCAp8oOMH4w6SkfgJYxEUT/BGRq62G2yNepn7qQXtHhAvChXOOYZlyXA4ZM++vZg6FcYnEvcDfqs5ZnM72VzjlTQXmxsRfybvA0OVoUwcPV4TyxjWywGr6+t4CRT79vHIE4/z/Be/yL4D+2m1p/BK8KLAKIKXcU3rpFAapfEnm3kSH4wklu5nTHPN0kR4nHMUeY6rHZm1BO9QvmTh8gLnz57l9Vd/wvl3znJt4QrD/oAd0zPMddq0jYkt9d5j0XEmm6jmfQMFYVPL7ajbbiyYFJjGQvr9xJKSDfO3xK0ZpeGUUrx79ixHjx5FGU0hyXEykbgf8O9zPTj+Bgt4HcbmmKOyiLGxblNP6nWGb1J5ookF4yFg8wwvgVVXc319jRsrK3S6XfYePMixh09x+lOPc+joUeb37CGY2MXsvR/PwfTej73vnHOpWeRDkMTSfUytBAlxiGRuLRKE9bU11lfXuHzpEt/80z/l3I++T291jfnZOXZ1Z2jZjFxbMqUQL1gtaBXwjeOs1dFEbfTFRSCYjRqn8c3WWimJX8D3jx1J0+qaeD8mxdLK6ipzc3O44MnT4LdE4v5g64XNlgkCsYTBjbuVty4zWlCFaAVgwoj1HgAAIABJREFUtEaZ+FNVNUqPvGIEEdBZhljD6rDPAOHS9UWW1tbYc2A/n/+N3+TkyZMcOXKEdrtNlmVorePxPaXfPjRJLP2i3GLrbZ1TtBXV5LKEOMssDpWNO69qbPtD8/z4d5SCEC8/Rrt5HRy+dly6eJHXfvQKb7/1Fn/z4l9jtGFmepr5XbvYF3z8YgUB5ymaURk0Ikvl4EI9vuIwRhOCEIIff36l7abC8NGIkUknXN/EjSYPFZObQZQQdAr53oo4iDOGyYOC1157jSeffDLWlBU5qkoOwInE/YDxmyM1m8YtNfdt8BsReqI5ZqxXGkXqhcxtHsZrraWu6/EIqU6IsyFrCdQikFsqo3E2NtI4hHfLiqXlZXq9dfYfOMjpR0/z9DPPcPr0I7Q7HYqiwAVBmorSUQ3sZF3kVj03ea5ibPMkWwTfLYTYrU6J95leS2LpF2C0n+gt+0o5Yb54KyPI4AV8nBmktUZrjVGKwWCAc44sy7gqPfIip9NqIT6A87RtDs5z49p1/vLP/px/89/+dyjnODg/x7GDh+MEeoGWzVAhptXQ6US7nVFK4SXgEUQpVtZWyfOcuekdhLLGogj6PjuqJBKJe4+K86NqJfRdxVA8tRZeO/MmK5XwpS89y/O/+ff5lV/5FYbDkizLqIc13W6XsqwYDIa0WgVGa+qqotVqMdXusr6yHj34vMI7R22HjdDbMMjcepsHN/JWv6n+9X4hiaVfkFudxoIKNz8/IagCcfjjqOiuleW4qkY3HQrOOYIryaxlsN7nBy+9xPe/9xKX3jvP2vIynaygVRR0TE23M0WmNMoLOkgzFilEASegbTrRbme892hrQSv65YAbS0scOnBwY8invH8dRCKRSLwfNsQ6J68BawhG0a9LaoSsXdAbDLi21gejqYNw4MhhHnvyST73xS+y79AB1gd9tIo1rCKCsTlFURBCMyi9CZUVUjefGBVQrN7QbMoz3MKQ+H4THkksfUgmU82M7k8UOsNGNGmUhhoX7jW/45Uw1NEtOzMWX1ZYbZDasba8wkvf+xt+8t0XufLeWQbrPWa6XabbHdpZgVYKqRztdpuhH8YcdF1jtYnFehJTbhu7aUp9bWc8sYjTWMvFSxeZn5unVRRICOTKYFD4++6wkkgk7jWF06AVosA1NgGOGMU2WRYLvINGFxnD4FjzNctVyVo1oOcch08c59NPPMEzTz3DkSNHULml9B6vNFiDRxEUTFfxfCOosfXB6Aw0uvUmej6NMy1bM3f3AUksfUgmzLE3CaVRWBGiPJl0y9bNwuNFxKPw9Nd7vPna65x962csXLjIu2++xfrqGp2ixYF2QctmWN3UAomgA2gU1hjqYUko9NgvYyTUJvPck48T2xMPoGBlZYWqqjhw4ADeOTJtmiLO5KuUSCR+Dny8UJ703ht5Lo064WztEGPp1yWtmRn6rqL0ATLDoKq4sbLC0Hm6O2Y4eOwYRx86yYnTpzl44hjZVAdR0AqmScEpBNV0TuvxLQCNm/jk9IjJc+L9IEKSWPo50M18HoBoRRTGrZkiQm0lptRqh1Eai6IcDBn0+lxdWOCdn77BX//Jn/L2z37Gzk6Xw/sPMJW3MBLTLjEiVaLUxM418uFgI2K1qXiQjWG6951kf8CYFLKVxP7hq1eucuTQoVizpjcXiaYmwkQi8WGpR4eRLY05m7yfVKxpVaKa44xu7scybqdgqAGtKENgtezz3pWr9ILn5KmTfPXXf419J06we88epqa72LzAeY9XCpQmKFDaYuqyMc9sphCEzQe1MHEO3a4ksfQh8RLnqOV5joQAIhRZTlVVEGIUIKgKV9X019d5+40zvPjCX/HOmbe4snCF6W6X3dMz7EKTWUthM0LtsEqPhZISKK3biBbB2LQMNk6eRsImwTSZcNto79/eO+CDxlandd0pWLi8QDsvmGq3yW0WC/rZ8LMyKZOaSCQ+JMOsOXDcwsdpdFbwOta5mqAwEuucdFCYEMVSaAYBYyzGWmqBgasYeEdeFKz2+ry1tADW8onTpzn58MN8/vkvMLNzJ63uFJ2pKergybBUVUXtY0QrNOUHPgS00RStFq6q3+cv2R4ksfQhubG2wvyu2SiUXCC3lkwZVBCWr9/g2rVr/Pf//J/y49fOcGzPPHtn55jbOYsblvi6jvPcQkBJFFxWa7xz0ESVaHbmysgmsTQZMBpHltjodLuFVUfzQhJL24nJ8QMAveC4fPEiJ44dI1MGfBjP/PNNe7FNYimRSHxI6uYqa1wKwuYotWZjFqUW3VyUb3SwjRJrouLYlBBAKU1ZVrQ63RgFzzOWh31mZnexvLqKMobzly9xbWWFXvD8B1/7Hf7B1/4h2cwurDE4BToz9MshdQgU7RZBQX/Qp50VH9GW+flIYulDUkkszM6N5YcvfZ+/+ta3WTh/kZVrN1Ah0C5a7KWmO9XFALoOGFFoEcQHjNZ4JfRN9DVSAj74TUnbeAWwOZ82mX4bUZuoxMez2kbLTnbeqeTQut0YjRzw3nNhaZFdO3cx05mCymGlKZJU4HXcLZJYSiQSHxYlN19Mb72otj6myrxWBBReK7xSjQ+UQgVPLrGcJLhAZmLkO89aDAYDjFJkWjOsSqamp+mVJRiNR1FKYHV9nTp4rqMp2m0OHzvKr37hOR799OO0p7uIBieCzizabe8D3X0hliZbp7f+s0cCYmRyPFbQIZacaWJhmyCozOK935iR07yfNgbvHE486Ji71UqRaUOoHeICg16PN998k1f/6lucPXuOhQvnaecFu6Z30MqiK7Yh/q6VepySUyIoUeiJKjZR4LSMDb5GJ89b/V2bnrtpu4RNz49fnxBLkiJL95bm/zjaL0XH7jZvoOi0WXjvArvn5zFKY1AYrXHOg9pIq6b/YCKR+LAoubP40KLHndwjk0wZdbQp0EEomvqiWEKgUVrjnUcbHc0sVTTVDSLxnKp1U+gdL/x88JQmI4hjfbDG+qDP2nDA1I5Zjp16mGeefY5PPvEkzGRYa5umFo1r5tcpNMF7xPsYnXKOPI+lL6PRLR8F94VYut20h7GoUBt28uPnR2JEaZRWVFITfCDLLK52GBMv3b33GK0xRqOVohqWnDt7lvPvnOWtN97kvbfeYfnGDRBhXw6tPKfb6YAXgnNoFd1URwXYLp3dEiMa4ToSSx7Baai0cOadn/HogaO0i9a4aSB1viUSie2CkhjZnrTGGXf/N4+9Ds3UiskFNJsv7xUKDyoQlOBRVKJYH9bcWB/QL2vmThzk4KFDnHz4IT5x+lGOPXSKOnhcgCBCkVnqsiLPc+q6pt1ux1rhj4j7QiypDzCtXovaZBmPaZyRGzt3AYzytIqCcjDAGhvnodWeuq64cnmBpctX+P53v8sL3/4OwQd2z+zkwN69ZGgkBIzS5KZCfMDVFZm2ZNYiPjRt/RGfxFJixERhJUDlamynxeqwz7XlJU7tORDHzjQWEJDsHhKJxPZgHIuQjaDFTUcnVbMx+2RkzR3zOiO0CLp5NwFUluEIVCEgxqIziwxi+u/i4gLvXVvEFxlf+rtf5TPPP8f83j10p6fZuXMXIQSMMfT7fYrio6tzui/EkgmGyX/R5AqP/oFZCJvm7TgCaA22CTNKIBdHXVb4uub8u2f53ot/zU9++COuLFxhqt1mT6tNRynyLKOVF+AC0nSqZcZQVzW+JYiL9UbiA+I8RuktHQYfzXZJ3Ads+XYpo+mXQ85dusDjTz5BWO0jfqNDLkWXEonEdiEQz2e3KvGAZkYoVePbrZoCcTVxP54MlarRoqAZuG7znKCESiqGbogLjtlyR8zKtCxrSlgOFSuuYs1XXF68Cjbjmc9+lt///d/f1FH8UfHRJfx+AbyaMK7aEgocUTV/yegK3oqK0abSMxgM6Pd7/F//5l/x9T/4/9DBc3DvPvbN7WZf0WZu3wG0UrQkkEszMmRYYrVGvKfIDKGu0a7GVUSvCB9tA5TW94ejVuLesOW77CVQVRX79uxlceEKu6d24CROAb9V7VoikUjcSyabhzQb59iNuae2OUGPltQToin+llcBwQIx8FHXCgwErVHWQhAqEargqSrHe4sLnL9xjcV6iM4srU6bEydOcuzYMayNNgRZln00G6Bh20aWRGQ8aHYgYKxFKUVdxTRYlmVUw3K8nOkofFnRzVssnD3Pn//Rn/Cz19/k2sXL4DwGRXvaMN2ZIteGUDlybbBhw3vCa4+ojXGAo1qTydbLkdHXVhfSTeueAgMJiI0FjaAejSyp6prr169z8OBBnHO0TJY8RBOJxLZEAQbVWAc0tiZNg1TWjNjqNcXccRlBNdEka20cwQWs+DVyY1FYnAtcuXYdr4S14YAb66us9nvYbsGjjz7KQ594mOMnH2L33j3Mz+2h1WlTFC1su43cQ+PKbRlZcs6RZVkc4yFCsAIS8LVDfKAwFuNrOhr6630WFhb47g9f4M3X3uDK2fcwDmZMzmy7y8Ozc7ElW+vYau8EJS4On3UbA2eVwFALtWoCh6OC3FjQj4fxcNNE4oPRdLcFT1CgreHG4hK7d+8G59k1PcOg1487WCKRSGw3goAPMctiYsCirCuCgooooFxeUDsPGmyuEBxVXTIMgbosWVld4trQU1dDfOijc8uu3QeZ3bMfUxv+03/8H7N73yHK+YDGRINmNNTRzFKpaL1zr0+921Is5XmO9x7vY21QFgL1cEChDatLy7x15m3OvPo6F945y/K166yvrDLVEqY7Uzy2ax5fVrRtjg6g3BCtFUYLgfgPVUFwroqqt8nvjQy5jOib87KT9yfaMUcF5YnErWgMK/AINs/pDQdorSmKAuOFweo6yiYfrEQisT2JNjdgjMIpwRFQ3YIgQk0gIKz2r+B8RX8wZHVtncGwT54Hujt2Mz+3kxMn9/HFg/vYMdtm9/4ZZnfPols7uHSt4ut/8gMOPnwCR4dc1tDaxqHyTlDaEjwYpRFtINTcy8Hw21Is1XWNUgrvPZcvX2bx8nu8+/bb/MWffIMrlxbZ0+1yYHaembzNoVYHMQVdKQkiuF6JzTOcd7HQWxxOK4yx0b+GaAqoWxkubN7wOtxsAKi3Fug2t0IUUSIp7Za4NYoYsh51uS0sLHDw4EFCCGTajMeaJBKJxHbEI9R4vHcM6oqBq6iVYqm3yupgnbJW7NzRZqo7zdyBOb709FM88eRjdKczbBYQamo3pFu10PmQYHuUXMHTQxlD0XEEVSGhzaxr4ZzDS42yGSiDGE0IcSwKSu6p59w9F0sBqAO084zh6ir1ygo/fvG7/PDFF7ly9hy9lWVm2vPM7trJE629cHweYxQ1Dq89A+3xbaBSqKa4zDX+SghYMnQAqeJAv/GHBmKobwuiNp/AfBJCiZ+ToGL3W6gDw16fA7vm6Zp8I+9vTJwnmfaxROJjwbhMo7Gw2eRP1NyGZngtqjkRxWcZzboSwKk2SvREmYgel4fEIbcViIvdYOMRJbE7TEQQUWA6iEQTZlRAa4XWgnM1QTxZluGkR0BTBovYNrUYKgel8ywvr3Jt6QrOXCf4FnlmOfUQPP2pvRw+fJh9+6aYn5vBZDtAWojkCAZRfbSqQDxKLC0KaC2Bn0J7S0sPcCrjxvmK2dbDZLTRxSoDn0MOMQzh409zfNTb4Bh5z8VSZizv/uwt/svf/89Zu3GdfTt38PCBw2hXcnD/Aez+g1gRQu0IVQ+jIFMGLQEvgg3Rm0HLhvDZ6n6d0mWJe4FWiv5gwNzsLD/4wQ947JHT93qVEonEXWRkSCyK922SVm6muTfRJTT5OkKu+5scuMeTKUafEwxBYhmJap5tt9tUdUVV1QgelzmCBLQWrNVooxDxeBPwoWK5XMfqGRauXuTq0nWu9wJOYHpH4MSpFp/90iN84pEvcODgbjJraRU5CqGVZbEWsyzx3qPNChCaSRmBMIpGqLjGYVzyPfoLNMELly5fZv++z2KMpQp+208quOdiyTvH3rl5jh06zLvDIXVZU7qauakuvV6PTlbg6wHKe4osjhQR77CoqOKVbyza46Yeu4vCht3DPfnLEg86PgTa7TYXLlzg5MmT0XIiWQMkEh9b/BYnmVvNZDM4xpWw49DT5qt5PVHbcasyD7EFQZsmchTFifMlyoAUCh8UPdPHGE1dD1m+fp2V1VV6Pc9az1MUnhMnupz6xDyPPfcs+w7uZHrakrVqZna0yAvwoUIRMDisAe88rnQoM4V4E02ai4Igq7EcRaSRRhIdvSXEsSebRsHHP0ZpTVG0KMsKYw3Km21/or7nYkkQds3N8l/9s/+a4VqPV17+AX/8h1/nhz99nW6nw9yOHezKDXmeMQygvJDrDJHoCqpEYQg3pctGIdAxKbKU+IjRSrO2tsbi4iJzc3NJKCUSDwCbBpqPPIkmX1frbJJRqvEkmhRIWGgmT0Q9JRsz3ACfBbwSQnD44BBxDAc91vurrK97hlUgtPtU9YCdczs59dAJPnvgSQ4enObwkQPMzHQoCksZVrEIEmoKq9HY2IXuA1o0SgwWg9SCFkcn04SwhkhAKcH76JVEDF80wbIYZWrGsrIx+kSNhaE0WceiKHB1QJvtHlfaDmJJQd9V5O2cwmg++7ee57kvfZFrV67w0ve+x7e//W1eeuUVZtpTHN5/iNxYOlmLUA5pW424Mrpr1zVZliHNeBOldVTcjcunC9FpO5G4W4yaEowx0ZNEawaDAadPnx4/ToIpkfj4YtyGGz8h+qzpJlGmiBGVUtfRgHZUsKg2xoOMao5cyFFGIwhOAqJjtKb2jpWVFVb7A0pXs9YfYNSAvXtn2Ld/P8cfPca+fbvZv38vnV053W6HzlQLwSFSIzi09iizQlmVmKICH8i1gkpQWArbpqyEIp+KPobBISJ4CeAd2sYaKFRAJODMbrwzGAxKPFZroAb8hpn0SOU1NilKKRauXOFzn9gfj412+5+b77lYAoVYKINHWYUSjRdo757nK3/vN/i13/4twkqff/2//Gu+/cILlEs92lnO4b27IdMY6xlUfTqtNqVz2KYV24dAEEEr4qTk5GWTuMuMRpWMut/KsoxTs9O+l0g8EMQ5ojEepJRCGxNF0yjPISCmE2eiCXF4u1bUtYuPtcYFx4A+g17JYFhR+UB/eJ3+sMRMddmzayeHDnQ5dXKexz/1OPv27SbLM0KoMBaqaog2CqNLoAQZgPJjgQMegqdtheDaGAlY8WiE3GaxxkhZqtphjCJQxkYVNKIynIBSObULDIcVlwY1rqqRcshw5TpPPHaC3Fq0+LgdmqDFZDRNKc1wUJLnBUppvA/YbV61tA3EkowLjOIupvHiyVstBq6GumbXrl187Xd/l9/53X/M2soq3/rmn/Ev/tk/Zd90hz07Ohw6MEunmGGwNsSGQGZsLJ9XmhCTqdGrIV3VJz4CRnYByyvL7JydBaJdRZr7lkh8vNGqcbMWaWaVCpj4nEeQEKjCVIw+ZdAr+/R6faqqYmV1hZWV64RM4doFh/cVPP7MI5x6+AR79+5mdn6Wosio6iG57QMDAPJ8iEiP4B21q7G5RhuNdsNmrZqcF9LkxcIoP4au51GqxkiJUlUstvaeARU6bxFyRVk7qjoQfEF/aFm41ufVH/+Uy4vrzM/txx7cyYljxzl2ZJaffecbPCI5hgpFjZKAEU9s+p9MN6pGHBq8j2Xh271U5p6LJQ0UTThyJGVMVtAfVvgQWyxLMyDrWNbX+hQzBV/5ja/wL//Vf8N/9l/8J7z60rf4+h+8QBgoTh09yJ7ZOQIBqxUWjQ5ACNu9dizxMcAYQ1VVWGtZXV1FK81Up0NVVY3Rap3EUiLxMWYoHmU0GI2TgCOO5lod9Fgb9BlWJWfPvhdrfQQ6HZibm+bZz3+Wz33uHzA/P0u702J5+C5FUZBZjdaC+BrnFxAJdDs5Siq8L3HOUQ6EdrsNyqNzjVKC84OJyQCbbJU3r7B2gCeoeA5eq2HNKVZdwdUb65y9dJnXz7zNm2fe4VOf/lW+/Hd+i0PPPMKO0xr0FN2ZOYadijDs0/JDXPsVpNiJlxKLxgQBPG7LdlJa0e/36XanUUqR5wXU2/ssfc/FkglQBIBAQBM0+KFnOiuoXNzEwQ1BG1othfcVnbbm9CePMTUT+FtfeZovfOEUNxb2cOaNM/zxH34dguHU4QPsnJqmbXMI0ij+e/qnJj7mjOqVvPcMh0P2HzgwHt1T13WTy08kEh9X1lzJ6mqP6ytLrPT69F0gKM/+owd45JOPcfT4cf7h7uvs2TNPlitarZy8UAQp0WYJ0Uv0xdPR0kSoXRw3YkBLhc10Y2abgbIoI2htwDtUCCgUIXiMMjg1mg4wGm7b3I4eA9J6GwV4yZHQYcgu/o8//TaPPPVldPsERx//Kseenue3u1MErQhWcyPLkI4mGMV6GFL7NpmyCJbSdFmrNbnNmk8OaDxui2BzLtDr9ZmfnycYS1D1Rqpym3LPxZLXiv5NjlOCD/VYBGspEO9BKYwpqF3gqae+QL/n6c70yLrXaT3U59DRGf7uV/8Jr/z0bf7mJ+f57uuvAS327NjFnu5e9g+jUaAxBlGBuhrQaVmCL5EQgCkCOYxaH0cmYhCL2ZhoWJgYiaLkJr2eeADIfNyfvI7+KkEpDIrr15fIpzoo3VxZuUDGlp5i4u8mEg8yuY+noNAYNMZjbBibM/7/7L3Zr+XXdef3WXv4/c5w57q35irWwFmkKYqDRFmD1bbktrvttNvOYAexEwQJDPRDEKCBPOep8xLkXwiSoBPkIXCnbVh2uy3LsWXNEimxKVKiJM7FGu90ht9vDysP+3fOPZekBkgluWjeBZw6w72n7m/ce+21vkP5dKZLtCDgOBcP1k7kcUZSzyUd0IwhH2gVSV2IPjFijEHEoAreFWuttm2x6hGjIEImUfV7hNgWgDVKVGGCI6VE0JYmTNkb77CzNybmQFVb7OoSd108xYfP3sO5k5azpwecOrWGqQ0TbUmuZT14suygmA524shiyCpoMiiWLIaeCbgEQT1N7OF7A2KYYOMUtZYsxch0rsZkLKl7Lg4Ti0I679zmcs1xxnZApRP6aczUel7JZ3n04d/GqqWSQK6UqErOBWKgIUIoIPaetfg8IUoPVYNvtzktjkG6yq5fYmz6rLQTkoC32xhNtHlINKtMDKR+S4ojqtAjMH37Bt5B8feeLP1EIYbpdEJKfZwru2BtVVyOQ+B9D1zinvdd4p+FD/PyS2/wradf4XvfeoXv7kw5tXmMtZUValtRu1V2R1N6dhUrhkQAEzgwMymxaKz7NoOKo0TpPRsHirzlWbLSxkBoW06eOY454IIcxVEcxTtEaxdVrGfw1cURVTHsvf2LC8rDRvNc27GIE1tEPWCQrpoylrawpV1FSKnLG5RJ02CtxfZ6tGlAExsqX2GcYbcZs7c/YWe8y7iZMp3sEXXE5uYaJ0+f4/Tx05w8eYGzF86yvDxkeXmJwUZFilMMCScJTS3eGWKcUlEhGFpdhS6JExSr4LToEx0oeKeuowLOeNQ6puMxNGOOrw3Ymzbgfvrpe5akzs6AcxXnz18sCWPOWG9oY1O2VWzBWhkzgzx1ZBbBip1jNauqgraTTuAHQJHUkHOH5eySWO5wm8x3UbK0MPEonDx5kp2da5w/XkE25GRIbYMlUVtLJrGxVLF67xYffPAM41sjPvudm/zNZ5/j5VdfYMn1ONZf58TqaSI1bcyFEsm0u/HKDWizmauDix7YocxUwefil0fxngvlcHXIGMPVq1c5feo0MSW8sUeXxlEcxQ+JaBfQLFosq0Rn1lUAimW88I23izke5E0G1AIOxYNaEg4waN8yCk1pUXmDMRBjZNqOmY6LwfWYzLQNTJtdRmMF7zm2sczp+4bcdeFe7r3nHJcvrZUFei5MMSWgKZG1wfuMhl2csYitEHGId0wnDR7HQATayKh0qLCqCBFLwnQP6VhyjfSp/TIxBkJyjFvo9VZYGgzZ3X6TamlAe1sIS7kcRjXF9DspGxsbZE2Qc4etmhFTOoafmbXy6EhTxaQ+50SM5XgcLissejpJd36E5eX1InQZAz3v3oZrutPiXZIsLeSn3U3ygQ88wV/8yf9OvLiFMxCmSq9y9K3ShgkrgyHb+3tojoj1GLvNE4+d4bFHTpAb4crL1/mTf/NXfOG5V+j3e5w+dZ7VqsJT1FMFg9WuJIrB5oLmFxkBB9WmWamYhSrDW813j+IfZmQ5bGswHo+pvGfY79NMphzJeh3FUfzwsLMJv7uRzIIDiFB0hjD1wRd0xqo6uLkSoFIIQnluNxLJZFQCWSCYfZILhBTZ29nl1vYN9vamqFYMl/oMh473/+ISDzzwECdOHqPqe4ZLNaoZY8tfEQXLiJwjYqCNLZW35NhQZBk9OYzwVR+MZxobYm4w1uCMoO0Er4o3i5UyISyoW88ra+4s49iQBW7sN+w2ju1Xr3Dje8/zG7/8QSbtPtb/9Eux2eK/VMkNTUhkLTpIGCHEBld3+KMOAxVDxNoDSRRrLDEW6YEcI5PJhMqXvTHkbj6cjZIl0RJ1CAOMsagWdfA7PRu5wzdvMRYLepljG5vESOmjiuB9Tc4jpqkh4Zi2GdffYDQesRcjS2sb2LANFnKlbN0/5O5L/xSpV/ni157jj//0b/jKs4GLx5Y4f/Y8FsegHhaxLfVFw8lYUi4GhDPWUzEpPLhojxKl905Mmin9pSGSM847nnvuOX7h4YdJoVwrOaZuFXYUR3EUsyhGr2WgdLlr13QrCxEhhYQgeF9aNY1Zpqp6jEajIuaoSuVrcs6klBjngHrwlSGmhmncZxx22J9ss7u/xxtvAhmOH4fVNbj//kv85x/7j7l06TyQumklY802c5d1ycAYZIZ7UjKWjGBNl9RVDqPgfK+oVgM9s05OQmxKpdm7sk9VzxNNw6QJmOBJ4ojiCVKRXZ9ka8YBrt7c5eb0tqDmAAAgAElEQVTOHm+8/k2e/eY32BmNuO/hx/nkP/mPOHPmMv/qf/o/+dQ//mUsLUX48acMyYUJlwt+qq57KOArT2wb+nWfyEwOpbTdZjIoMz25GFqqwTqj3RHOWYaDGuJCe1UyBxXBklYqFtVACJl+v0dsAnd6i+bdkSyp4TBIzTBtpuzs3MS5U1jjKcS5TJJMEMf//W8+S7W8xS/98ifZn9yizUoVrmNRet6QtaVfG3aaKzz5wcs88vgl9l7PvPnSNn/1mb/lhe9sc/qY58yJ8/T8Er5fMQ1jvHdEAdevyVkJbYszC3JaixXHo/gHHUsrKzRtQ8yJN69d5fz58zhrCW1DZR0Yy5FoxVEcRQlVnatbzyU0QqlgpJyJKeArj3ohaybRkCQzjdDQYmpLyC2aEzE3xBQY7e/z2s3r3ByNmYSEkHB15iMfu8jH3v9Rto4v0+9ZhnWPfq/HYKlPzqmwzGT3EFDcxP68pVfwQxnRA+MsFSXag/aS6EFLcHaXJ3qgGaMRNJFzJmTlVkhgBwS3hG02SWL5Dy++zKc/85dIf4WtM5c4fu4Sa8fvwx/r8cBdyqOf+E0UQ2s8U2sh7rO0DpOmZcW9nTDyE50TFoH0ws2b2ywtX+jIVJa2nYLzpJSKHlLOxdYE6YDyUmQLjOB6FePRfvmdeYVQ5/is2ZEFy+uvX+H0qQudpErEOUcs8PQ7Nt4dydI8ZlLp5d3e3j6aIeaIoSxRskArFd98ccQf/vf/gs9940Wm01uc2Oxx9/EtlirI0lJJQwojVno1bTvGq7C1NeT4sTP8wmO/x9UrN3jhhdf4/N9+ketvwuZ6n7W1ZdbcFpozsW0xCL5yB5pflBXHEcvpvRFN2xQ7nW6ltbq6SkoZKwYjhpzTUeJ8FEfRxSxBWqwsZdsrtlROMH3HJLUH1h6xpU0tTbzFZHfMZBrYHxuMNNS9hrrvOHX6FJ/86EMcP3WMEyc22dxcpepZrMmIjYQ4xTmDaFcJ0TFWFGtnC++DjEOpivuIAmrn3m7drINKwsp0/g1ZaJ3NPgtGSqNJEkYDZCW24FdP8kd//kVGqYe3eyyvbLC0fhf/yR/+Ev2VdQKOiKObybB2p7hQGEvIAmRMbBjtg6dF9DYlFjNV764IsbO7hz9WM55MqL3QhqbYtXTJk3PFA04WRZ5zpG2mDK3FGkNOsTsy+aAfNIccFwmD3Z19NjZOkFLCmGpW3Luj412SLM2O9OxmKyC4GBMgpR0WS5acRIhSc9d995LqM3ziNz7O7v5NXn7pmzxz9WWuvvQ8F45VPHr5JGt1RZruU9vizxNklyAJEcfxc33WT1zgg794Lzeu7/Pss9/ly19+hmeee5mtjVUunDtPZSy5U3JXFvrtR/GeiNkAubu7y8rqKiklVKESU0COR1XGoziKeSw6KMyqEhO1iHW0acr2zq1OvHHCznhEZsrSiuPy+RPc9+BFtrb6nDl7gsGw4tjmKnXtEKM4EyGHgi+SneLWkBVapY9Am0g24hdU9EXMvI00u0mT2y/bpoJki1HbVY1mrLqMzQs4RZEDwYIZpNYmrLY4GgwBVNjcOM33bsFg6xEe/cAnmdQtOWbEOtRaRmRynnbDhcEaQ0qmkzAQshiEhOQpl84aemaKaEBvIyhS54lfUdZOmsl6ALMvwO7ChsvpcMLrjcG4HqMb1/HOklMCuyhbsPh8YKRbDHe7Y5/u/IXluyJZmlOz0UJZFHDeE3IsBrkxkSUCrhx8gdW1NZpk2G0cqXeMi488yXT0fh7/WOD5r36WT3/lac6sDTizVnPheB8Je5g64VwGjcS0h/M1MUWOnaj5yNb7+Eefeoybr8FffuavePbZ59FgWFs+xtpSj0E9xGMxWXC5bKdqpytgpPAFckKkGyjSAgZLAF0UzSy/f/COd3x9FD+fmN/uXRuhfKZop0I7now5trWJZMWkMohoLiq1R3EUty1m1FtZ6PssvqZM7GUS1YWW0kEIkCQvfN5Nk9Jd391nOgP5AjnrQYKheY4bUqTz9UpzoK5gQIp1bDBpTvHPORJzJMXAtJnQtIGmyeyFQEw7mIFhZaXPqQsbPHbuApfvu8j5i+dYX19F2huoZCIB4wxKIscG5wKqgRQDTgRrCnNZ1JQJu2uTWWMwJpLaRN/3aNoI1nY4qcLSMAjRTbrDacAYtGOIzSQIZCF56I5SR/U/SFpUMjrTi+rYeqP9Mb16nXowJFfrNP4G4hRUibSEtsEKeGdBMzFmNA8RKS2L2g+IIeKM4/FH70VTgzhZPO0/cah6bA4YhCAW9TXGGJb7NZARqcnZkGKmzQ2qincVi204tX1yity68jInjq1Q1TUp+u66TCQBVBH1KJEsLZM2YP0KxjlibJHsjqQDbkdEkzCqBQxIkS6zPc/1/W2iZpYwjHyDbZdxOeJlitVtjI4Ra4hOGaU9KnecsZly8alf58xjv850d8zV73+d11/4LB99aIMcQTqRNAeQwYuCtCXpyVNOn7P83u9/iJ3RY7z6xjbPPvt9/u5vv8X+TsvFcxdZX17leAO+rskoamBvuo+vHaYWYo4QAzULDI+O3XEwVBlU2vlPD9ghR8nS30fM5qjS2++SIYEkMJpO2NjcRNJsbSazivYRWukobmuU66kkQmV6LpOpLPw04sm48nnHzBXNhxKn1hdz03kTSRVNReens9REjaENDWTBeU+MhdhiAM25aBVVFSkmer0+k0lLXQ2IMRPbAlXZ8ZHd0S5X3nyN8XgH78FVNcsrFe976DJPPPEYpzYTa2vLDIY1zisxtagGkAjyBrRvYOMSyQbUJmJ2oB6nPWw7xZGJsoxqhWZFu/1SbVGTEJeIEjFhjyW3xGR3j4314+w2LQ2FHGQBmwUfhz/42AsLi9nDYRYXtgrgSViUwhCLbUt/2KJ5jKmn+MmCVrVa+mapJKZdZ80JiHOITFHJJE3Y7HF2hZgdUtWk1C7yin7iUB3S1z0gMXJb7GnN2so6PgVGocU4g8lCzkKKBYNVVzMwfnlshz7L+Rbjqy9yatXS5Iw1AwTFkph6g0mK1WWCuYIa4bVrN7j/kSdoYkQk4WSI0vz0O/QzjHdFsvS2UME6SzMNxBgR99aUVNnYWGc8GTPUUs2RbPDWYoylaUaoepxz3HvffXz1239GSLmoeP+I7DbmxLRp6PeXuXThDGdOn+W3fvM32L4x4k//3z/jK1/8Gt9Vy9lTZ9hc36RX9YljxWWHjRU2FxAipqjOls1VkIRZWKHkd2jhHPGq/n5DjEFzRlWxznFr+xbOOQZ1r6y28x3edD+Kd3cInYfXrNpu4C1SJULbMaUoCyyZF9tnH+E7vMtMz0iwGFOXSoyCRiFVFlt3bLO2pd9fIqRETLFUE5zH1BXTvM/rV17COcOb33udN29OCcBGH05eXuXC3ef5p//sUzz08IOcPn2C8WSXEKbsj/YYDHrUEjC2YHwOgCuLLRvIpuBqHAGrCTRh1Xbga4fRKSpTLAbb7ajzgjoh5FIB2cs1tl4i9fvsJCEY28kLhNI6apXbUdowHIbeiIBzjleuXkNZZjyeguvkametLGuQBdasqpJCBkkgmUTCuR6pSbQhkHIsi/jbFjMCFbz66qvcf9djTMZT8JYUE4Kd45Vm1aSybwXLZJJijVDXFe2kfccFvTGGHDJiBWMduzv71FU9x3aq3vlj57syWRJj2Nvbpd8fghY10cJMmGH6lbvvvsS3rrzBibuFHCNVz6Ntmnt1qXp8PYDJhOu3djH2PFl/NHepaWNXOhwj1jHoe2J4nbX1it//g1/hd/75h3j21REvfOv7/PVffIEeNQ9euIu+ETSCzRXWC1PZO+gHdyquZj6IzdaOciR+eYdEaa1lxBi89yTNTCcTTp84WSaPnN8mG3FUWTqK2x1vr264rs0BIFjGXbJkFqohZoFnZPA5lnqUOkBQFRIWIxXZCCkq+x1DCeuIXpgI7Ix2uXLlCjcnI1JsGafEYJD50FOP8oHH3s/m8RrjJvQHjtXVIV4CxihVVSFyg939K4ASU2A4LIBhoSamsnVKZ1sySwS0GHZkGzC0OA3YnDFqyHgSnkyFMMZKQDClApIB6ZHFk21FkxJ67ALXpkKTpvztX/0lSz3l4x95BGcyWWfq0f3bdZa6f4WoiqsqPv+lz3HpF38XYx1q4iFWYNu2RcF6HoKRqiQSUpLZEAI0Lesry6QQqCtXFtQ/9aaahXnFYK1lOmmp+kK/PyCliO3SBBFBVWnb9lDCZJxAyoxGe2wOqo5heLBxomaeDAmWFDN13WM8nmKMw3kht9zx8e5Jlma0BC0nbNBfYm1tA+1k0w9+pTRLvBesKJojrrI0ISA5Y22XuaNoSPQwxKzEnLFG0B9xAYp1WGuwEsk6RfMYK2WVhjh6Q7j3oQ3ueWCDT/3qw7zwze/z9Jdf4tmXnoHQ48TmCZbMEF91rAmlE78sqd4MFze7fo/EL++MEBFSZ5MgIuzs7LCxvFoMI+dgx6Ns9ih+diGAy4c1a3SGK5o1gbUC7PxSVEwRT+UgcUKKyOCBqKqi0hDSiMm0ZdxMuTW9xe4ooKlleVkYLG+wvrbEh3/hEU6eOsbps1usby2ztrZCG0a4KpHypCQDtOS8j8sBby0pjgrWxXtSyvSrjkmVM0kSSVNJzFQKMPvQ6Kck00I2uOyxGpipTkd6JPqoqRFTMEoxKyEJL1+5yRs3rjOKjr1Jy7R/i5Wl42jIvP+jv8s3vvBp2tSj74TUTjBS3Za21kFod87KuGFdXVJB54o6tjKvUospHY/FM23EI2SsRBIWp6Wy8/hjjzHsteTY3r7hRg0zCQXva5xzVFVFaAPGFiuSdwLnzxKm2E5wHp5/7jX+0e88jMariOmqbPOKQJ6PkSFkbt3Y5cSJ06hCaFu8DO50Mty7JFmS0lefoXYES0wtaFkFmV6FmbdAMoZIbCdYO8RbR5sSvvLYbDrLEphhhGJWkgpqKmII/EgNQQNJIxC6XnXGOEPOyqht6feH+PZ6GRiG8OgTp3n8qft5880dXn75Bl/+6nf54jefYd2tcuLYCieOHSe0iUxnq2IsZCGEfXzlyTnjnCPFeKhUe5Qo/fxjcSU4Ho/ZPHMWVLtzcWC7sKjqfRRH8dPEIuvIiFBrMXLNUkbCuZm85kLnpkcWizGGpJGQYmFVScZ6R0IJNrOzd4vdvV32mwn7k11G04aqB5fuPse5ey/x6IkTXLh4huXlIYNhzerqMhDnVQPRhOcm6E16DsjdZJKglGksiEMzxSNRpGBCKWaxZecM2D2sNagWZrO8A8NrGltMXkLNEg0J4yN7baYeHufV1/f59ivXeeHFK3jfYlyP9Y3juOEx3txf4gMf/gSPnrlEZIK6dYxa6nCL9ktfwboVNN3EaI/EACeT23DGcucJOQshRAWxJLWEXGQMZonGYuKxmJAoHpFY2qhJ8GJIbaCuKtApt2uEWVzjaRZef/117nrUdS1cQ4gRk+VQJcm9xZPOeQGJCIEUGpyTOca2gOfLmxQVcdCvl7h5c49jG1uoasdmP2LD/WxCoG0jzlWkBEYszNymyQiJwbDH5NURITT4wYAmwYEA2SwMKpYslqDgfuylRTEPRA2Co43g6iHW1+xHYc3u0bYNWVvwlkDLsdN9Vk+d477HzpPHn+Bbn3+eL3/peb70zWdYXfKcOn6ayvYgGZzx9FeGtG1DiBGfQcm4BVTTQdJ3FD+vMKZgC65cucKZc2exd/pS6Cje1TFjXy7iRGILztdYoyUZIpFIiC3Gp5gBTQi0kwbINGlaMELNhNH+NgBNPeTE5pATl/s8evYc5y+c5OLlMxw7vsy02UOJDLx0iVpCTCLn68zxRFIgAy5HmLXz1B88Y0ANi4TfwziCxYRoYQrSd6awVL0lXn45srMf2Jk0vLH9EtlkXnntq2xuXOT4ubv56G/9aqcqrQQFtUvcePEN8so97LotarlGwxKqpQ2WTB/JpcGkGZKpgNuRLC2ECCpCVqGNHRXfeAR/IMoJZNV5cjJT/G+b4q/mTCblItK5urKCXi0sRyNymyQcD9vH7O3OVNIhxPS25EhESktw8X9wfVJoEXp470gh4U0my2y+KrQsay0hKlJZNGthTqoh5TTHmt3J8S5Jlg7PSqrKcLjMpUt3M9qfkJb9QtWlVHs0taQoeO+YvoOGw7wsLQaxjpgU9+OktpLLhd3RSlUqXLXEjVuBafYYv8Sgb0lmijMNmKYozjZ79GyPWg3JKR/8+F089uHzpGj4+tee48/++Bkm4xEnTmyyurJCm5bxlQfrCSlTVxUaur6vlspSehdcYP9QYtaG007u3zmHWYAZHAmRHsXtjjk1W5UYY9GiqQeEXJhQrmcYhykhNzRtSxMCN7dvsH1zTNNY6l5NVVV8+Kl1HnviSc6dOY5zhv7aSqeX0wIJY4qBvYl7VHkybxvFGDFSMJ/WHPZjg5lJLeVz6X4uBxX+Q7WP+f2hczmB8vYHTUFz4AFNA1/+xiucvPtXWbrvEveuBHqDzOWbDSYOEeeYmsxkvI+1huHqMqOpMiWQvJIsKBMiQ5IINQmkxTLGMyIB2fzsbFyruub6zW3uX11FjcWJ7exD8jwhnr2fabU5v4YzBjERrx6fDRoUbw0pdBU+e7u59iVZq6serVLYj7bgkRa3N6XDaVo2ARGlqm6imjBd22O2oJ8/S5FhyAmMqTCmOpCi03xUWbr9UQ64amZlZYW2fRORqvykkzWalYpzjLiOpWRsd4/O+1cGzYIaQcUSU0Z+rKOxIGSmDqjZnxiu3GjYOnUX//bTf825tYb77jvH+dOrOEbEyS61KquVIzWZ3cku5pihiVOSsfzSJx/hwx9/jGZi+NvPfZU//dP/j9EN2NxY44F776cSw2Q0pidujmu6w6+rf3Ax80S68uabnDlzptOkOSBtHym3H8XtjhjjvLKkqmRVrox2GU1H7OzdYm98i6u7ytoxOHNuhYt3X+JDl9/HPZdOc9f5M1ibiGFESnt4F7FmREwNld3FWodRx2Tcoi14BnhTU6unaRRb1Vipy8SYKqy1h6pDWZTWKiX5yRyAelN5SMbM57/OAI7Zg3lSZeIaB2NqPpxIdWFNj97SSU5cfJLx8nF25RrXJ1fp95ao4hB0xK3t11hZGTIe7dHDEWmxboKxY3w1QdtdxA4K7DVPUBlhzACjI7IYkNtDWy/knMMD9LQJfO7zr/Jr/+0q26pMmgZjCphauoXXYhsuZ+Vzn/s8KyuO9z14Dzkpoc18//nn+dC5Hq7Tu7pt5iAzc2LpvFYVxAjGWqbtBA3F43L2sG9J0sY5Aom6ckV6ohsZlYPTKVIqn8YZJm2k1+tjbKkwOW/RdJQs3ZYwucJq6YkWl2QhqiVLTbCG4AJVzOw7ixhPLydWrJDbfcZpH61XyK0h+QlVWMJpRP2E6BxWV2lG0JeMKUqCP3RbbBZUfXFN1oQwpicNqrv4rU1+/b/5lzTTPUZ7N/lf/p//iyU75p9/6inWBpEbYQfDlGptSJMUaRtOL6/Q7O2RpYdxlo9//B4+8uFT7N20vPHGDf6Pf/2XbO8aLtw14PSJC2jr8LmHwbISxwC0ocU4W25SW/rLWYu0eOzosEYPHjOl/5Lxz5gbzFl3uauGz4aw96JkQZUgkKFyhJxwvYorr79Bf2kAKTOw1R3vZfQPOebXKQfK+bLwDIAUMHC5gi2o7VpF3WsMk15xgC+6Q50EYadNhJSWR2P6nYKzIGowqaPbI6WVIAlkMk+orXVkVTQVPR1jhJCmGGcQa8laGFtiDCEVELYgTHqxk6VQtnducuvWNa7fmDJuUkcuyHz4g2s89YmHuHT3Y/QHwtLQU/mKynis8WBSEUZMb6IRKnFgeiV/iQaPkpItV66AWMV5Q8iZaQxFZmXgMdN9jBtgTEWQhmynQC6sY/WAdOxdPTgh5WzMn22uZoCq"
               +
              "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"
               +
              "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",
          fileName="modelica://SpawnRefSmallOfficeBuilding/../../../../../../../Pictures/Screenshot from 2021-05-02 15-12-15.png")}),
                                                                 Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-300,-440},{420,360}})),
    uses(                            Modelica(version="3.2.3"), Buildings(
          version="9.0.0")),
    experiment(
      StopTime=1604800,
      Interval=60,
      __Dymola_Algorithm="Dassl"),
    version="1",
    conversion(noneFromVersion=""));
end SpawnRefSmallOfficeBuildingvariant1;
