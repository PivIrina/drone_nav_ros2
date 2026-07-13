
from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'drone_nav_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
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
