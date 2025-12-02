#!/bin/bash
# Simple run script for BeePlan
cd "$(dirname "$0")"
export QT_MAC_WANTS_LAYER=1
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_QPA_PLATFORM=cocoa
python3 main.py

