from setuptools import setup

package_name = 'drone_nav_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/drone_nav_py']),
    ('share/drone_nav_py', ['package.xml']),
    ('share/drone_nav_py/launch', ['launch/simulation_launch.py']),  
    ('share/drone_nav_py/meshes', ['meshes/quadrotor.dae']),
],
    install_requires=['setuptools'],
    zip_safe=True,
    description='Drone navigation package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'map_node = drone_nav_py.map_node:main',
            'path_node = drone_nav_py.path_node:main',
            'drone_node = drone_nav_py.drone_node:main',
            'obstacle_node = drone_nav_py.obstacle_node:main',
            'interactive_obstacle_node = drone_nav_py.interactive_obstacle_node:main',
        ],
    },
)
