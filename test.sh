#!/bin/sh

export PYTHONPATH=src/main/:src/test/ 
python -m unittest flac2mp3_test flac2mp3_acceptance_test
