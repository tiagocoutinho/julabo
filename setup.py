# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = ["pyserial", "sockio>=0.10", "serialio>=2"]

with open("README.md") as f:
    description = f.read()

extras_require={
    "tango": ["pytango"],
    "simulator": ["sinstruments>=1.3"]
}

extras_require["all"] = list(
    {pkg for pkgs in extras_require.values() for pkg in pkgs}
)

setup(
    name="julabo",
    author="Tiago Coutinho",
    author_email="tcoutinho@cells.es",
    version="2.3.0",
    description="julabo library",
    long_description=description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "Julabo = julabo.tango.server:main [tango]",
        ],
        'sinstruments.device': [
            'JulaboCF = julabo.simulator:JulaboCF [simulator]',
            'JulaboHL = julabo.simulator:JulaboHL [simulator]'
        ]
    },
    install_requires=requirements,
    extras_require=extras_require,
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
