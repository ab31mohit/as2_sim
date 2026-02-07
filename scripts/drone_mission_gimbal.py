#!/usr/bin/env python3

import argparse
from time import sleep
from typing import List, Tuple

from as2_python_api.drone_interface import DroneInterface
import rclpy
from rclpy.node import Node
from as2_msgs.msg import GimbalControl
from geometry_msgs.msg import Vector3Stamped
from std_msgs.msg import Header


class DroneMissionGimbalCommander:
    """
    A class to send waypoint mission to the drone with integrated gimbal control.
    """
    
    def __init__(self, drone_namespace: str = 'drone0', verbose: bool = False, use_sim_time: bool = True):
        """
        Initialize the drone mission controller.
        
        :param drone_namespace: Namespace of the drone
        :param verbose: Enable verbose output
        :param use_sim_time: Use simulation time
        """
        self.drone_namespace = drone_namespace
        self.verbose = verbose
        self.use_sim_time = use_sim_time
        self.pi = 3.14159265
        
        print(f'Initializing DroneMissionGimbalController for {drone_namespace}')
        rclpy.init()
        
        self.uav = DroneInterface(
            drone_id=drone_namespace,
            use_sim_time=use_sim_time,
            verbose=verbose
        )
        
        # Create a node for gimbal publishing
        self.gimbal_node = Node('gimbal_controller')
        self.gimbal_publisher = self.gimbal_node.create_publisher(
            GimbalControl, 
            f'/{drone_namespace}/platform/gimbal/gimbal_command', 
            10
        )
        
        self.is_armed = False
        self.is_offboard = False
        self.is_flying = False
        
        # # Default parameters
        self.default_takeoff_height = 1.0
        self.default_takeoff_speed = 1.0
        self.default_mission_speed = 1.0
        self.default_land_speed = 0.5
        self.takeoff_settling_time = 3.0
        
    def takeoff(self, height: float = None, speed: float = None) -> bool:
        """
        Execute takeoff procedure.
        
        :param height: Takeoff height in meters (uses default if None)
        :param speed: Takeoff speed in m/s (uses default if None)
        :return: Success status
        """
        takeoff_height = height if height is not None else self.default_takeoff_height
        takeoff_speed = speed if speed is not None else self.default_takeoff_speed
        
        print(f'\nStarting takeoff to {takeoff_height}m with speed {takeoff_speed}m/s')
        
        # Arm the drone
        print('Arming...')
        arm_success = self.uav.arm()
        print(f'Arm success: {arm_success}')
        if not arm_success:
            return False
        self.is_armed = True
        
        # Set to offboard mode
        print('Setting offboard mode...')
        offboard_success = self.uav.offboard()
        print(f'Offboard success: {offboard_success}')
        if not offboard_success:
            return False
        self.is_offboard = True
        
        # Execute takeoff
        print('Taking off...')
        takeoff_success = self.uav.takeoff(height=takeoff_height, speed=takeoff_speed)
        print(f'Takeoff success: {takeoff_success}')
        
        if takeoff_success:
            self.is_flying = True
            if self.takeoff_settling_time != 0:
                print(f'Waiting for {self.takeoff_settling_time} seconds for drone to settle')
                sleep(self.takeoff_settling_time)
        
        return takeoff_success
    
    def set_gimbal_orientation(self, pitch: float, control_mode: int = 0) -> bool:
        """
        Set gimbal orientation using direct angle control (only controlling pitch)
        
        :param pitch: Pitch angle in radians, positive (look down) and negative (look up)
        :param control_mode: 0=position control, 1=speed control
        :return: Success status
        """
        try:
            
            # Create GimbalControl message
            msg = GimbalControl()
            msg.control_mode = control_mode
            
            # Create Vector3Stamped message
            vector_msg = Vector3Stamped()
            vector_msg.header = Header()
            vector_msg.header.stamp = self.gimbal_node.get_clock().now().to_msg()
            vector_msg.header.frame_id = f'{self.drone_namespace}/gimbal'
            
            # Set the target position (order: roll, pitch, yaw)
            vector_msg.vector.x = 0.0
            vector_msg.vector.y = pitch  
            vector_msg.vector.z = 0.0
            
            msg.target = vector_msg
            
            # Publish the message
            self.gimbal_publisher.publish(msg)
            
            return True
            
        except Exception as e:
            print(f"Error setting gimbal orientation: {e}")
            return False
    
    def go_to_point_with_gimbal(self, x: float, y: float, z: float, 
                              target_yaw: float = 0.0,
                              gimbal_pitch: float = 0.0,
                              speed: float = None,
                              frame_id: str = 'earth') -> bool:
        """
        Go to a waypoint with specific yaw orientation and gimbal pitch control.
        
        This function first moves the drone to the specified position with the desired yaw orientation,
        then sets the gimbal pitch angle.
        
        :param x: Waypoint X coordinate
        :param y: Waypoint Y coordinate  
        :param z: Waypoint Z coordinate
        :param target_yaw: Desired yaw orientation in radians for the drone
        :param gimbal_pitch: Gimbal pitch angle in radians (positive = look down, negative = look up)
        :param speed: Movement speed in m/s (uses default if None)
        :param frame_id: Reference frame of the coordinates
        :return: Success status
        """
        waypoint = [x, y, z]
        movement_speed = speed if speed is not None else self.default_mission_speed
        
        # Use go_to_point_with_yaw to reach waypoint with specific orientation
        success = self.uav.go_to.go_to_point_with_yaw(
            point=waypoint, 
            speed=movement_speed, 
            angle=target_yaw,
            frame_id=frame_id
        )
        
        if not success:
            print(f'Waypoint movement failed: {waypoint}')
            return False

        print('Waypoint reached successfully')
        
        # Set gimbal pitch after reaching waypoint
        gimbal_success = self.set_gimbal_orientation(
            pitch=gimbal_pitch,
        )
        
        if gimbal_success:
            print('Gimbal command sent successfully')
        else:
            print("WARNING: Gimbal pitch command failed after reaching at waypoint!")
        
        return True
    
    def execute_mission(self, waypoints: List[Tuple], mission_speed: float, frame_id: str, wait_at_waypoint: int) -> bool:
        """
        Execute a complete mission with multiple waypoints, yaw orientations, and gimbal commands.
        
        :param waypoints: List of tuples in format (x, y, z, target_yaw, gimbal_pitch)
        :mission_speed: speed in m/s to execute mission at
        :frame_id: frame id of the framw wrt. which mission is to be executed
        :wait_at_waypoint: time is seconds upto which to hold the drone at the waypoint position once it is reached
        :return: Success status
        """
        print(f'\n========= Starting mission of {len(waypoints)} waypoints with speed {mission_speed} m/s and wait_time {wait_at_waypoint} seconds =========')
        
        for i, waypoint in enumerate(waypoints):
            if len(waypoint) != 5:
                print(f"Error: Waypoint {i} must have 5 values (x, y, z, target_yaw, gimbal_pitch)")
                return False
            
            x, y, z, target_yaw, gimbal_pitch = waypoint
            
            print(f'\n--------- Waypoint {i+1}/{len(waypoints)} --------')
            
            # Move to waypoint with specific yaw orientation
            print(f'waypoint pose: [x={x:.2f}, y={y:.2f}, z={z:.2f}, yaw={target_yaw:.2f}]')
            print(f'Gimbal pitch: {gimbal_pitch:.2f} ({gimbal_pitch * 180/self.pi:.2f}°)')
            success = self.go_to_point_with_gimbal(
                x=x, y=y, z=z,
                target_yaw=target_yaw,
                gimbal_pitch=gimbal_pitch,
                speed=mission_speed,
                frame_id=frame_id
            )

            if success:
                # Wait at waypoint if requested
                if wait_at_waypoint != 0:
                    print(f'waiting for {wait_at_waypoint} seconds')
                    sleep(wait_at_waypoint)

            else:
                print(f"Mission failed at waypoint {i+1}")
                return False
        
        print('\n========= All mission waypoints completed successfully =========')
        return True
    
    def land(self, speed: float = None) -> bool:
        """
        Execute landing procedure.
        
        :param speed: Landing speed in m/s (uses default if None)
        :return: Success status
        """
        land_speed = speed if speed is not None else self.default_land_speed
        
        print('\nEnding mission')
        
        # Reset gimbal to neutral position before landing
        print('Resetting gimbal to neutral position...')
        self.set_gimbal_orientation(pitch=0.0)
        sleep(1.0)
        
        # Land
        print(f'Landing with speed {land_speed}m/s...')
        success = self.uav.land(speed=land_speed)
        print(f'Land success: {success}')
        
        if not success:
            print('Landing Failed!')
            return False
        
        # Set to manual mode
        print('Setting UAV to manual mode...')
        manual_success = self.uav.manual()
        print(f'Manual success: {manual_success}')
        
        if manual_success:
            self.is_flying = False
            self.is_offboard = False
            self.is_armed = False
        
        return manual_success
    
    def shutdown(self):
        """Clean shutdown of the controller."""
        print('Shutting down DroneMissionController...')
        if hasattr(self, 'gimbal_node'):
            self.gimbal_node.destroy_node()
        if hasattr(self, 'uav'):
            self.uav.shutdown()
        rclpy.shutdown()
        print('Clean exit')


# Example usage and main function
def main():
    parser = argparse.ArgumentParser(description='Drone Mission with Gimbal Control')
    parser.add_argument('-n', '--namespace', type=str, default='drone0', help='Drone namespace')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-s', '--use_sim_time', action='store_true', default=True, help='Use simulation time')
    
    args = parser.parse_args()
    
    """
    Define mission waypoints with orientation and gimbal commands
    FORMAT: (x, y, z, target_yaw, gimbal_pitch)
    target_yaw: Drone orientation in radians (0 = facing east, π/2 = facing north, etc.)
    gimbal_pitch: Gimbal pitch in radians (positive = look down, negative = look up)
    """
    MISSION_WAYPOINTS = [
        (6.139, 2.742, 1.623, -1.85, -0.129),
        (4.453, 2.054, 4.149, -1.6186, 0.7987),
    ]
    
    # Create controller and execute mission
    controller = DroneMissionGimbalCommander(
        drone_namespace=args.namespace,
        verbose=args.verbose,
        use_sim_time=args.use_sim_time
    )
    
    try:
        # Takeoff
        if not controller.takeoff(height=1.0, speed=1.0):
            print("Takeoff failed!")
            return
        
        # Execute mission with fixed yaw orientation
        if not controller.execute_mission(waypoints=MISSION_WAYPOINTS, mission_speed=1.0, frame_id='earth', wait_at_waypoint=5.0):
            print("Mission failed!")
            return
        
        # Land
        if not controller.land(speed=0.5):
            print("Landing failed!")
            return
            
        print("Mission completed successfully!")
        
    except Exception as e:
        print(f"Mission error: {e}")
    
    finally:
        controller.shutdown()


if __name__ == '__main__':
    main()