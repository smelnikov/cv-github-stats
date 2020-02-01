#!/usr/bin/env python
import io

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with io.open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='ghstats',
    version='0.1.0',
    description='Simple GitHub stats interface',
    long_description=readme,
    author='S Melnikov',
    author_email='asmelnikovse@gmail.com',
    url='https://github.com/smelnikov/cv-github-stats',
    packages=[
        'ghstats',
        'ghstats.api'
    ],
    package_dir={
        'ghstats': 'ghstats',
        'ghstats.api': 'ghstats/api',
    },
    include_package_data=True,
    install_requires=[],
    license='MIT',
    zip_safe=False,
    keywords='ghstats',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'ghstats = ghstats.__main__:main'
        ]
    }
)