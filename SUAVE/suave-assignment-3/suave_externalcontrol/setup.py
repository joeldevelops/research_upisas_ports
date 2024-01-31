import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'suave_externalcontrol'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*launch.[pxy][yma]*')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='FAS Team',
    maintainer_email='nonexistent-fas-team-mail@vu.nl',
    description='An HTTP server with a node for remote monitoring and adaptation',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'suave_externalcontrol = ' +
                ' suave_externalcontrol.http_server:main',
        ],
    },
)
