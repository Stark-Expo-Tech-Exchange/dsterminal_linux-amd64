from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Filter out comments and empty lines
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name='dsterminal',
<<<<<<< HEAD
    version='4.0.0.113',
=======
    version='2.1.0',
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    description='Defensive Security Terminal - Advanced security auditing and monitoring tool',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Spark Wilson Spink',
    author_email='your-email@example.com',
    url='https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators - Government institutions',
        'License :: OSI Approved :: MIT License & Stark Expo Tech Exchange LTD',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Security',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'dsterminal=dsterminal:main',
        ],
    },
    include_package_data=True,
    keywords='security, dsterminal, monitoring, defensive, terminal, audit, forensics',
)