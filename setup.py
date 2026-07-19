from setuptools import find_packages, setup

package_name = 'my_robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'my_robot_description/launch/view_my_robot.xml',
            'my_robot_description/launch/view_my_robot.launch.py',
        ]),
        ('share/' + package_name + '/robot_description', ['my_robot_description/robot_description/my_robot_description.xacro']),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xing',
    maintainer_email='xing@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
