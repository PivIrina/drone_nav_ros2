from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_nav_py',
            executable='map_node',
            name='map_node',
            parameters=[{
                'map_min_x': 0.0,
                'map_min_y': 0.0,
                'map_max_x': 50.0,
                'map_max_y': 50.0
            }]
        ),

        Node(
            package='drone_nav_py',
            executable='path_node',
            name='path_node',
            parameters=[{
                'map_min_x': 0.0,
                'map_min_y': 0.0,
                'map_max_x': 50.0,
                'map_max_y': 50.0,
                'goal_x': 10.0,
                'goal_y': 10.0,
                'step': 0.5
            }]
        ),
        Node(
            package='drone_nav_py',
            executable='drone_node',
            name='drone_node',
            parameters=[{
                'speed': 5.0
            }]
        ),
        Node(
            package='drone_nav_py',
            executable='obstacle_node',
            name='obstacle_node',
            parameters=[{
                'map_min_x': 0.0,
                'map_min_y': 0.0,
                'map_max_x': 50.0,
                'map_max_y': 50.0
            }]
        ),

        Node(
            package='drone_nav_py',
            executable='interactive_obstacle_node',
            name='interactive_obstacle_node'
        )
    ])