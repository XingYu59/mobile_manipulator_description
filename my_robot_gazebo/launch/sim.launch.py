# Copyright (c) 2025
#
# Gazebo Fortress (Gazebo Sim 6) + MoveIt simulation for my_robot (Humble)
#
# Dingo dd100 差分底盘 + Kinova Gen3 + Robotiq 2F-85 + 桅杆深度相机 + 2D LiDAR + IMU
#
# Key design points:
#   - ros2_control 由 clearpath generic/gazebo.urdf.xacro 注入的单个
#     libign_ros2_control-system.so 插件统一管理(底座 + 臂 + 夹爪)
#   - controller_manager 默认名 /controller_manager
#   - 传感器(scan/imu/camera)经 ros_gz_bridge 桥接
#   - spawn 用 ros_gz_sim create -topic robot_description
#
# Usage:
#   ros2 launch my_robot_gazebo sim.launch.py
#   ros2 launch my_robot_gazebo sim.launch.py headless:=true launch_rviz:=false

import os
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    ExecuteProcess,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")
    launch_rviz = LaunchConfiguration("launch_rviz")
    headless = LaunchConfiguration("headless").perform(context)
    world_name = LaunchConfiguration("world").perform(context)

    # ==================== URDF (xacro) ====================
    # 已修复 kortex {2*pi} 源,无需任何正则后处理
    xacro_file = os.path.join(
        get_package_share_directory("my_robot_description"),
        "robot_description",
        "my_robot_description.xacro",
    )
    result = subprocess.run(
        [
            "xacro", xacro_file,
            "use_platform_controllers:=true",
            "is_sim:=true",
            "sim_ignition:=true",
            "sim_gazebo:=false",
            "sim_gazebo_sensors:=false",
            "use_fake_hardware:=false",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"xacro failed:\n{result.stderr}")
    urdf = result.stdout

    # ==================== robot_state_publisher ====================
    # 同时把 robot_description 作为 latched topic 发布,供 ros_gz_sim create 订阅
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": urdf,
                "use_sim_time": use_sim_time,
                "publish_frequency": 10.0,
            }
        ],
    )

    # ==================== Gazebo Fortress ====================
    # 让 gz 能解析 URDF 里的 package:// -> model:// 网格(clearpath/kortex 等包)
    # 各包 share 的父目录(install/<pkg>/share)内含 <pkg>/ 子目录
    resource_paths = [
        os.path.dirname(get_package_share_directory("clearpath_platform_description")),
        os.path.dirname(get_package_share_directory("kortex_description")),
        os.path.dirname(get_package_share_directory("my_robot_description")),
    ]
    os.environ["GZ_SIM_RESOURCE_PATH"] = os.pathsep.join([
        os.environ.get("GZ_SIM_RESOURCE_PATH", ""),
        *resource_paths,
    ])

    # -r 立即运行(headless 时另加 -s 只启 server)
    world_path = os.path.join(
        get_package_share_directory("my_robot_gazebo"), "worlds", world_name
    )
    gz_args = f"{'-s ' if headless == 'true' else ''}-r {world_path}"
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ]),
        launch_arguments={
            "gz_args": gz_args,
            "gz_version": "6",
        }.items(),
    )

    # ==================== Spawn Robot ====================
    # 用 ros_gz_sim create 从 robot_description topic 生成模型;
    # 延迟 6s 覆盖 gz server 启动 + RSP 发布
    spawn_robot = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                name="spawn_my_robot",
                arguments=[
                    "-world", "default",
                    "-topic", "robot_description",
                    "-name", "my_robot",
                    "-x", "0", "-y", "0", "-z", "0",
                ],
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ],
    )

    # ==================== Sensor Bridge (gz -> ROS) ====================
    # cmd_vel/odom/joint_states 由 ros2_control 直接发布为 ROS topic,无需 bridge;
    # 传感器经 config/bridge.yaml 配置(gz_topic_name 与 ros_topic_name 可不同)
    bridge_yaml = os.path.join(
        get_package_share_directory("my_robot_gazebo"), "config", "bridge.yaml"
    )
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="sensor_bridge",
        arguments=["--ros-args", "-p", f"config_file:={bridge_yaml}"],
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # ==================== Controller Spawners ====================
    # 等待 /controller_manager/list_controllers service 就绪后再 spawn
    # (controller_manager 由 gz ros2_control 插件在模型生成时创建)
    def _spawner(name, delay):
        return TimerAction(
            period=delay,
            actions=[
                ExecuteProcess(
                    cmd=[
                        "bash", "-c",
                        f'until ros2 service list 2>/dev/null | grep -q '
                        f'"/controller_manager/list_controllers"; do sleep 0.5; done; '
                        f'exec ros2 run controller_manager spawner {name} -c /controller_manager',
                    ],
                    output="screen",
                )
            ],
        )

    # ==================== MoveIt ====================
    moveit_config = (
        MoveItConfigsBuilder("my_robot", package_name="my_robot_moveit_config")
        .robot_description(mappings={
            "use_platform_controllers": "true",
            "is_sim": "true",
            "sim_ignition": "true",
            "sim_gazebo": "false",
            "sim_gazebo_sensors": "false",
            "use_fake_hardware": "false",
        })
        .robot_description_semantic(file_path="config/my_robot.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=False,
            publish_robot_description_semantic=True,
        )
        .planning_pipelines(pipelines=["ompl", "pilz_industrial_motion_planner"])
        .to_moveit_configs()
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        name="move_group",
        output="screen",
        parameters=[moveit_config.to_dict(), {"use_sim_time": use_sim_time}],
    )

    rviz_config = PathJoinSubstitution([
        FindPackageShare("my_robot_moveit_config"), "config", "moveit.rviz"
    ])
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {"use_sim_time": use_sim_time},
        ],
        condition=IfCondition(launch_rviz),
    )

    return [
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
        _spawner("joint_state_broadcaster", 8.0),
        _spawner("platform_velocity_controller", 10.0),
        _spawner("joint_trajectory_controller", 12.0),
        _spawner("robotiq_gripper_controller", 14.0),
        _spawner("imu_sensor_broadcaster", 16.0),
        move_group,
        rviz,
    ]


def generate_launch_description():
    args = [
        DeclareLaunchArgument("world", default_value="empty.world"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("launch_rviz", default_value="true"),
        DeclareLaunchArgument("headless", default_value="false"),
    ]
    return LaunchDescription(args + [OpaqueFunction(function=launch_setup)])
