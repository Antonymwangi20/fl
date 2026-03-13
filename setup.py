#!/usr/bin/env python3
"""
Setup script for fl - Python project management tool
Enables installation via: pip install .
Or publishing to PyPI: python setup.py sdist bdist_wheel
"""

from setuptools import setup
import os

# Read the long description from README
script_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(script_dir, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = 'Python project management without friction'

setup(
    name='fl-tool',
    version='1.0.0',
    description='Python project management without the friction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Antony Mwangi',
    author_email='antony254mm@gmail.com',
    url='https://github.com/Antonymwangi20/fl',
    license='MIT',
    
    # The main script
    py_modules=[],
    scripts=['fl'],
    
    python_requires='>=3.8',
    
    # No external dependencies - uses stdlib only!
    install_requires=[],
    
    # Make entry point for easier invocation
    entry_points={
        'console_scripts': [
            'fl=fl:main',  # This allows `fl` command if installed via pip
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
    ],
    
    keywords='python project management venv dependencies packaging',
    
    project_urls={
        'Documentation': 'https://github.com/Antonymwangi20/fl#readme',
        'Source': 'https://github.com/Antonymwangi20/fl',
        'Tracker': 'https://github.com/Antonymwangi20/fl/issues',
    },
)
