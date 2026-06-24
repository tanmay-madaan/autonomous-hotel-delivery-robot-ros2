#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class TwistStamper(Node):
    """Convert Twist teleop commands to TwistStamped for diff_drive_controller (Jazzy)."""

    def __init__(self):
        super().__init__('twist_stamper')
        self.declare_parameter('input_topic', 'cmd_vel_unstamped')
        self.declare_parameter('output_topic', 'cmd_vel')
        self.declare_parameter('frame_id', 'base_footprint')

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        self._frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        self._publisher = self.create_publisher(TwistStamped, output_topic, 10)
        self.create_subscription(Twist, input_topic, self._callback, 10)

    def _callback(self, msg: Twist) -> None:
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = self._frame_id
        stamped.twist = msg
        self._publisher.publish(stamped)


def main() -> None:
    rclpy.init()
    node = TwistStamper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
