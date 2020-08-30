import os
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
py_version = sys.version_info[:2]
if py_version < (3, 5):
    raise Exception("flac2mp3 requires Python >= 3.5.")

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()

NAME = 'flac2mp3'

install_requires = [
    'argparse==1.4.0'
]

tests_require = [
    'nose==1.3.7',
    'eyeD3==0.9.5',
    'bumpversion==0.5.3'
]

setup(
    name=NAME,
    version='0.7.0',
    description='Python flac2mp3 transcoding script',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    author='Bruno Thomas',
    author_email='bruno@barreverte.fr',
    license='MIT',
    url='https://github.com/bamthomas/flac2mp3',
    keywords='transcoding mp3 lame flac',
    packages=['flac2mp3'],
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=install_requires,
    extras_require={
        'dev': tests_require,
    },
    entry_points={
          'console_scripts': [
              'flac2mp3 = flac2mp3.__init__:main'
          ]
    },
)
