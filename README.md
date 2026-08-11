# mobile_manipulator_description


A ROS 2 workspace (monorepo) for a mixed mobile manipulator combining a **Clearpath Dingo dd100** differential base, a **Kinova Gen3** 6-DOF manipulator, and a **Robotiq 2F-85** gripper — with Gazebo Fortress simulation and MoveIt 2 grasping support, designed for autonomous navigation and object grasping.

## Packages

| Package | Purpose |
|---|---|
| `my_robot_description` | Robot model (URDF/Xacro): Dingo dd100 base + Gen3 arm + 2F-85 gripper + mast camera + LiDAR |
| `my_robot_gazebo` | Gazebo Fortress (Gazebo Sim 6) simulation: launch, ros2_control controllers, ros_gz bridge |
| `my_robot_moveit_config` | MoveIt 2 configuration for motion planning and grasping |

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

- **Dingo dd100 base** (`base_link`) - provides differential-drive mobility; `/cmd_vel`, `/odom` and `/joint_states` are published by the platform controller
- **PACS Top Plate** - mounted on `default_mount`, surface at z ≈ 0.27 m; the arm mounts on grid point `top_plate_mount_c3`
- **Mast & Camera** - a 0.58 m mast at the front (x = 0.24, y = 0.2 m) with a depth camera facing forward and tilted down for navigation and object detection
- **LiDAR** - front of the base (x = 0.30, z = 0.58 m), scanning above the folded arm for navigation
- **Kinova Gen3 Arm** - mounted on the top plate; workspace extends forward past the robot front edge for grasping
- **Robotiq 2F-85 Gripper** - attached to the arm's tool flange, actuated by `arm_robotiq_85_left_knuckle_joint`

## Dependencies

The workspace vendors the third-party ROS 2 packages that the three packages depend on. After cloning this repo, import them with `vcs` and apply the local patches:

```bash
cd ~/your_ws
git clone https://github.com/XingYu59/mobile_manipulator_description.git src
cd src
vcs import < deps.repos
./patches/apply_patches.sh
```

Third-party packages (see `deps.repos` for exact URLs and versions):

- `clearpath_common` - Dingo dd100 URDF and platform definitions
- `ros2_kortex` - Kinova Gen3 arm URDF and macros
- `gz_ros2_control` - ros2_control plugin for Gazebo Fortress
- `ros_gz` - Gazebo Fortress bridge and simulation tools
- `ros2_robotiq_gripper`, `picknik_controllers`, `serial`, etc.

> **Patches**: the workspace relies on 4 local fixes to third-party packages
> (kortex xacro variable evaluation, clearpath dd100 IMU and topic remapping).
> They are archived under `patches/` and are **required** for the simulation to
> work — re-apply them with `./patches/apply_patches.sh` after any re-import or
> upgrade of the third-party packages.

## Building

Make sure all dependencies are installed in your ROS 2 workspace, then build with colcon:

```bash
cd ~/your_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Launch

Simulation with MoveIt and RViz:

```bash
ros2 launch my_robot_gazebo sim.launch.py
```

Headless (no GUI, for testing):

```bash
ros2 launch my_robot_gazebo sim.launch.py headless:=true launch_rviz:=false
```

## File Structure

```
src/
├── README.md
├── deps.repos                 # vcs import manifest for third-party dependencies
├── patches/                   # local fixes to third-party packages + apply script
├── my_robot_description/      # robot model (URDF/Xacro)
├── my_robot_gazebo/           # Gazebo Fortress simulation
└── my_robot_moveit_config/    # MoveIt 2 configuration
```
