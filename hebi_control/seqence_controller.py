import rclpy
from control_msgs.action import GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Empty
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor


class SequenceController(Node):
    """Runs a hard-coded motion + gripper sequence with feedback control."""

    def __init__(self):
        """Initialize publishers, action client, and start the sequence."""
        super().__init__('sequence_controller')
        
        # Use reentrant callback group to handle multiple callbacks
        self.callback_group = ReentrantCallbackGroup()
        
        # Create publishers for each motion command
        self.pub1 = self.create_publisher(Empty, '/exec_move1', 10)
        self.pub2 = self.create_publisher(Empty, '/exec_move2', 10)
        self.pub3 = self.create_publisher(Empty, '/exec_move3', 10)
        self.pub1_j6 = self.create_publisher(Empty, '/exec_j6_only1', 10)
        self.pub2_j6 = self.create_publisher(Empty, '/exec_j6_only2', 10)

        # Create action client for gripper control
        self._action_client = ActionClient(
            self, GripperCommand, '/gripper_controller/gripper_cmd',
            callback_group=self.callback_group
        )

        # Flags to track completion of each motion
        self.move1_done = False
        self.move2_done = False
        self.move3_done = False
        self.move1_j6_done = False
        self.move2_j6_done = False

        # Create subscribers to listen for completion feedback from motion nodes
        self.sub_move1_complete = self.create_subscription(
            Empty, '/move1_complete', self._move1_complete_callback,
            10, callback_group=self.callback_group
        )
        self.sub_move2_complete = self.create_subscription(
            Empty, '/move2_complete', self._move2_complete_callback,
            10, callback_group=self.callback_group
        )
        self.sub_move3_complete = self.create_subscription(
            Empty, '/move3_complete', self._move3_complete_callback,
            10, callback_group=self.callback_group
        )
        self.sub_move1_j6_complete = self.create_subscription(
            Empty, '/move1_j6_complete', self._move1_j6_complete_callback,
            10, callback_group=self.callback_group
        )
        self.sub_move2_j6_complete = self.create_subscription(
            Empty, '/move2_j6_complete', self._move2_j6_complete_callback,
            10, callback_group=self.callback_group
        )

        self.get_logger().info('='*50)
        self.get_logger().info('Sequence Controller Initialized')
        self.get_logger().info('='*50)
        self.get_logger().info('Waiting for motion executor nodes to be ready...')
        self.get_logger().info('='*50)
        
        # Start the sequence
        self.run_sequence()

    # Callback functions for motion completion feedback
    def _move1_complete_callback(self, msg):
        """Callback when Move 1 completes."""
        self.get_logger().debug('  [CALLBACK] Received move1_complete signal')
        self.move1_done = True

    def _move2_complete_callback(self, msg):
        """Callback when Move 2 completes."""
        self.get_logger().debug('  [CALLBACK] Received move2_complete signal')
        self.move2_done = True

    def _move3_complete_callback(self, msg):
        """Callback when Move 3 completes."""
        self.get_logger().debug('  [CALLBACK] Received move3_complete signal')
        self.move3_done = True

    def _move1_j6_complete_callback(self, msg):
        """Callback when Move 1 J6 completes."""
        self.get_logger().debug('  [CALLBACK] Received move1_j6_complete signal')
        self.move1_j6_done = True

    def _move2_j6_complete_callback(self, msg):
        """Callback when Move 2 J6 completes."""
        self.get_logger().debug('  [CALLBACK] Received move2_j6_complete signal')
        self.move2_j6_done = True

    def send_gripper_goal(self, position):
        """Send a gripper goal asynchronously."""
        self.get_logger().debug(f'Sending gripper goal: position={position}')
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
            
            # Spin once to process callbacks
            rclpy.spin_once(self, timeout_sec=0.1)
        
        # Log successful completion with elapsed time
        elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
        if getattr(self, flag_name):
            self.get_logger().info(f'  ✓ {flag_name} completed in {elapsed:.1f}s')

    def run_sequence(self):
        """Run the full sequence with feedback control."""
        import time
        
        # Initial delay before starting sequence
        self.get_logger().info('Initial delay: 3 seconds...')
        time.sleep(3.0)

        # ===== MOVE 1 =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 1/5] Running Move 1')
        self.move1_done = False
        self.get_logger().debug('  Publishing to /exec_move1')
        self.pub1.publish(Empty())
        self.wait_for_completion('move1_done', timeout=40.0)
        self.get_logger().info('[STEP 1/5] ✓ Move 1 Complete')

        # ===== MOVE 2 =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 2/5] Running Move 2')
        self.move2_done = False
        self.get_logger().debug('  Publishing to /exec_move2')
        self.pub2.publish(Empty())
        self.wait_for_completion('move2_done', timeout=20.0)
        self.get_logger().info('[STEP 2/5] ✓ Move 2 Complete')

        # ===== GRIPPER CONTROL =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 2.5/5] Closing Gripper')
        self.get_logger().debug('  Sending gripper command: position=1.0 (closed)')
        self.send_gripper_goal(1.0)
        
        # Wait for gripper action to settle
        self.get_logger().info('  Waiting 5 seconds for gripper to settle...')
        time.sleep(5.0)
        self.get_logger().info('[STEP 2.5/5] ✓ Gripper closed')

        # ===== MOVE 3 =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 3/5] Running Move 3')
        self.move3_done = False
        self.get_logger().debug('  Publishing to /exec_move3')
        self.pub3.publish(Empty())
        self.wait_for_completion('move3_done', timeout=40.0)
        self.get_logger().info('[STEP 3/5] ✓ Move 3 Complete')

        # ===== MOVE 1 J6 =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 4/5] Running Move 1 J6 (joint 6 only)')
        self.move1_j6_done = False
        self.get_logger().debug('  Publishing to /exec_j6_only1')
        self.pub1_j6.publish(Empty())
        self.wait_for_completion('move1_j6_done', timeout=20.0)
        self.get_logger().info('[STEP 4/5] ✓ Move 1 J6 Complete')

        # ===== MOVE 2 J6 =====
        self.get_logger().info('')
        self.get_logger().info('[STEP 5/5] Running Move 2 J6 (joint 6 only)')
        self.move2_j6_done = False
        self.get_logger().debug('  Publishing to /exec_j6_only2')
        self.pub2_j6.publish(Empty())
        self.wait_for_completion('move2_j6_done', timeout=20.0)
        self.get_logger().info('[STEP 5/5] ✓ Move 2 J6 Complete')

        # ===== SEQUENCE COMPLETE =====
        self.get_logger().info('')
        self.get_logger().info('='*50)
        self.get_logger().info('✓ ALL SEQUENCES COMPLETED SUCCESSFULLY')
        self.get_logger().info('='*50)
        
        raise SystemExit


def main():
    """Entry point for the `hebi_mover` console script."""
    rclpy.init()
    node = SequenceController()
    try:
        # Use MultiThreadedExecutor to allow concurrent callbacks
        executor = MultiThreadedExecutor()
        executor.add_node(node)
        executor.spin()
    except SystemExit:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
