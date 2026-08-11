# my_robot_description


A robot description package for a **Clearpath Dingo dd100** differential base combined with a **Kinova Gen3** 6-DOF manipulator and a **Robotiq 2F-85** gripper — designed for autonomous navigation and object grasping.

## Robot Components

| Component | Description |
|---|---|
| **Mobile Base** | Clearpath Dingo dd100 — differential-drive platform (2 front wheels + rear caster) |
| **Manipulator** | Kinova Gen3 — 6-DOF collaborative robot arm |
| **Gripper** | Robotiq 2F-85 — two-finger adaptive gripper |
| **Depth Camera** | Mast-mounted depth camera at the front, tilted down for ground visibility |
| **LiDAR** | 2D laser scanner at the front of the base |
| **Top Plate** | PACS top plate (surface z ≈ 0.27 m) carrying the arm and mast |

## Architecture

The robot consists of:

- **Dingo dd100 base** (`base_link`) - provides differential-drive mobility
- **PACS Top Plate** - mounted on `default_mount`, surface at z ≈ 0.27 m; the arm mounts on grid point `top_plate_mount_c3`
- **Mast & Camera** - a 0.58 m mast at the front (x = 0.24, y = 0.2 m) with a depth camera facing forward and tilted down for navigation and object detection
- **LiDAR** - front of the base (x = 0.30, z = 0.58 m), scanning above the folded arm for navigation
- **Kinova Gen3 Arm** - mounted on the top plate; workspace extends forward past the robot front edge for grasping
- **Robotiq 2F-85 Gripper** - attached to the arm's tool flange, actuated by `arm_robotiq_85_left_knuckle_joint`

## Dependencies

This package depends on the following ROS 2 packages:

- `clearpath_platform_description` - Dingo dd100 URDF definitions
- `kortex_description` - Kinova Gen3 arm URDF and macros
- `joint_state_publisher_gui` - for visualizing and controlling joint states
- `robot_state_publisher` - for publishing TF transforms
- `rviz2` - for 3D visualization

Some of the required dependencies can be found in the following repositories. Please clone them into your workspace and follow their respective setup instructions:

- `ros2_kortex` - https://github.com/Kinovarobotics/ros2_kortex
- `clearpath_common` - https://github.com/clearpathrobotics/clearpath_common

## Building

Make sure you have all dependencies installed in your ROS 2 workspace, then build with colcon:

```bash
cd ~/your_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select my_robot_description
source install/setup.bash
```

## Launch

To view the robot in RViz with joint control GUI:

```bash
ros2 launch my_robot_description view_my_robot.launch.py
```

This will start:
- `robot_state_publisher` - publishes the robot model and TF frames
- `joint_state_publisher_gui` - interactive GUI to control robot joints
- `rviz2` - 3D visualization of the robot

## File Structure

```
my_robot_description/
├── README.md
├── .gitignore
├── setup.py
├── package.xml
└── my_robot_description/
    ├── launch/
    │   └── view_my_robot.launch.py          # Launch file for visualization
    └── robot_description/
        └── my_robot_description.xacro        # Main robot Xacro description
```
