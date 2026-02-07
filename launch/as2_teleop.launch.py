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

    # Include all launch files with parameter propagation
    as2_keyboard_teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('as2_keyboard_teleoperation'),
                'launch/as2_keyboard_teleoperation_launch.py')
        ]),
        launch_arguments={
            'namespace': LaunchConfiguration('namespace')
        }.items()
    )

    return LaunchDescription([
        use_sim_time_arg,
        namespace_arg,
        as2_keyboard_teleop_launch
    ])