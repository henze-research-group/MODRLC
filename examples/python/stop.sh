#!/bin/bash
echo "TESTING: stopping BOPTEST"
cd ../..
make stop TESTCASE=spawnrefsmalloffice
