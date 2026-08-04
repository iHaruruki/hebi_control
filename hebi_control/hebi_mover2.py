import time

import rclpy
from control_msgs.action import GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Empty


"""Sequence manager node for publishing predefined HEBI motions."""

class SequenceController(Node):
    """Runs a hard-coded motion + gripper sequence."""

    def __init__(self):
        """Initialize publishers, action client, and start the sequence."""
        super().__init__('sequence_controller')
        self.pub1 = self.create_publisher(Empty, '/exec_move1', 10)
        self.pub2 = self.create_publisher(Empty, '/exec_move2', 10)
        self.pub3 = self.create_publisher(Empty, '/exec_move3', 10)
        self.pub3_j6 = self.create_publisher(Empty, '/exec_j6_only3', 10)
        self.pub4_j6 = self.create_publisher(Empty, '/exec_j6_only4', 10)
        self.pub5_j6 = self.create_publisher(Empty, '/exec_j6_only5', 10)
        self.pub_home = self.create_publisher(Empty, '/exec_home', 10)


        self._action_client = ActionClient(
            self, GripperCommand, '/gripper_controller/gripper_cmd'
        )

        self.get_logger().info('Start to autosequence.')
        self.run_sequence()

    def send_gripper_goal(self, position):
        """Send a gripper goal asynchronously."""
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = 10.0

        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)

    def run_sequence(self):
        """Run the full sequence and then exit the process."""
        time.sleep(2.0)

        self.get_logger().info('Running Move 1')
        self.pub1.publish(Empty())

        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)

        self.get_logger().info('Running Move 2')
        self.pub2.publish(Empty())

        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)

        self.get_logger().info('Close Gripper')
        self.send_gripper_goal(1.0)

        self.get_logger().info('Wait 3 seconds')
        time.sleep(3.0)

        self.get_logger().info('Running Move 3 j6')
        self.pub3_j6.publish(Empty())

        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)

        self.get_logger().info('Running Move 4 j6')
        self.pub4_j6.publish(Empty())
        
        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)
        
        self.get_logger().info('Running Move 5 j6')
        self.pub5_j6.publish(Empty())
        
        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)        
        
        self.get_logger().info('Running Move 3')
        self.pub3.publish(Empty())

        self.get_logger().info('Wait 10 seconds')
        time.sleep(10.0)

        self.get_logger().info('Open Gripper')
        self.send_gripper_goal(0.0)
        
        self.get_logger().info('Wait 3 seconds')
        time.sleep(3.0)
        
        self.get_logger().info('Running Move to home')
        self.pub_home.publish(Empty())
        
        self.get_logger().info('Sequence Finished.')

        raise SystemExit


def main():
    """Entry point for the `hebi_mover` console script."""
    rclpy.init()
    node = SequenceController()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    node.destroy_node()
    rclpy.shutdown()


