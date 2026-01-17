#!/usr/bin/env python
"""Setup script for Ultrabot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ultrabot",
    version="1.0.0",
    author="Gaming News Aggregator Team",
    description="Production-ready Telegram gaming news aggregator bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kimakorr-gif/Ultrabot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Chat",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.2",
            "mypy>=1.7.0",
            "ruff>=0.1.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "ultrabot=src.main:main",
        ],
    },
)
