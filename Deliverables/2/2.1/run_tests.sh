#!/bin/bash

input4_file='../../../../team21-tests/2/2.1/input1'
input5_file=/../../../../team21-tests/2/2.1/input5
echo $input4_file
python3 testdriver.py < $input5_file
IN_FILES=../../../../team21-tests/2/2.1/input*
for file in $IN_FILES
do
  echo $(basename $file)
done
