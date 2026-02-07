#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Define launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='drone0',
        description='Namespace for the drone'
    )

    # Get package share directory
    pkg_share = get_package_share_directory('as2_sim')
    
    # Paths to configuration files
    simulation_world_config = PathJoinSubstitution([pkg_share, 'config', 'simulation_world.yaml'])
    drone_platform_config = PathJoinSubstitution([pkg_share, 'config', 'drone_platform.yaml'])
    pid_speed_control_config = PathJoinSubstitution([pkg_share, 'config', 'pid_speed_controller.yaml'])

    # Include all launch files with parameter propagation
    simulation_world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_gazebo_assets'),
                'launch/launch_simulation.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'simulation_config_file': simulation_world_config
        }.items()
    )

    drone_platform_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_platform_gazebo'),
                'launch/platform_gazebo_launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'platform_config_file': drone_platform_config,
            'simulation_config_file': simulation_world_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    state_estimator_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_state_estimator'),
                'launch/state_estimator_launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'config_file': drone_platform_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    motion_controllers_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_motion_controller'),
                'launch/controller_launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'config_file': drone_platform_config,
            'plugin_name': 'pid_speed_controller',
            'plugin_config_file': pid_speed_control_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    motion_behaviors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_behaviors_motion'),
                'launch/motion_behaviors_launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'config_file': drone_platform_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    trajectory_gen_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_behaviors_trajectory_generation'),
                'launch/generate_polynomial_trajectory_behavior_launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'config_file': drone_platform_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    gimbal_behavior_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_behaviors_perception'),
                'launch/point_gimbal_behavior.launch.py'
            )
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace'),
            'config_file': drone_platform_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    return LaunchDescription([
        use_sim_time_arg,
        namespace_arg,
        simulation_world_launch,
        drone_platform_launch,
        state_estimator_launch,
        motion_controllers_launch,
        motion_behaviors_launch,
        trajectory_gen_launch,
        gimbal_behavior_launch
    ])