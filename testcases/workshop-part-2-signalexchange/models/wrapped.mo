model wrapped "Wrapped model"
	// Input overwrite
	Modelica.Blocks.Interfaces.RealInput overwrite_u(unit="1", min=0.0, max=7.0);
	Modelica.Blocks.Interfaces.BooleanInput overwrite_activate "Activation for ";
	// Out read
	Modelica.Blocks.Interfaces.RealOutput read_y(unit="1") = mod.read.y "";
	// Original model
	workshop_pt_1_overrides_sensors mod(
		overwrite(uExt(y=overwrite_u),activate(y=overwrite_activate))) "Original model with overwrites";
end wrapped;
