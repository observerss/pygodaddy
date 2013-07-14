pygodaddy
==========

.. image:: https://travis-ci.org/observerss/pygodaddy.png?branch=master
        :target: https://travis-ci.org/observerss/pygodaddy


PyGoDaddy is a 3rd-party client library, written in Python, for site admins(devs), to make GoDaddy suck less. 

Currently, Only A-Record manipulation is supported

Features
--------

- Login with a USERNAME and a PASSWORD
- CREATE, READ, UPDATE, DELETE your domain's DNS Records (A-Record only for now)

INSTALL
-------

To install pygodaddy, simply:

.. code-block:: bash
    
    pip install pygodaddy


QUICKSTART
----------

.. code-block:: python

    from pygodaddy import GoDaddyClient
    client = GoDaddyClient()
    if client.login(username, password):
        print client.find_domains()
        client.update_dns_record('sub.example.com', '1.2.3.4')

DOCS
----

https://pygodaddy.readthedocs.org/

Or you can always refer to ``docstrings`` and ``tests``


TESTING
-------

Create a file in `tests/accounts.py`

Put settings in this file::
 
    accounts = [
        {
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'test_domain': 'DOMAIN.NAME',
        },
    ]

run `nosetests tests` in root directory
