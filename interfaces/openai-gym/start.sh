#!/bin/bash
echo "TESTING: starting BOPTEST"
cd ../..
ls
sudo gnome-terminal -x sh -c "make run TESTCASE=spawnrefsmalloffice"
#sudo xterm -hold -e make run TESTCASE=som3
