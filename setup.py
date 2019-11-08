from setuptools import setup, find_packages

setup(
    name='pyhumio',
    version='0.0.3',
    author='Nathan Kuik',
    author_email='naku0510@dsb.dk',
    packages=find_packages(),
    description="Log to Humio from python's default logger",
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests'
    ]
)