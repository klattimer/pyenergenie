from setuptools import setup
import setuptools

PYENERGENIE_VERSION = '0.9'
PYENERGENIE_DOWNLOAD_URL = (
    'https://github.com/klattimer/pyenergenie/tarball/' + PYENERGENIE_VERSION
)

setup(
    name='pyenergenie',
    packages=setuptools.find_packages(),
    version=PYENERGENIE_VERSION,
    description='Energinie interface in python.',
    long_description='',
    license='MIT',
    author='Karl Lattimer',
    author_email='karl@qdh.org.uk',
    url='https://github.com/klattimer/pyenergenie',
    download_url=PYENERGENIE_DOWNLOAD_URL,
    entry_points={
        'console_scripts': [
            'pyenergenie=energenie:main'
        ]
    },
    keywords=[
        'smarthome', 'energenie', 'trv', 'relay', 'sensor', 'remote'
    ],
    install_requires=[
        'paho-mqtt',
        'websockets',
        'flask'
        # 'requests',
        # 'ws4py'
        # 'wakeonlan',
    ],
    data_files=[
        ('energenie/drv', ['energenie/drv/radio_rpi.so'])
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
    ],
)
