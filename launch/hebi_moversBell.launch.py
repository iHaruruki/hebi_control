from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():

    package_name = "hebi_a-2085-06g_moveit_config"
    print(package_name)
    
    moveit_config = MoveItConfigsBuilder("hebi_a-2085-06g", package_name="hebi_a-2085-06g_moveit_config").to_moveit_configs()
    
    joint_parameters = [moveit_config.to_dict()]
    
    joint_parameters.append({'use_sim_time': False})
    
    return LaunchDescription([

        Node(
            package=package_name,
            executable='hebi_bell_home',
            name='hebi_bell_home',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_ready',
            name='hebi_bell_ready',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_approach',
            name='hebi_bell_approach',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_grasp',
            name='hebi_bell_grasp',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_roll',
            name='hebi_bell_roll',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_place',
            name='hebi_bell_place',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_bell_retreat',
            name='hebi_bell_retreat',
            parameters=joint_parameters
        ),
        
        Node(
            package='hebi_control',
            executable='hebi_moverBell',
            name='hebi_sequence_manager',
            output='screen',
            emulate_tty=True,
        )
    ])
