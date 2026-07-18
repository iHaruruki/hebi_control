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
            executable='hebi_arm_mover1',
            name='hebi_arm_mover1',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_arm_mover2',
            name='hebi_arm_mover2',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_arm_mover3',
            name='hebi_arm_mover3',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_j6_rotator1',
            name='hebi_j6_rotator1',
            output='screen',
            parameters=joint_parameters
        ),
          
        Node(
            package=package_name,
            executable='hebi_j6_rotator2',
            name='hebi_j6_rotator2',
            output='screen',
            parameters=joint_parameters
        ),
        
        Node(
            package=package_name,
            executable='hebi_j6_rotatorno',
            name='hebi_j6_rotatorno',
            output='screen',
            parameters=joint_parameters
        ),        
        
        Node(
            package=package_name,
            executable='hebi_home_position',
            name='hebi_home_position',
            output='screen',
            parameters=joint_parameters
        ), 
              
        Node(
            package='hebi_control',
            executable='hebi_mover',
            name='hebi_sequence_manager',
            output='screen',
            emulate_tty=True,
        ),
    ])
