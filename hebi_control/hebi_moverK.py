import time
import rclpy
import threading
from control_msgs.action import GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Empty
from std_msgs.msg import String
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

"""Sequence manager node for publishing predefined HEBI motions."""

class SequenceController(Node):
    """Runs a hard-coded motion + gripper sequence."""

    def __init__(self):
        """Initialize publishers, action client, and start the sequence."""
        super().__init__('sequence_controller')
        
        self.callback_group = ReentrantCallbackGroup()
        
        self.pub1 = self.create_publisher(Empty, '/exec_move1', 10)
        self.pub2 = self.create_publisher(Empty, '/exec_move2', 10)
        self.pub3 = self.create_publisher(Empty, '/exec_move3', 10)
        self.pub4 = self.create_publisher(Empty, '/exec_move4', 10)
        self.pub1_j6 = self.create_publisher(Empty, '/exec_j6_only1', 10)
        self.pub2_j6 = self.create_publisher(Empty, '/exec_j6_only2', 10)
        self.pubU0 = self.create_publisher(Empty, '/exec_moveU0', 10)
        self.pubU1 = self.create_publisher(Empty, '/exec_moveU1', 10)
        self.pubU2 = self.create_publisher(Empty, '/exec_moveU2', 10)
        self.pubU3 = self.create_publisher(Empty, '/exec_moveU3', 10)
        self.pubU4 = self.create_publisher(Empty, '/exec_moveU4', 10)
        self.pubU1_j6 = self.create_publisher(Empty, '/exec_j6_onlyU1', 10)
        self.pubU2_j6 = self.create_publisher(Empty, '/exec_j6_onlyU2', 10)
        self.pubU3_j6 = self.create_publisher(Empty, '/exec_j6_onlyU3', 10)
        self.pubno_j6 = self.create_publisher(Empty, '/exec_j6_onlyno', 10)
        self.pub_home = self.create_publisher(Empty, '/exec_home', 10)
        
        self._action_client = ActionClient(
            self, GripperCommand, '/gripper_controller/gripper_cmd', callback_group=self.callback_group
        )
        
        # Flags to track completion of motion
        self.move_done = False
        
        self.sub_move_done = self.create_subscription(
            Empty, '/move_done', self._move_complete_callback,
            10, callback_group=self.callback_group
        )
        
    # Callback functions for motion completion feedback
    def _move_complete_callback(self, msg):
        """Callback when Move completes."""
        self.get_logger().info('===== [CALLBACK] Received /move_done signal =====')
        self.move_done = True

    def send_gripper_goal(self, position):
        """Send a gripper goal asynchronously."""
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = 10.0

        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)
        
    def wait_for_completion(self, flag_name, timeout=60.0):
        """
        Wait for a move to complete with timeout.
        
        Args:
            flag_name: Name of the completion flag to monitor (e.g., 'move1_done')
            timeout: Maximum time to wait in seconds
        """
        self.get_logger().info(f'  → Waiting for {flag_name} (timeout: {timeout}s)')
        start_time = self.get_clock().now()
        
        # Poll the flag until it's True or timeout occurs
        while not getattr(self, flag_name):
            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            
            # Check if timeout exceeded
            if elapsed > timeout:
                self.get_logger().warn(f'  ✗ TIMEOUT waiting for {flag_name} after {elapsed:.1f}s')
                self.get_logger().warn(f'     → Make sure the motion executor is publishing to the correct topic!')
                break
            time.sleep(0.01)
        
        # Log successful completion with elapsed time
        elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
        if getattr(self, flag_name):
            self.get_logger().info(f'  ✓ {flag_name} completed in {elapsed:.1f}s')

    def run_sequence(self):
        """Run the full sequence and then exit the process."""
        self.get_logger().info('Initial delay: 3 seconds...')
        time.sleep(2.0)
        
        self.get_logger().info('Start sequence')
        self.move_done = False
        self.pub_home.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.send_gripper_goal(0.0)
        time.sleep(1.0)
        
        self.get_logger().info('Running Move 1')
        self.move_done = False
        self.pub1.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Running Move 2')
        self.move_done = False
        self.pub2.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Close Gripper')
        self.send_gripper_goal(1.0)
        time.sleep(1.0)
        
        self.get_logger().info('Running Move 3')
        self.move_done = False
        self.pub3.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Running Move 1 j6')
        self.move_done = False
        self.pub1_j6.publish(Empty())
        self.wait_for_completion('move_done', timeout=10.0)

        self.get_logger().info('Running Move 2 j6')
        self.move_done = False
        self.pub2_j6.publish(Empty())
        self.wait_for_completion('move_done', timeout=10.0)
        
        self.get_logger().info('Running Move 4')
        self.move_done = False
        self.pub4.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.get_logger().info('Open Gripper')
        self.send_gripper_goal(0.0)
        time.sleep(1.0)
        
        self.get_logger().info('Running Move 1')
        self.move_done = False
        self.pub1.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.get_logger().info('Running Move U0')
        self.move_done = False
        self.pubU0.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.get_logger().info('Running Move U1 j6')
        self.move_done = False
        self.pubU1_j6.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
                
        self.get_logger().info('Running Move U1')
        self.move_done = False
        self.pubU1.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Running Move U2')
        self.move_done = False
        self.pubU2.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Close Gripper')
        self.send_gripper_goal(1.0)
        time.sleep(1.0)
        
        self.get_logger().info('Running Move U3')
        self.move_done = False
        self.pubU3.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Running Move U2 j6')
        self.move_done = False
        self.pubU2_j6.publish(Empty())
        self.wait_for_completion('move_done', timeout=10.0)

        self.get_logger().info('Running Move U3 j6')
        self.move_done = False
        self.pubU3_j6.publish(Empty())
        self.wait_for_completion('move_done', timeout=10.0)

        self.get_logger().info('Running Move U4')
        self.move_done = False
        self.pubU4.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Open Gripper')
        self.send_gripper_goal(0.0)
        time.sleep(1.0)
        
        self.get_logger().info('Running Move U1')
        self.move_done = False
        self.pubU1.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.get_logger().info('Running Move U0')
        self.move_done = False
        self.pubU0.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)
        
        self.get_logger().info('Running Move to home')
        self.move_done = False
        self.pub_home.publish(Empty())
        self.wait_for_completion('move_done', timeout=5.0)

        self.get_logger().info('Sequence Finished.')
	
        rclpy.shutdown()
	
def main():
    """Entry point for the `hebi_mover` console script."""
    rclpy.init()

    node = SequenceController()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    threading.Thread(
        target=node.run_sequence,
        daemon=True
    ).start()

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

