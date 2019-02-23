from distutils.core import setup
import setuptools 

setup(
    name='TypeNet',
    version='0.1.0',
    author='Matth Ingersoll',
    author_email='matth@mtingers.com',
    packages=['typenet',],
    license='BSD 2-Clause License',
    long_description=open('README.md').read(),
    url='https://github.com/mtingers/typenet',
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': ['typenet-server=typenet.cli_server:main',],
    },
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

