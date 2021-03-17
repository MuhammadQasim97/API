#!/bin/bash

# driver.sh - The simplest autograder we could think of. It checks
#   that students can write a C program that compiles, and then
#   executes with an exit status of zero.
#   Usage: ./driver.sh

# Compile the code
rm -f $1
(make clean; make)
status=$?
if [ ${status} -ne 0 ]; then
   
    echo "0" > output.txt
    exit
fi

# Run the code

result=$(./hello)
status=$?
read -p "Press Key"
if [ ${status} -eq 0 ]; then
    
    echo "100" > output.txt
else
   
    echo "0" > output.txt
    echo result >output.txt
fi



exit

