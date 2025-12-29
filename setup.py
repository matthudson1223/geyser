#!/usr/bin/env python3
"""Setup script for Geyser - Equity Research Report Generator."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="geyser",
    version="1.0.0",
    author="Geyser Contributors",
    description="Comprehensive Python tool for generating institutional-quality equity research reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthudson1223/geyser",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "geyser=run_analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
