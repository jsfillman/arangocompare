from setuptools import setup, find_packages

setup(
    name='arango_compare',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'arango_compare=arango_compare.arango_compare:main',
        ],
    },
)
