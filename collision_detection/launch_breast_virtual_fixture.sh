#!/bin/bash
# Start Command Prompt - Open 3D Slicer with ROS2 sourced
gnome-terminal -- /bin/bash -c "cd ~/dev/rosmed_sandbox/Slicer-SuperBuild-Release/Slicer-build; source /opt/ros/galactic/setup.bash; ./Slicer; exec bash"

# Start Command Prompt - launch the ros2 to ros1 bridge
gnome-terminal -- /bin/bash -c "source/opt/ros/galactic/setup.bash; source /opt/ros/noetic/setup.bash; source ~/vf_deepdive/bridge/install/setup.bash;  ros2 run ros1_bridge dynamic_bridge --bridge-all-topics; exec bash"

# Start Command Prompt - launch ros core
gnome-terminal -- /bin/bash -c "source /opt/ros/noetic/setup.bash; roscore; exec bash"

# Start Command Prompt - launch the simulator
gnome-terminal -- /bin/bash -c "source /opt/ros/noetic/setup.bash; cd ~/vf_deepdive/simulation/breast_plugin/scripts/study_gui/; ./drilling_simulator.sh; exec bash"

# Start Command Prompt - control loop
gnome-terminal -- /bin/bash -c "source /opt/ros/noetic/setup.bash; source ~/vf_deepdive/simulation/ambf/build/devel/setup.bash; cd ~/vf_deepdive/simulation/breast_plugin/control_loop/; python3 launch_pyigtl_control_loop.py; exec bash"



