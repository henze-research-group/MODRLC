#!/bin/bash
echo "TESTING: stopping BOPTEST"
cd ../../
sudo gnome-terminal -x sh -c "make stop TESTCASE=spawnrefsmalloffice"
