import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'hebi_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='YOUR_EMAIL',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [ 
        	'hebi_mover = hebi_control.hebi_mover:main',
        	'hebi_mover2 = hebi_control.hebi_mover2:main',
        	'hebi_moverU = hebi_control.hebi_moverU:main', 
        	'hebi_moverK = hebi_control.hebi_moverK:main', 
        	'hebi_moverBell = hebi_control.hebi_moverBell:main', 
        	'hebi_seqence = hebi_control.seqence_controller:main',
        ],
    },
)
