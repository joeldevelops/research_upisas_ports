#!/bin/bash
source ~/.bashrc
source ~/suave_ws/install/setup.bash

echo 'Starting a tmux session'
tmux new-session -d -s sauve

# Launch ArduSub sim without GUI
echo 'Launching ArduSub sim without GUI'
tmux send-keys 'sim_vehicle.py -v ArduSub -L RATBeach --console --map false' C-m
sleep 2

# Launch ROS2 simulation
echo 'Launching ROS2 simulation'
tmux new-window
tmux send-keys 'ros2 launch suave simulation.launch.py x:=-17.0 y:=2.0 gui:=false' C-m
sleep 2

# Start ROS2 mission
echo 'Launching ROS2 mission'
tmux new-window
tmux send-keys 'ros2 launch suave_missions mission.launch.py' C-m
sleep 5

# Start ROS2 HTTP server
echo 'Launching ROS2 HTTP server'
python ~/suave_ws/src/suave/suave_externalcontrol/suave_externalcontrol/http_server.py
