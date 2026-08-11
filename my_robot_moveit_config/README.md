# my_robot_moveit_config


MoveIt 2 configuration for the **my_robot** mobile manipulator (Dingo dd100 base + Kinova Gen3 6-DOF arm + Robotiq 2F-85 gripper), generated with the MoveIt Setup Assistant and re-targeted for the dd100 base — used for motion planning and grasping.

## Planning Groups

| Group | Type | Contents |
|---|---|---|
| `manipulator` | chain | `arm_base_link` → `arm_end_effector_link` (Gen3 joints 1–6 + fixed end-effector joint) |
| `gripper` | joints | Robotiq 2F-85 joints (`arm_robotiq_85_*`) |

Named states:

| Group | State | Value |
|---|---|---|
| `manipulator` | `Vertical` / `Home` / `Retract` | Predefined arm poses |
| `gripper` | `Open` / `Close` | Knuckle 0 / 0.8 |

## Controllers

`config/moveit_controllers.yaml` maps MoveIt groups to the simulation controllers (names match `my_robot_gazebo/config/gazebo_controllers.yaml`):

| Controller | MoveIt type | Manages | Action namespace |
|---|---|---|---|
| `joint_trajectory_controller` | `FollowJointTrajectory` | Gen3 arm (`arm_joint_1..6`) | `follow_joint_trajectory` |
| `robotiq_gripper_controller` | `GripperCommand` | Gripper knuckle | `gripper_cmd` |

## Kinematics

`config/kinematics.yaml` uses the **KDL** solver for the `manipulator` group (6-DOF chain, tip `arm_end_effector_link`).

## Notes

- The **collision matrix** was regenerated with the MoveIt Setup Assistant `collisions_updater` against the actual **dd100** URDF (183 pairs: 152 Never + 26 Adjacent + 5 Default), replacing the stale A200 collision pairs.
- `my_robot.srdf.a200.bak` (kept outside `config/`) is the old A200 SRDF backup — do not move it back into `config/`, it would be installed by the CMake `install(DIRECTORY config ...)` rule.
- Requires the kortex `{-2*pi}` fix (see `patches/`) for the arm's joint limits to be evaluated correctly.

## Dependencies

- `my_robot_description` - robot model
- `moveit_ros_planning`, `moveit_ros_move_group` - MoveIt 2 core
- `moveit_simple_controller_manager` - controller management
- `ros2_robotiq_gripper` - gripper description
- `ros2_controllers` - `joint_trajectory_controller`, `diff_drive_controller`, etc.

## Usage

Plan and execute grasping with the MoveIt 2 **MoveGroup** action (`/move_action`), e.g. from RViz (MoveGroup plugin) or the `moveit_py`/`move_group_interface` API:

- Plan to a grasp pose with group `manipulator` (target link `arm_end_effector_link`), then execute
- Close the gripper with group `gripper` (target joint `arm_robotiq_85_left_knuckle_joint`, value ≈ 0.8)
- Return to a home pose (named state `Home` / `Retract`)

Interactive demo (MoveIt + RViz only, no simulation):

```bash
ros2 launch my_robot_moveit_config demo.launch.py
```

## File Structure

```
my_robot_moveit_config/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── my_robot.srdf                # SRDF: groups, named states, collision matrix
│   ├── my_robot.urdf.xacro          # MoveIt view of the robot
│   ├── my_robot.ros2_control.xacro  # ros2_control (fake / gazebo hardware)
│   ├── kinematics.yaml              # KDL solver
│   ├── moveit_controllers.yaml      # MoveIt -> controller mapping
│   ├── joint_limits.yaml            # Joint limits
│   ├── ompl_planning.yaml           # OMPL planner settings
│   └── ...                          # Setup Assistant generated configs
└── launch/
    ├── demo.launch.py               # Interactive demo (MoveIt + RViz)
    ├── move_group.launch.py         # move_group only
    └── ...                          # Setup Assistant generated launch files
```
