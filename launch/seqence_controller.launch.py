from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Generate launch description for sequence controller."""
    
    # Declare launch arguments
    verbose_arg = DeclareLaunchArgument(
        'verbose',
        default_value='true',
        description='Enable verbose logging'
    )
    
    return LaunchDescription([
        verbose_arg,
        Node(
            package='hebi_control',
            executable='hebi_seqence',
            name='hebi_seqence',
            output='screen',
            parameters=[
                {'verbose': LaunchConfiguration('verbose')},
            ],
        ),
    ])
