from setuptools import setup

setup(
    name = 'mplstereonet',
    version = '0.2',
    description = "Stereonets for matplotlib",
    author = 'Joe Kington',
    author_email = 'joferkington@gmail.com',
    license = 'LICENSE',
    url = 'https://github.com/joferkington/mplstereonet/',
    packages = ['mplstereonet'],
    install_requires = [
        'matplotlib >= 0.98',
        'numpy >= 1.1']
)
