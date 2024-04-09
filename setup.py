import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("pytolnet/__init__.py", "r") as fh:
    for ll in fh:
        if ll.startswith('__version__'):
            exec(ll)
            break
    else:
        __version__ = 'x.y.z'

setuptools.setup(
    name="pytolnet",
    version=__version__,
    author="Barron H. Henderson",
    author_email="barronh@gmail.com",
    description="Python interface to TOLNet Web API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barronh/pytolnet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests", "numpy", "matplotlib", "netcdf4", "pandas", "xarray"
    ],
)
