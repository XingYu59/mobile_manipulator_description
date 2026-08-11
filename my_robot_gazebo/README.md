# my_robot_gazebo


A Gazebo Fortress (Gazebo Sim 6) simulation package for the **my_robot** mobile manipulator — Dingo dd100 base + Kinova Gen3 arm + Robotiq 2F-85 gripper + mast camera + LiDAR, with MoveIt 2 motion planning integrated.

## What It Provides

- **`sim.launch.py`** - one-shot launch of the full simulation: robot spawn, ros2_control, sensor bridge and (optionally) MoveIt + RViz
- **`gazebo_controllers.yaml`** - single `/controller_manager` covering base, arm and gripper (loaded by the clearpath `libign_ros2_control-system.so` plugin)
- **`bridge.yaml`** - `ros_gz_bridge` config bridging `/clock`, `/scan`, `/imu/data_raw` and mast camera topics (GZ -> ROS)
- **`empty.world`** - empty simulation world

## Controllers

All controllers are managed by a single `controller_manager` (see `config/gazebo_controllers.yaml`):

| Controller | Type | Manages |
|---|---|---|
| `joint_state_broadcaster` | `joint_state_broadcaster/JointStateBroadcaster` | All joints |
| `platform_velocity_controller` | `diff_drive_controller/DiffDriveController` | Dingo dd100 base (front_left/front_right wheels) |
| `joint_trajectory_controller` | `joint_trajectory_controller/JointTrajectoryController` | Gen3 arm (`arm_joint_1..6`) |
| `robotiq_gripper_controller` | `position_controllers/GripperActionController` | Gripper (`arm_robotiq_85_left_knuckle_joint`) |
| `imu_sensor_broadcaster` | `imu_sensor_broadcaster/IMUSensorBroadcaster` | IMU (`imu_0`) |

## Bridged Topics

| ROS Topic | GZ Topic | Type |
|---|---|---|
| `/clock` | `/world/default/clock` | `rosgraph_msgs/msg/Clock` |
| `/scan` | `/front_laser/scan` | `sensor_msgs/msg/LaserScan` |
| `/imu/data_raw` | `/imu/data_raw` | `sensor_msgs/msg/Imu` |
| `/camera/image_raw` | `/mast_camera/image` | `sensor_msgs/msg/Image` |
| `/camera/depth/image_raw` | `/mast_camera/depth_image` | `sensor_msgs/msg/Image` |
| `/camera/camera_info` | `/mast_camera/camera_info` | `sensor_msgs/msg/CameraInfo` |
| `/camera/depth/points` | `/mast_camera/points` | `sensor_msgs/msg/PointCloud2` |

> `/cmd_vel`, `/odom` and `/joint_states` are published directly by ros2_control as
> ROS topics, so they are not bridged. `/clock` must be bridged manually because
> `gz_ros2_control` does not publish it.

## Dependencies

- `my_robot_description` - robot model
- `clearpath_common` - Dingo dd100 URDF and platform controller definitions
- `ros2_kortex`, `ros2_robotiq_gripper` - arm and gripper descriptions
- `gz_ros2_control` / `ros_gz` - Gazebo Fortress ros2_control plugin and bridge
- `my_robot_moveit_config` - MoveIt configuration (for the integrated move_group)
- `moveit_configs_utils` - MoveIt launch utilities

## Launch

Full simulation with MoveIt and RViz:

```bash
ros2 launch my_robot_gazebo sim.launch.py
```

Headless (no GUI, for testing):

```bash
ros2 launch my_robot_gazebo sim.launch.py headless:=true launch_rviz:=false
```

This starts:
- `robot_state_publisher` - publishes the robot model and TF frames
- `ign gazebo` + `ros_gz_sim create` - sim server and robot spawn
- `ros_gz_bridge` (parameter_bridge) - bridges clock / sensors
- `move_group` (MoveIt 2) - motion planning
- `rviz2` - 3D visualization (unless `launch_rviz:=false`)

## File Structure

```
my_robot_gazebo/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── gazebo_controllers.yaml   # Single controller_manager for base + arm + gripper
│   └── bridge.yaml               # ros_gz_bridge config (clock / scan / imu / camera)
├── launch/
│   └── sim.launch.py             # Full simulation launch
└── worlds/
    └── empty.world               # Empty simulation world
```
