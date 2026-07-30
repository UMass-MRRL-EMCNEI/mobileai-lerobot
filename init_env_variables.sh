#!/bin/bash

# This script initializes global variables for the project

# IP adresses
LF_IP=192.168.1.5
RF_IP=192.168.1.4
LL_IP=192.168.1.3
RL_IP=192.168.1.2

# YAML config files
LF_CONFIG="config_left_follower_clara.yaml"
RF_CONFIG="config_right_follower_clara.yaml"
LL_CONFIG="config_left_leader_clara.yaml"
RL_CONFIG="config_right_leader_clara.yaml"

# Camera settings
CAMERA_CONFIG="{
    cam_high: {type: intelrealsense, serial_number_or_name: "218622275251", width: 640, height: 480, fps: 30},
    cam_left_wrist: {type: intelrealsense, serial_number_or_name: "130322272903", width: 640, height: 480, fps: 30},
    cam_right_wrist: {type: intelrealsense, serial_number_or_name: "218622271135", width: 640, height: 480, fps: 30},
    }"

# Hugging Face user
HF_USER=$(uvx hf auth whoami --format quiet)