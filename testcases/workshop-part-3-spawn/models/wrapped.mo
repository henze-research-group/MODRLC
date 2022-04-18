model wrapped "Wrapped model"
	// Input overwrite
	Modelica.Blocks.Interfaces.RealInput overwrite_u(unit="1", min=0.0, max=1.0);
	Modelica.Blocks.Interfaces.BooleanInput overwrite_activate "Activation for ";
	// Out read
	Modelica.Blocks.Interfaces.RealOutput read_y(unit="K") = mod.read.y "";
	// Original model
	workshoppt3spawn mod(
		overwrite(uExt(y=overwrite_u),activate(y=overwrite_activate))) "Original model with overwrites";
end wrapped;
