from setuptools import setup

setup(
    name = 'mplstereonet',
    version = '0.1',
    description = "Stereonets for matplotlib",
    author = 'Joe Kington',
    author_email = 'joferkington@gmail.com',
    license = 'MIT',
    url = 'http://code.google.com/p/python-geoprobe/',
    packages = ['mplstereonet'],
    package_data = {'mplstereonet' : ['__init__.py', 'stereonet_axes.py',
                                      'stereonet_math.py']}
)
