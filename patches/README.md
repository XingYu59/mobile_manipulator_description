# patches — 对第三方依赖的本地修改

本目录保存对 vendored 第三方仓库的**必要本地修改**(未提交到上游)。这些改动是
Gazebo Fortress sim 能正常工作的前提,重新 `vcs import` 后必须重新套用。

## 补丁清单

| 补丁 | 目标仓库/文件 | 内容 | 必要性 |
|---|---|---|---|
| `001-kortex-6dof-ros2_control-var-fix.patch` | ros2_kortex `gen3/6dof/.../kortex.ros2_control.xacro` | `{-2*pi}` → `${-2*pi}` | 修上游 bug:xacro 只求值 `${...}`,原写法使关节限位变成字面量 |
| `002-kortex-7dof-ros2_control-var-fix.patch` | ros2_kortex `gen3/7dof/.../kortex.ros2_control.xacro` | 同上 | 同上 |
| `003-clearpath-dd100-imu-via-ros2_control.patch` | clearpath_common `urdf/dd100/dd100.urdf.xacro` | 移除内置 gz IMU 传感器,改为在 ros2_control 暴露 IMU 状态接口 | gz-sim 6.18 不通过 gz transport 发布 imu,需走 `imu_sensor_broadcaster` |
| `004-clearpath-gazebo-topic-remap.patch` | clearpath_common `urdf/generic/gazebo.urdf.xacro` | 话题从 `platform/odom` 等重映射为顶层 `odom`/`cmd_vel`/`joint_states` | 让 moveit/导航/用户节点订阅标准话题名 |

## 怎么套用

在**工作区 `src/` 目录**下(第三方包已 `vcs import` 完成后):

```bash
./patches/apply_patches.sh
```

或手动逐个套:

```bash
cd ros2_kortex       && git apply ../patches/001-kortex-6dof-ros2_control-var-fix.patch
cd ros2_kortex       && git apply ../patches/002-kortex-7dof-ros2_control-var-fix.patch
cd clearpath_common  && git apply ../patches/003-clearpath-dd100-imu-via-ros2_control.patch
cd clearpath_common  && git apply ../patches/004-clearpath-gazebo-topic-remap.patch
```

## 注意事项

- 补丁基于 `deps.repos` 锁定的版本生成;升级第三方包后若套用失败,请重新
  `git diff` 生成新补丁。
- 上游若已修复对应问题,可直接删除对应补丁文件。
