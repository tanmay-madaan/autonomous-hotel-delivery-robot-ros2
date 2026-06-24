from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    use_rviz = LaunchConfiguration('use_rviz')
    use_teleop = LaunchConfiguration('use_teleop')

    pkg_hotel_launch = FindPackageShare('hotel_launch')
    pkg_nav2_bringup = FindPackageShare('nav2_bringup')
    pkg_slam_toolbox = FindPackageShare('slam_toolbox')

    default_slam_params = PathJoinSubstitution(
        [pkg_hotel_launch, 'config', 'nav2_slam_params.yaml']
    )
    default_rviz_config = PathJoinSubstitution(
        [pkg_slam_toolbox, 'config', 'slam_toolbox_default.rviz']
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock from Gazebo',
    )

    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_slam_params,
        description='Nav2 / slam_toolbox parameter file',
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz with the slam_toolbox view',
    )

    declare_use_teleop = DeclareLaunchArgument(
        'use_teleop',
        default_value='true',
        description='Launch keyboard teleop on /cmd_vel',
    )

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_hotel_launch, 'launch', 'diff_drive_example.launch.py'])
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_nav2_bringup, 'launch', 'slam_launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': slam_params_file,
        }.items(),
    )

    teleop_hint = LogInfo(
        msg=(
            'Drive the robot in a separate terminal:\n'
            '  source ~/ros2_ws/install/setup.bash\n'
            '  ros2 run teleop_twist_keyboard teleop_twist_keyboard '
            '--ros-args -r cmd_vel:=cmd_vel_unstamped\n'
            'Keys: i=forward  ,=back  j=left  l=right  k=stop  q=quit'
        ),
    )

    twist_stamper_node = Node(
        package='hotel_launch',
        executable='twist_stamper',
        name='twist_stamper',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    teleop_terminal = ExecuteProcess(
        condition=IfCondition(use_teleop),
        cmd=[
            'gnome-terminal',
            '--title=Hotel Robot Teleop',
            '--',
            'bash',
            '-c',
            (
                'source ~/ros2_ws/install/setup.bash 2>/dev/null || '
                'source /opt/ros/jazzy/setup.bash; '
                'echo; echo "Hotel teleop - click this window first"; '
                'echo "i=forward  ,=back  j=left  l=right  k=stop  q=quit"; '
                'echo; '
                'ros2 run teleop_twist_keyboard teleop_twist_keyboard '
                '--ros-args -r cmd_vel:=cmd_vel_unstamped; '
                'echo; read -p "Press Enter to close..."'
            ),
        ],
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params_file,
        declare_use_rviz,
        declare_use_teleop,
        teleop_hint,
        sim_launch,
        twist_stamper_node,
        slam_launch,
        teleop_terminal,
        rviz_node,
    ])
