#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from as2_msgs.msg import GimbalControl
from geometry_msgs.msg import Vector3Stamped
from std_msgs.msg import Header
import termios
import tty
import sys
import select

class GimbalKeyboardControl(Node):
    def __init__(self):
        super().__init__('gimbal_keyboard_control')

        # Gimbal joint motion publisher
        self.publisher = self.create_publisher(
            GimbalControl, 
            '/drone0/platform/gimbal/gimbal_command', 
            10
        )
        
        self.step_size = 0.78  # 45 degrees in radians
        self.current_position = [0.0, 0.0, 0.0]  # [roll, pitch, yaw]
        self.control_mode = 0  # 0=position, 1=speed
        
        # Set up terminal for non-blocking keyboard input
        self.settings = termios.tcgetattr(sys.stdin)

        self.get_logger().info("""
Gimbal Keyboard Control Started!
------------------------------
Controls:
  Q/E : Roll (Q=-0.78rad, E=+0.78rad)
  W/S : Pitch (W=+0.78rad, S=-0.78rad)
  A/D : Yaw (A=-0.78rad, D=+0.78rad)
  *note*: all these rotations are wrt. drone's FLU body frame.
                               
Exit Methods:
  Press 'ESC' to exit
""")
                
    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
    
    def publish_gimbal_command(self):
        msg = GimbalControl()
        msg.control_mode = self.control_mode
        
        # Create Vector3Stamped message
        vector_msg = Vector3Stamped()
        vector_msg.header = Header()
        vector_msg.header.stamp = self.get_clock().now().to_msg()
        vector_msg.header.frame_id = 'drone0/gimbal'  # reference frame for gimbal motion
        
        # Set the target position
        vector_msg.vector.x = self.current_position[0]  # Roll
        vector_msg.vector.y = self.current_position[1]  # Pitch
        vector_msg.vector.z = self.current_position[2]  # Yaw
        
        msg.target = vector_msg
        self.publisher.publish(msg)
    
    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key()

                # Exit condition
                if key == '\x1b':  # ESC key
                    break
                
                # Motion commands
                elif key == 'q':
                    self.current_position[0] -= self.step_size  # Roll -
                    self.get_logger().info(f"Roll: {self.current_position[0]:.2f} rad")
                elif key == 'e':
                    self.current_position[0] += self.step_size  # Roll +
                    self.get_logger().info(f"Roll: {self.current_position[0]:.2f} rad")
                elif key == 'w':
                    self.current_position[1] += self.step_size  # Pitch +
                    self.get_logger().info(f"Pitch: {self.current_position[1]:.2f} rad")
                elif key == 's':
                    self.current_position[1] -= self.step_size  # Pitch -
                    self.get_logger().info(f"Pitch: {self.current_position[1]:.2f} rad")
                elif key == 'a':
                    self.current_position[2] -= self.step_size  # Yaw -
                    self.get_logger().info(f"Yaw: {self.current_position[2]:.2f} rad")
                elif key == 'd':
                    self.current_position[2] += self.step_size  # Yaw +
                    self.get_logger().info(f"Yaw: {self.current_position[2]:.2f} rad")
                
                if key in ['q', 'e', 'w', 's', 'a', 'd']:
                    self.publish_gimbal_command()
                                          
        except Exception as e:
            self.get_logger().error(f"Error: {str(e)}")

        finally:
            # Reset terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            self.get_logger().info("Keyboard control terminated")

def main(args=None):
    rclpy.init(args=args)
    node = GimbalKeyboardControl()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()