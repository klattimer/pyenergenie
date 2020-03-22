from setuptools import setup

PYENERGENIE_VERSION = '0.2'
PYENERGENIE_DOWNLOAD_URL = (
    'https://github.com/klattimer/pyenergenie/tarball/' + PYENERGENIE_VERSION
)

setup(
    name='pyenergenie',
    packages=['energenie'],
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
        # 'wakeonlan',
        # 'ws4py',
        # 'requests'
    ],
    data_files=[
        ('config', ['data/config.json'],
         'energenie/drv', ['energenie/drv/radio_rpi.so']')
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
    ],
)
