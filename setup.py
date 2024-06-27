from setuptools import setup, find_packages

setup(
    name='roapi',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'roapi-cli = roapi.cli:main',
        ],
    },
    author='0kan12',
    author_email='',
    description='A Python library to simplify interacting with Roblox APIs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/0kan12/roapi',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
