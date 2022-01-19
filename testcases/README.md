# Test Cases

This directory contains test cases for the ACTB.  A summary of available test cases is provided in the table below.  For more detail on a particular test case, go to ``/<testcase_dir_name>/docs``.

| Test Case                                                             | Description                                               | Status
|-----------------------------------------------------------------------|-----------------------------------------------------------|---------------|
| ``spawnrefsmalloffice`` | Spawn of EnergyPlus test case based on the U.S. DOE Reference Small Office Building.  5-zone building with 5 constant air volume AHUs based on ASHRAE Baseline System 3.| Ready |
| ``spawnrefmediumoffice``| Spawn of EnergyPlus test case based on the U.S. DOE Reference Medium Office Building. 15-zone building with 3 multi-zone variable air volume AHUs.| In development|

To run a test case, simply run the ACTB Docker container as explained on the main page's ReadMe file using `make run`. This will upload and run all test cases
present in this directory. The specific test case can then be selected using the ACTB client.