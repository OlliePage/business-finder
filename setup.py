# File: setup.py
from setuptools import setup, find_packages

setup(
    name="business_finder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "business-finder=business_finder.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for finding and exporting business data using Google Maps API",
    keywords="google, maps, business, search",
    url="https://github.com/yourusername/business-finder",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)