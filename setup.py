from setuptools import setup, find_packages
import os

def main():

    setup(
        name='PyDsJulabo',
        packages= find_packages(),
        version = '1.2.1',    
        long_description='The device server is intended to contro the Julabo Cryo-Compact Circulator.\n It can manage Cf and FC series',
        url='http://www.cells.es',
        author='CTBeamlines',
        author_email='ctbeamlines@cells.es',
        description='This package contains Julabo DS',
        platforms = "all",        
        include_package_data = True,
    
    # Define automatic scripts tht will be created during installation.
    entry_points={
        'console_scripts': [
                            'PyDsJulabo = PyDsJulabo.PyDsJulabo:main',
                        ],
        }
    )
if __name__ == "__main__":
    main()
