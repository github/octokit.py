#!/bin/sh

echo "**************************"
echo "Loading test configuration"
echo "**************************"
config_file="test_config.sh"
if [ -e .${config_file} ]
then
  source .${config_file}
  echo Config loaded.
else
  echo You need to configure $config_file and move it to .${config_file}
  exit
fi

echo ""
echo ""
echo "*************************"
echo "Running tests in python 2"
echo "*************************"
python2 ./test.py

echo ""
echo ""
echo "*************************"
echo "Running tests in python 3"
echo "*************************"
python3 ./test.py