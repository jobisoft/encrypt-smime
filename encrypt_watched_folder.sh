#!/bin/bash

# Location of encrypt-smime.py
SCRIPT=/path/to/encrypt-smime.py

# Check command line arguments
if [ "$#" -lt 2 ]; then
    echo "This script needs at least two parameters (watched folder name and name of the new message)"
    exit
fi

# Default location of pub.pem
PEM=$1/../../pub.pem

# User may provide specific location of pub.pem via 3rd parameter
if [ "$#" -eq 3 ]; then
    PEM=$3
fi

# If the PEM file does not exist, do nothing
if [ ! -f $PEM ]; then
    exit
fi

# Incron does support the IN_NO_LOOP symbol, but to be sure, for loop
# prevention we skip files created with prefix "encrypted-".
if [[ "${2:0:10}" != "encrypted-" ]]; then
    ENCFILENAME=$(cat /proc/sys/kernel/random/uuid)
    cat $1/$2 | $SCRIPT $PEM > $1/encrypted-${ENCFILENAME}:2,S
    chown vmail:vmail $1/encrypted-${ENCFILENAME}:2,S
    rm -f $1/$2
fi
