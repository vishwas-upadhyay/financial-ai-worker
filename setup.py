"""
Setup script for Financial AI Worker
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="financial-ai-worker",
    version="1.0.0",
    author="Financial AI Worker Team",
    author_email="contact@financialaiworker.com",
    description="A comprehensive investment portfolio analysis and tracking system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/financial-ai-worker/financial-ai-worker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "financial-ai-worker=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json"],
    },
)

