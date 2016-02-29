#!/bin/bash

#generate audio file for arg1
echo "speaking $1"
pico2wave -w test.wav "$1"

#play back audio file
mplayer -ao alsa:device=default -really-quiet -noconsolecontrols test.wav

#remove audio file since we dont need it any more
rm test.wav
