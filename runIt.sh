#!/bin/bash

rm -f ./output-keywords.txt
rm -f ./input-keywords.txt
python getInputs.py
python main.py
