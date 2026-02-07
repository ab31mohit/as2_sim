cmake_minimum_required(VERSION 3.8)
project(as2_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)

# # Aerostack2 dependencies
find_package(as2_core REQUIRED)
find_package(as2_msgs REQUIRED)
find_package(as2_gazebo_assets REQUIRED)
find_package(as2_platform_gazebo REQUIRED)

# # Message packages
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(sensor_msgs REQUIRED)

# #  Gazebo
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)

## Install launch and config folders
install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}/
)


# Install python nodes scripts
install(PROGRAMS
  scripts/gimbal_teleop_keyboard.py
  scripts/drone_mission_gimbal.py
  DESTINATION lib/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
