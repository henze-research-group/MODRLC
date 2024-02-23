model wrapped "Wrapped model"
	// Input overwrite
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaPer1_u(unit="1", min=0.0, max=1.0) "Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaPer1_activate "Activation for Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaStpPer2_u(unit="K", min=250.0, max=330.0) "Perimeter zone 2 heating setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaStpPer2_activate "Activation for Perimeter zone 2 heating setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaStpPer3_u(unit="K", min=250.0, max=330.0) "Perimeter zone 3 heating setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaStpPer3_activate "Activation for Perimeter zone 3 heating setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaStpPer1_u(unit="K", min=250.0, max=330.0) "Perimeter zone 1 heating setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaStpPer1_activate "Activation for Perimeter zone 1 heating setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaPer2_u(unit="1", min=0.0, max=1.0) "Perimeter zone 2 heating coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaPer2_activate "Activation for Perimeter zone 2 heating coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaStpPer4_u(unit="K", min=250.0, max=330.0) "Perimeter zone 4 heating setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaStpPer4_activate "Activation for Perimeter zone 4 heating setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDemandLimitLevel_u(unit="1", min=0.0, max=5.0) "Demand limit level";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDemandLimitLevel_activate "Activation for Demand limit level";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooCor_u(unit="1", min=0.0, max=1.0) "Core zone cooling coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooCor_activate "Activation for Core zone cooling coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaCor_u(unit="1", min=0.0, max=1.0) "Core zone heating coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaCor_activate "Activation for Core zone heating coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDamP1_u(unit="m3/s", min=0.0, max=0.5) "Perimeter zone 1 damper override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDamP1_activate "Activation for Perimeter zone 1 damper override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDamP3_u(unit="m3/s", min=0.0, max=0.5) "Perimeter zone 3 damper override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDamP3_activate "Activation for Perimeter zone 3 damper override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDamP2_u(unit="m3/s", min=0.0, max=0.5) "Perimeter zone 2 damper override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDamP2_activate "Activation for Perimeter zone 2 damper override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDamP4_u(unit="m3/s", min=0.0, max=0.5) "Perimeter zone 4 damper override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDamP4_activate "Activation for Perimeter zone 4 damper override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooStpPer4_u(unit="K", min=250.0, max=330.0) "Perimeter zone 4 cooling setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooStpPer4_activate "Activation for Perimeter zone 4 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooStpPer3_u(unit="K", min=250.0, max=330.0) "Perimeter zone 3 cooling setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooStpPer3_activate "Activation for Perimeter zone 3 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooStpPer2_u(unit="K", min=250.0, max=330.0) "Perimeter zone 2 cooling setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooStpPer2_activate "Activation for Perimeter zone 2 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooStpPer1_u(unit="K", min=250.0, max=330.0) "Perimeter zone 1 cooling setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooStpPer1_activate "Activation for Perimeter zone 1 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooStpCor_u(unit="K", min=250.0, max=330.0) "Core zone cooling setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooStpCor_activate "Activation for Core zone cooling setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaStpCor_u(unit="K", min=250.0, max=330.0) "Core zone heating setpoint override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaStpCor_activate "Activation for Core zone heating setpoint override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveDamCor_u(unit="m3/s", min=0.0, max=0.5) "Core zone damper override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveDamCor_activate "Activation for Core zone damper override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaPer4_u(unit="1", min=0.0, max=1.0) "Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaPer4_activate "Activation for Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooPer4_u(unit="1", min=0.0, max=1.0) "Perimeter zone 4 cooling coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooPer4_activate "Activation for Perimeter zone 4 cooling coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooPer3_u(unit="1", min=0.0, max=1.0) "Perimeter zone 3 cooling coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooPer3_activate "Activation for Perimeter zone 3 cooling coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooPer2_u(unit="1", min=0.0, max=1.0) "Perimeter zone 2 cooling coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooPer2_activate "Activation for Perimeter zone 2 cooling coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveCooPer1_u(unit="1", min=0.0, max=1.0) "Perimeter zone 1 cooling coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveCooPer1_activate "Activation for Perimeter zone 1 cooling coil override";
	Modelica.Blocks.Interfaces.RealInput PSZACcontroller_oveHeaPer3_u(unit="1", min=0.0, max=1.0) "Perimeter zone 3 heating coil override";
	Modelica.Blocks.Interfaces.BooleanInput PSZACcontroller_oveHeaPer3_activate "Activation for Perimeter zone 3 heating coil override";
	// Out read
	Modelica.Blocks.Interfaces.RealOutput senTemRoom4_y(unit="K") = mod.senTemRoom4.y "Perimeter zone 4 temperature";
	Modelica.Blocks.Interfaces.RealOutput senHouDec_y(unit="1") = mod.senHouDec.y "Time";
	Modelica.Blocks.Interfaces.RealOutput senTemRoom1_y(unit="K") = mod.senTemRoom1.y "Perimeter zone 1 temperature";
	Modelica.Blocks.Interfaces.RealOutput senTemRoom2_y(unit="K") = mod.senTemRoom2.y "Perimeter zone 2 temperature";
	Modelica.Blocks.Interfaces.RealOutput senTemRoom3_y(unit="K") = mod.senTemRoom3.y "Perimeter zone 3 temperature";
	Modelica.Blocks.Interfaces.RealOutput senHeaPow_y(unit="W") = mod.senHeaPow.y "Core Heating Coil Power";
	Modelica.Blocks.Interfaces.RealOutput senPowCor_y(unit="W") = mod.senPowCor.y "Core AHU Power demand";
	Modelica.Blocks.Interfaces.RealOutput senHeaPow1_y(unit="W") = mod.senHeaPow1.y "P1 Heating Coil Power";
	Modelica.Blocks.Interfaces.RealOutput senHeaPow2_y(unit="W") = mod.senHeaPow2.y "P2 Heating Coil Power";
	Modelica.Blocks.Interfaces.RealOutput senHeaPow3_y(unit="W") = mod.senHeaPow3.y "P3 Heating Coil Power";
	Modelica.Blocks.Interfaces.RealOutput senHeaPow4_y(unit="W") = mod.senHeaPow4.y "P4 Heating Coil Power";
	Modelica.Blocks.Interfaces.RealOutput senCCPow_y(unit="W") = mod.senCCPow.y "Core Cooling Coil Power demand";
	Modelica.Blocks.Interfaces.RealOutput senPpmPerimeter1_y(unit="ppm") = mod.senPpmPerimeter1.y "P1 CO2 ppm";
	Modelica.Blocks.Interfaces.RealOutput senPpmPerimeter2_y(unit="ppm") = mod.senPpmPerimeter2.y "P2 CO2 ppm";
	Modelica.Blocks.Interfaces.RealOutput senPpmPerimeter3_y(unit="ppm") = mod.senPpmPerimeter3.y "P3 CO2 ppm";
	Modelica.Blocks.Interfaces.RealOutput senPpmPerimeter4_y(unit="ppm") = mod.senPpmPerimeter4.y "P4 CO2 ppm";
	Modelica.Blocks.Interfaces.RealOutput senDay_y(unit="1") = mod.senDay.y "Day of the week - 1 to 7";
	Modelica.Blocks.Interfaces.RealOutput senCCPow3_y(unit="W") = mod.senCCPow3.y "P3 Cooling Coil Power demand";
	Modelica.Blocks.Interfaces.RealOutput senCCPow2_y(unit="W") = mod.senCCPow2.y "P2 Cooling Coil Power demand";
	Modelica.Blocks.Interfaces.RealOutput senCCPow1_y(unit="W") = mod.senCCPow1.y "P1 Cooling Coil Power demand";
	Modelica.Blocks.Interfaces.RealOutput senCCPow4_y(unit="W") = mod.senCCPow4.y "P4 Cooling Coil Power demand";
	Modelica.Blocks.Interfaces.RealOutput senPowPer4_y(unit="W") = mod.senPowPer4.y "Perimeter zone 4 AHU Power demand";
	Modelica.Blocks.Interfaces.RealOutput senPowPer1_y(unit="W") = mod.senPowPer1.y "Perimeter zone 1 AHU Power demand";
	Modelica.Blocks.Interfaces.RealOutput senPowPer3_y(unit="W") = mod.senPowPer3.y "Perimeter zone 3 AHU Power demand";
	Modelica.Blocks.Interfaces.RealOutput senPowPer2_y(unit="W") = mod.senPowPer2.y "Perimeter zone 2 AHU Power demand";
	Modelica.Blocks.Interfaces.RealOutput senFanPow1_y(unit="W") = mod.senFanPow1.y "P1 Fan Power demand";
	Modelica.Blocks.Interfaces.RealOutput senFanPow3_y(unit="W") = mod.senFanPow3.y "P3 Fan Power demand";
	Modelica.Blocks.Interfaces.RealOutput senFanPow2_y(unit="W") = mod.senFanPow2.y "P2 Fan Power demand";
	Modelica.Blocks.Interfaces.RealOutput senFanPow4_y(unit="W") = mod.senFanPow4.y "P4 Fan Power demand";
	Modelica.Blocks.Interfaces.RealOutput senTemRoom_y(unit="K") = mod.senTemRoom.y "Core temperature";
	Modelica.Blocks.Interfaces.RealOutput senFanPow_y(unit="W") = mod.senFanPow.y "Core Fan Power demand";
	Modelica.Blocks.Interfaces.RealOutput senTemOA_y(unit="K") = mod.senTemOA.y "OA Temperature";
	Modelica.Blocks.Interfaces.RealOutput senPpmCore_y(unit="ppm") = mod.senPpmCore.y "Core CO2 ppm";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaPer1_y(unit="1") = mod.PSZACcontroller.oveHeaPer1.y "Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaStpPer2_y(unit="K") = mod.PSZACcontroller.oveHeaStpPer2.y "Perimeter zone 2 heating setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaStpPer3_y(unit="K") = mod.PSZACcontroller.oveHeaStpPer3.y "Perimeter zone 3 heating setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaStpPer1_y(unit="K") = mod.PSZACcontroller.oveHeaStpPer1.y "Perimeter zone 1 heating setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaPer2_y(unit="1") = mod.PSZACcontroller.oveHeaPer2.y "Perimeter zone 2 heating coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaStpPer4_y(unit="K") = mod.PSZACcontroller.oveHeaStpPer4.y "Perimeter zone 4 heating setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDemandLimitLevel_y(unit="1") = mod.PSZACcontroller.oveDemandLimitLevel.y "Demand limit level";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooCor_y(unit="1") = mod.PSZACcontroller.oveCooCor.y "Core zone cooling coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaCor_y(unit="1") = mod.PSZACcontroller.oveHeaCor.y "Core zone heating coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDamP1_y(unit="m3/s") = mod.PSZACcontroller.oveDamP1.y "Perimeter zone 1 damper override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDamP3_y(unit="m3/s") = mod.PSZACcontroller.oveDamP3.y "Perimeter zone 3 damper override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDamP2_y(unit="m3/s") = mod.PSZACcontroller.oveDamP2.y "Perimeter zone 2 damper override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDamP4_y(unit="m3/s") = mod.PSZACcontroller.oveDamP4.y "Perimeter zone 4 damper override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooStpPer4_y(unit="K") = mod.PSZACcontroller.oveCooStpPer4.y "Perimeter zone 4 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooStpPer3_y(unit="K") = mod.PSZACcontroller.oveCooStpPer3.y "Perimeter zone 3 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooStpPer2_y(unit="K") = mod.PSZACcontroller.oveCooStpPer2.y "Perimeter zone 2 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooStpPer1_y(unit="K") = mod.PSZACcontroller.oveCooStpPer1.y "Perimeter zone 1 cooling setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooStpCor_y(unit="K") = mod.PSZACcontroller.oveCooStpCor.y "Core zone cooling setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaStpCor_y(unit="K") = mod.PSZACcontroller.oveHeaStpCor.y "Core zone heating setpoint override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveDamCor_y(unit="m3/s") = mod.PSZACcontroller.oveDamCor.y "Core zone damper override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaPer4_y(unit="1") = mod.PSZACcontroller.oveHeaPer4.y "Perimeter zone 1 heating coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooPer4_y(unit="1") = mod.PSZACcontroller.oveCooPer4.y "Perimeter zone 4 cooling coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooPer3_y(unit="1") = mod.PSZACcontroller.oveCooPer3.y "Perimeter zone 3 cooling coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooPer2_y(unit="1") = mod.PSZACcontroller.oveCooPer2.y "Perimeter zone 2 cooling coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveCooPer1_y(unit="1") = mod.PSZACcontroller.oveCooPer1.y "Perimeter zone 1 cooling coil override";
	Modelica.Blocks.Interfaces.RealOutput PSZACcontroller_oveHeaPer3_y(unit="1") = mod.PSZACcontroller.oveHeaPer3.y "Perimeter zone 3 heating coil override";
	// Original model
	SpawnRefSmallOfficeBuilding mod(
		PSZACcontroller.oveHeaPer1(uExt(y=PSZACcontroller_oveHeaPer1_u),activate(y=PSZACcontroller_oveHeaPer1_activate)),
		PSZACcontroller.oveHeaStpPer2(uExt(y=PSZACcontroller_oveHeaStpPer2_u),activate(y=PSZACcontroller_oveHeaStpPer2_activate)),
		PSZACcontroller.oveHeaStpPer3(uExt(y=PSZACcontroller_oveHeaStpPer3_u),activate(y=PSZACcontroller_oveHeaStpPer3_activate)),
		PSZACcontroller.oveHeaStpPer1(uExt(y=PSZACcontroller_oveHeaStpPer1_u),activate(y=PSZACcontroller_oveHeaStpPer1_activate)),
		PSZACcontroller.oveHeaPer2(uExt(y=PSZACcontroller_oveHeaPer2_u),activate(y=PSZACcontroller_oveHeaPer2_activate)),
		PSZACcontroller.oveHeaStpPer4(uExt(y=PSZACcontroller_oveHeaStpPer4_u),activate(y=PSZACcontroller_oveHeaStpPer4_activate)),
		PSZACcontroller.oveDemandLimitLevel(uExt(y=PSZACcontroller_oveDemandLimitLevel_u),activate(y=PSZACcontroller_oveDemandLimitLevel_activate)),
		PSZACcontroller.oveCooCor(uExt(y=PSZACcontroller_oveCooCor_u),activate(y=PSZACcontroller_oveCooCor_activate)),
		PSZACcontroller.oveHeaCor(uExt(y=PSZACcontroller_oveHeaCor_u),activate(y=PSZACcontroller_oveHeaCor_activate)),
		PSZACcontroller.oveDamP1(uExt(y=PSZACcontroller_oveDamP1_u),activate(y=PSZACcontroller_oveDamP1_activate)),
		PSZACcontroller.oveDamP3(uExt(y=PSZACcontroller_oveDamP3_u),activate(y=PSZACcontroller_oveDamP3_activate)),
		PSZACcontroller.oveDamP2(uExt(y=PSZACcontroller_oveDamP2_u),activate(y=PSZACcontroller_oveDamP2_activate)),
		PSZACcontroller.oveDamP4(uExt(y=PSZACcontroller_oveDamP4_u),activate(y=PSZACcontroller_oveDamP4_activate)),
		PSZACcontroller.oveCooStpPer4(uExt(y=PSZACcontroller_oveCooStpPer4_u),activate(y=PSZACcontroller_oveCooStpPer4_activate)),
		PSZACcontroller.oveCooStpPer3(uExt(y=PSZACcontroller_oveCooStpPer3_u),activate(y=PSZACcontroller_oveCooStpPer3_activate)),
		PSZACcontroller.oveCooStpPer2(uExt(y=PSZACcontroller_oveCooStpPer2_u),activate(y=PSZACcontroller_oveCooStpPer2_activate)),
		PSZACcontroller.oveCooStpPer1(uExt(y=PSZACcontroller_oveCooStpPer1_u),activate(y=PSZACcontroller_oveCooStpPer1_activate)),
		PSZACcontroller.oveCooStpCor(uExt(y=PSZACcontroller_oveCooStpCor_u),activate(y=PSZACcontroller_oveCooStpCor_activate)),
		PSZACcontroller.oveHeaStpCor(uExt(y=PSZACcontroller_oveHeaStpCor_u),activate(y=PSZACcontroller_oveHeaStpCor_activate)),
		PSZACcontroller.oveDamCor(uExt(y=PSZACcontroller_oveDamCor_u),activate(y=PSZACcontroller_oveDamCor_activate)),
		PSZACcontroller.oveHeaPer4(uExt(y=PSZACcontroller_oveHeaPer4_u),activate(y=PSZACcontroller_oveHeaPer4_activate)),
		PSZACcontroller.oveCooPer4(uExt(y=PSZACcontroller_oveCooPer4_u),activate(y=PSZACcontroller_oveCooPer4_activate)),
		PSZACcontroller.oveCooPer3(uExt(y=PSZACcontroller_oveCooPer3_u),activate(y=PSZACcontroller_oveCooPer3_activate)),
		PSZACcontroller.oveCooPer2(uExt(y=PSZACcontroller_oveCooPer2_u),activate(y=PSZACcontroller_oveCooPer2_activate)),
		PSZACcontroller.oveCooPer1(uExt(y=PSZACcontroller_oveCooPer1_u),activate(y=PSZACcontroller_oveCooPer1_activate)),
		PSZACcontroller.oveHeaPer3(uExt(y=PSZACcontroller_oveHeaPer3_u),activate(y=PSZACcontroller_oveHeaPer3_activate))) "Original model with overwrites";
end wrapped;
