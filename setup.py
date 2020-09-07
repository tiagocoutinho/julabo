# -*- coding: utf-8 -*-

"""The setup script."""

import sys
from setuptools import setup, find_packages

requirements = ["pyserial", "sockio>=0.10", "serialio>=2"]

with open("README.md") as f:
    description = f.read()

setup(
    name="julabo",
    author="Tiago Coutinho",
    author_email="tcoutinho@cells.es",
    version="2.2.0",
    description="julabo library",
    long_description=description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "Julabo = julabo.tango.server:main [tango]",
        ]
    },
    install_requires=requirements,
    extras_require={
        "tango": ["pytango"],
        "simulator": ["sinstruments>=1"]
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
    ],
    license="LGPLv3",
    include_package_data=True,
    keywords="julabo, library, tango",
    packages=find_packages(),
    url="https://github.com/tiagocoutinho/julabo",
    project_urls={
        "Documentation": "https://github.com/tiagocoutinho/julabo",
        "Source": "https://github.com/tiagocoutinho/julabo"
    }
)
