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


class SequenceController(Node):
    """Runs a hard-coded motion + gripper sequence with feedback control."""

    def __init__(self):
        """Initialize publishers, action client, and start the sequence."""
        super().__init__('sequence_controller')
        
        # Use reentrant callback group to handle multiple callbacks
        self.callback_group = ReentrantCallbackGroup()
        
        # Create publishers for each motion command
        self.pub_home = self.create_publisher(Empty, '/exec_home', 10)
        self.pub_ready = self.create_publisher(Empty, '/exec_ready', 10)
        self.pub_approach = self.create_publisher(Empty, '/exec_approach', 10)
        self.pub_grasp = self.create_publisher(Empty, '/exec_grasp', 10)
        self.pub_roll = self.create_publisher(Empty, '/exec_roll', 10)
        self.pub_place = self.create_publisher(Empty, '/exec_place', 10)
        self.pub_retreat = self.create_publisher(Empty, '/exec_retreat', 10)
        self.pub_bell = self.create_publisher(String, "/selected_bell", 10)

        # Create action client for gripper control
        self._action_client = ActionClient(
            self, GripperCommand, '/gripper_controller/gripper_cmd', callback_group=self.callback_group
        )

        # Flags to track completion of motion
        self.move_done = False
        
        # Create subscribers to listen for completion feedback from motion nodes
        self.sub_move_done = self.create_subscription(
            Empty, '/move_done', self._move_complete_callback,
            10, callback_group=self.callback_group
        )
        self.sub_command = self.create_subscription(
            String, "/sequence_command", self.command_callback,
            10, callback_group=self.callback_group
        )

        self.get_logger().info('='*50)
        self.get_logger().info('Sequence Controller Initialized')
        self.get_logger().info('='*50)
        self.get_logger().info('Waiting for motion executor nodes to be ready...')
        self.get_logger().info('='*50)

    # Callback functions for motion completion feedback
    def _move_complete_callback(self, msg):
        """Callback when Move completes."""
        self.get_logger().info('===== [CALLBACK] Received /move_done signal =====')
        self.move_done = True

    def send_gripper_goal(self, position):
        """Send a gripper goal asynchronously."""
        self.get_logger().info(f'Sending gripper goal: position={position}')
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = 10.0

        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)
    
    # Pose Functions  
    def home(self):
    	self.get_logger().info('Now Homing...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_home =====")
    	self.pub_home.publish(Empty())
    	self.wait_for_completion('move_done', timeout=5.0)
    	self.get_logger().info('Homing Complete')
    	
    def ready(self):
    	self.get_logger().info('Now Preparing...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_ready =====")
    	self.pub_ready.publish(Empty())
    	self.wait_for_completion('move_done', timeout=5.0)
    	self.get_logger().info('Preparing Complete')
    	
    def approach(self):
    	self.get_logger().info('Now Approaching...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_approach =====")
    	self.pub_approach.publish(Empty())
    	self.wait_for_completion('move_done', timeout=3.0)
    	self.get_logger().info('Approaching Complete')
    	
    def close_gripper(self):
    	self.get_logger().info('Now Grasping...')
    	self.get_logger().info('Closing Gripper...')
    	self.send_gripper_goal(1.0)
    	time.sleep(1.0)
    	self.get_logger().info('Gripper closed')
	
    def grasp(self):
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_grasp =====")
    	self.pub_grasp.publish(Empty())
    	self.wait_for_completion('move_done', timeout=3.0)
    	self.get_logger().info('Grasping Complete')
    	
    def roll(self):
    	self.get_logger().info('Now Rolling...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_roll =====")
    	self.pub_roll.publish(Empty())
    	self.wait_for_completion('move_done', timeout=3.0)
    	self.get_logger().info('Rolling Complete')
    	
    def place(self):
    	self.get_logger().info('Now Placing...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_place =====")
    	self.pub_place.publish(Empty())
    	self.wait_for_completion('move_done', timeout=3.0)
    	self.get_logger().info('Placing Complete')
    
    def open_gripper(self):
    	self.get_logger().info('Opening Gripper...')
    	self.send_gripper_goal(0.0)
    	time.sleep(1.0)
    	self.get_logger().info('Gripper opened')
    	
    def retreat(self):
    	self.get_logger().info('Now Retreating...')
    	self.move_done = False
    	self.get_logger().info("===== Publishing /exec_retreat =====")
    	self.pub_retreat.publish(Empty())
    	self.wait_for_completion('move_done', timeout=3.0)
    	self.get_logger().info('Retreating Complete')
    	
    def select_bell(self, bell_name):
        msg = String()
        msg.data = bell_name
        self.pub_bell.publish(msg)
        self.get_logger().info(f"Selected bell: {bell_name}")
    	
    	
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
        """Run the full sequence with feedback control."""
        
        # Initial delay before starting sequence
        self.get_logger().info('Initial delay: 3 seconds...')
        time.sleep(3.0)
        
        self.home()
        self.open_gripper()
        
    def command_callback(self, msg: String):
        cmd = msg.data.strip().lower()

        self.get_logger().info(f"Received command: {cmd}")

        if cmd == "c":
            self.select_bell("handbell_c")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()

        elif cmd == "d":
            self.select_bell("handbell_d")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
            
        elif cmd == "e":
            self.select_bell("handbell_e")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
            
        elif cmd == "f":
            self.select_bell("handbell_f")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
            
        elif cmd == "g":
            self.select_bell("handbell_g")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
        
        elif cmd == "a":
            self.select_bell("handbell_a")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
        
        elif cmd == "b":
            self.select_bell("handbell_b")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()
            
        elif cmd == "cp":
            self.select_bell("handbell_cp")
            self.ready()
            self.approach()
            self.close_gripper()
            self.grasp()

        elif cmd == "roll1":
            self.roll()

        elif cmd == "roll2":
            self.roll()
            time.sleep(0.5)
            self.roll()
            
        elif cmd == "place":
            self.place()
            self.open_gripper()
            self.retreat()

        elif cmd == "home":
            self.open_gripper()
            self.home()

        elif cmd == "exit":
            self.open_gripper()
            self.home()
            rclpy.shutdown()

        else:
            self.get_logger().warn(f"Unknown command: {cmd}")
        
def main():
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
