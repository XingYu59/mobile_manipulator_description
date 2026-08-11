#!/usr/bin/env bash
# Apply the third-party patches listed in patches/README.md.
# Run from the workspace src/ directory (where the third-party repos live).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

apply() { # $1=repo  $2=patch
  local repo="$1" patch="$2"
  echo "==> $repo  <-  $patch"
  (cd "$DIR/../$repo" && git apply "$DIR/$patch")
  echo "    OK"
}

apply ros2_kortex       001-kortex-6dof-ros2_control-var-fix.patch
apply ros2_kortex       002-kortex-7dof-ros2_control-var-fix.patch
apply clearpath_common  003-clearpath-dd100-imu-via-ros2_control.patch
apply clearpath_common  004-clearpath-gazebo-topic-remap.patch

echo "All patches applied."
