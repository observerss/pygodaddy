.. pygodaddy documentation master file, created by
   sphinx-quickstart on Fri Jul 12 17:25:16 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pygodaddy's documentation!
=====================================

.. toctree::
   :maxdepth: 2

PyGoDaddy is a 3rd-party client library, written in Python, for site admins(devs), to make GoDaddy suck less. 

Currently, Only A-Record manipulation is supported

Install
-----------

To install pygodaddy, simply:

.. code-block:: bash
    
    pip install pygodaddy


Quick Start
-----------

Package Tastes below

.. code-block:: python

    from pygodaddy import GoDaddyClient
    client = GoDaddyClient()
    if client.login(username, password):
        print client.find_domains()
        client.update_dns_record('sub.example.com', '1.2.3.4')


API Documents
-------------

.. autoclass:: pygodaddy.GoDaddyClient
    :members:

.. autoclass:: pygodaddy.GoDaddyAccount
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

