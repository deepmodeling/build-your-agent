#!/usr/bin/env python3
"""
PubChem MCP Server Installation Script
"""

from setuptools import setup, find_packages

setup(
    name="pubchem-mcp-server",
    version="1.0.0",
    description="PubChem MCP Server - Provides PubChem compound data retrieval functionality",
    author="PubChem MCP Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "rdkit": ["rdkit>=2022.9.1"],
    },
    entry_points={
        "console_scripts": [
            "pubchem-mcp=pubchem_mcp_server.cli:main",
            "pubchem-mcp-server=pubchem_mcp_server.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.8",
)
