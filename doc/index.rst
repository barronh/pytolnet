.. pytolnet documentation master file, created by
   sphinx-quickstart on Fri Mar 17 21:46:43 2023.

pytolnet User's Guide
=====================

`pytolnet` is a python tool to work with TOLNet's API

The key value of `pytolnet` is to provide a python interface that returns
pandas.DataFrame and xarray.Dataset objects. DataFrames and Dasasets have
great built-in support for analytics and plotting. This should make analysis
easy and *fun*.

Getting Started
---------------

The best way to get started is to install (see below) and then explore the
:doc:`auto_examples/index`. The examples include data download, processing,
and create summaries of the data (figures and tables).


Installation
------------

Right now, you can get the latest version of `pytolnet` with this command.

.. code-block::

    pip install git+https://github.com/barronh/pytolnet.git


Issues
------

If you're having any problems, open an issue on github.

https://github.com/barronh/pytolnet/issues


Quick Links
-----------

* :doc:`auto_examples/index`
* :doc:`api/pytolnet`


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Table of Contents

   self
   auto_examples/index
   api/pytolnet
   api/modules
