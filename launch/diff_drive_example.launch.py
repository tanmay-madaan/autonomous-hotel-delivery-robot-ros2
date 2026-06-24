from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def robot_state_publisher(context):

    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [
                    FindPackageShare('hotel_launch'),
                    'urdf',
                    'test_diff_drive.xacro.urdf'
                ]
            )
        ]
    )

    robot_description = {
        'robot_description': ParameterValue(
            robot_description_content,
            value_type=str
        )
    }

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    return [node_robot_state_publisher]


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare('hotel_launch'),
            'config',
            'diff_drive_controller.yaml',
        ]
    )

    ros_gz_bridge_config = PathJoinSubstitution(
        [
            FindPackageShare('hotel_launch'),
            'config',
            'ros_gz_bridge.yaml',
        ]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'diff_drive',
            '-allow_renaming',
            'true'
        ]
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster']
    )

    diff_drive_base_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_base_controller',
            '--param-file',
            robot_controllers
        ]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': ros_gz_bridge_config,
            'use_sim_time': use_sim_time,
        }],
        output='screen'
    )

    ld = LaunchDescription()

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [
                    PathJoinSubstitution(
                        [
                            FindPackageShare('ros_gz_sim'),
                            'launch',
                            'gz_sim.launch.py'
                        ]
                    )
                ]
            ),
            launch_arguments={
                'gz_args': '-r -v 1 /home/tanmay/hotel_world.sdf'
            }.items()
        )
    )

    ld.add_action(bridge)
    ld.add_action(gz_spawn_entity)

    ld.add_action(
        RegisterEventHandler(
            OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[
                    TimerAction(
                        period=5.0,
                        actions=[joint_state_broadcaster_spawner],
                    )
                ]
            )
        )
    )

    ld.add_action(
        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_base_controller_spawner]
            )
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='Use simulation time'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            'description_format',
            default_value='urdf',
            description='Robot description format'
        )
    )

    ld.add_action(OpaqueFunction(function=robot_state_publisher))

    return ld
