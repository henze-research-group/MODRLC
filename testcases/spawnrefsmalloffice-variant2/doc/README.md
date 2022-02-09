# Spawn DOE Reference Small Office Building

This model is a Spawn replica of the DOE Reference Small Office Building. All systems, setpoints and schedules are replicated from the corresponding EnergyPlus model. ASHRAE Guideline 36 has been implemented where applicable using Modelica Building Library's components. 

# Inputs

Low-level heating coil control:

PSZACcontroller_oveHeaCor_u : Core zone heating coil override, 0 to 1
PSZACcontroller_oveHeaCor_activate :  Activation for Core zone heating coil override, 0 or 1
PSZACcontroller_oveHeaPer1_u : Perimeter zone 1 heating coil override, 0 to 1
PSZACcontroller_oveHeaPer1_activate : Activation for Perimeter zone 1 heating coil override, 0 or 1
PSZACcontroller_oveHeaPer2_u : Perimeter zone 2 heating coil override, 0 to 1
PSZACcontroller_oveHeaPer2_activate :  Activation for Perimeter zone 2 heating coil override, 0 or 1
PSZACcontroller_oveHeaPer3_u : Perimeter zone 3 heating coil override, 0 to 1
PSZACcontroller_oveHeaPer3_activate :  Activation for Perimeter zone 3 heating coil override, 0 or 1
PSZACcontroller_oveHeaPer4_u : Perimeter zone 1 heating coil override, 0 to 1
PSZACcontroller_oveHeaPer4_activate :  Activation for Perimeter zone 1 heating coil override, 0 or 1

Low-level cooling coil control:

PSZACcontroller_oveCooCor_u : Core zone cooling coil override, 0 or 1
PSZACcontroller_oveCooCor_activate :  Activation for Core zone cooling coil override, 0 or 1
PSZACcontroller_oveCooPer1_u : Perimeter zone 1 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer1_activate :  Activation for Perimeter zone 1 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer2_u : Perimeter zone 2 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer2_activate :  Activation for Perimeter zone 2 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer3_u : Perimeter zone 3 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer3_activate :  Activation for Perimeter zone 3 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer4_u : Perimeter zone 4 cooling coil override, 0 or 1
PSZACcontroller_oveCooPer4_activate :  Activation for Perimeter zone 4 cooling coil override, 0 or 1

Low-level damper control:

PSZACcontroller_oveDamCor_u : Core zone damper override, 0 to 0.5 m3/s
PSZACcontroller_oveDamCor_activate :  Activation for Core zone damper override, 0 or 1
PSZACcontroller_oveDamP1_u : Perimeter zone 1 damper override, 0 to 0.5 m3/s
PSZACcontroller_oveDamP1_activate :  Activation for Perimeter zone 1 damper override, 0 or 1
PSZACcontroller_oveDamP2_u : Perimeter zone 2 damper override, 0 to 0.5 m3/s
PSZACcontroller_oveDamP2_activate :  Activation for Perimeter zone 2 damper override, 0 or 1
PSZACcontroller_oveDamP3_u : Perimeter zone 3 damper override, 0 to 0.5 m3/s
PSZACcontroller_oveDamP3_activate :  Activation for Perimeter zone 3 damper override, 0 or 1
PSZACcontroller_oveDamP4_u : Perimeter zone 4 damper override, 0 to 0.5 m3/s
PSZACcontroller_oveDamP4_activate :  Activation for Perimeter zone 4 damper override, 0 or 1

Heating setpoint control:

PSZACcontroller_oveHeaStpCor_u : Core zone heating setpoint override, 250 to 330 K
PSZACcontroller_oveHeaStpCor_activate :  Activation for Core zone heating setpoint override, 0 or 1
PSZACcontroller_oveHeaStpPer1_u : Perimeter zone 1 heating setpoint override, 250 to 330 K
PSZACcontroller_oveHeaStpPer1_activate :  Activation for Perimeter zone 1 heating setpoint override";
PSZACcontroller_oveHeaStpPer2_u : Perimeter zone 2 heating setpoint override, 250 to 330 K
PSZACcontroller_oveHeaStpPer2_activate : Activation for Perimeter zone 2 heating setpoint override, 0 or 1
PSZACcontroller_oveHeaStpPer3_u : Perimeter zone 3 heating setpoint override, 250 to 330 K
PSZACcontroller_oveHeaStpPer3_activate :  Activation for Perimeter zone 3 heating setpoint override, 0 or 1
PSZACcontroller_oveHeaStpPer4_u : Perimeter zone 4 heating setpoint override, 250 to 330 K
PSZACcontroller_oveHeaStpPer4_activate :  Activation for Perimeter zone 4 heating setpoint override, 0 or 1



Cooling setpoint control:
PSZACcontroller_oveCooStpCor_u : Core zone cooling setpoint override, 250 to 330 K
PSZACcontroller_oveCooStpCor_activate :  Activation for Core zone cooling setpoint override, 0 or 1
PSZACcontroller_oveCooStpPer1_u : Perimeter zone 1 cooling setpoint override, 250 to 330 K
PSZACcontroller_oveCooStpPer1_activate :  Activation for Perimeter zone 1 cooling setpoint override, 0 or 1
PSZACcontroller_oveCooStpPer2_u : Perimeter zone 2 cooling setpoint override, 250 to 330 K
PSZACcontroller_oveCooStpPer2_activate :  Activation for Perimeter zone 2 cooling setpoint override, 0 or 1
PSZACcontroller_oveCooStpPer3_u : Perimeter zone 3 cooling setpoint override, 250 to 330 K
PSZACcontroller_oveCooStpPer3_activate :  Activation for Perimeter zone 3 cooling setpoint override, 0 or 1
PSZACcontroller_oveCooStpPer4_u : Perimeter zone 4 cooling setpoint override, 250 to 330 K
PSZACcontroller_oveCooStpPer4_activate :  Activation for Perimeter zone 4 cooling setpoint override, 0 or 1

Demand limit level:

PSZACcontroller_oveDemandLimitLevel_u : Demand limit level, 0 to 5
PSZACcontroller_oveDemandLimitLevel_activate :  Activation for Demand limit level, 0 or 1

# Outputs:

Temperatures:

senTemRoom_y : Core temperature
senTemRoom1_y : Perimeter zone 1 temperature
senTemRoom2_y : Perimeter zone 2 temperature
senTemRoom3_y : Perimeter zone 3 temperature
senTemRoom4_y : Perimeter zone 4 temperature

Total AHU power demand:

senPowCor_y : Core AHU Power demand
senPowPer1_y : Perimeter zone 1 AHU Power demand
senPowPer2_y : Perimeter zone 2 AHU Power demand
senPowPer3_y : Perimeter zone 3 AHU Power demand
senPowPer4_y : Perimeter zone 4 AHU Power demand

Heating coil power demand (note: must apply 0.8 efficiency):

senHeaPow_y : Core Heating Coil Power
senHeaPow1_y : P1 Heating Coil Power
senHeaPow2_y : P2 Heating Coil Power
senHeaPow3_y : P3 Heating Coil Power
senHeaPow4_y : P4 Heating Coil Power

Cooling coil power demand:

senCCPow_y : Core Cooling Coil Power demand
senCCPow1_y : P1 Cooling Coil Power demand
senCCPow2_y : P2 Cooling Coil Power demand
senCCPow3_y : P3 Cooling Coil Power demand
senCCPow4_y : P4 Cooling Coil Power demand

Fan power demand:

senFanPow_y : Core Fan Power demand
senFanPow1_y : P1 Fan Power demand
senFanPow3_y : P3 Fan Power demand
senFanPow2_y : P2 Fan Power demand
senFanPow4_y : P4 Fan Power demand

Other:

senHouDec_y : Hour of the day (decimal)
senDay_y : Day of the week - 1 to 7
senTemOA_y : OA Temperature

