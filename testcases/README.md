# Test Cases

This directory contains test cases for the ACTB.  A summary of available test cases is provided in the table below.  For more detail on a particular test case, go to ``/<testcase_dir_name>/docs``.

| Test Case                                                             | Description                                               | Status
|-----------------------------------------------------------------------|-----------------------------------------------------------|---------------|
| ``spawnrefsmalloffice`` | Spawn of EnergyPlus test case based on the U.S. DOE Reference Small Office Building.  5-zone building with 5 constant air volume AHUs based on ASHRAE Baseline System 3.| Ready |
| ``spawnrefmediumoffice``| Spawn of EnergyPlus test case based on the U.S. DOE Reference Medium Office Building. 15-zone building with 3 multi-zone variable air volume AHUs.| In development|

To build and run a testcase:
1. Build the test case by ``$ make build TESTCASE=<testcase_dir_name>`` where <testcase_dir_name> is the name of the test case subdirectory.
For example, build the Spawn Small Office test case by running ``$ make build TESTCASE=spawnrefsmalloffice``
2. Deploy the test case by ``$ make run TESTCASE=<testcase_dir_name>`` where <testcase_dir_name> is the name of the test case subdirectory.
3. Shutdown a test case container by selecting the container terminal window, ``Ctrl+C`` to close port, and ``Ctrl+D`` to exit the Docker container.
4. Remove the test case Docker image by ``$ make remove-image TESTCASE=<testcase_dir_name>``.