pygodaddy
==========

3rd Party Client Library for Manipulating Go Daddy DNS Records.

Currently, Only A Records Manipulation is supported

INSTALL
-------
TBD


QUICKSTART
----------

```python
from pygodaddy import GoDaddyClient
client = GoDaddyClient()
if client.login(username, password):
    print client.find_domains()
    client.update_dns_record('sub.example.com', '1.2.3.4')
```

DOCS
----

Please refer to docstrings and tests


TESTING
-------

Create a file in `tests/accounts.py`

Put settings in this file
 
```python 
accounts = [
    {
        'username': 'USERNAME',
        'password': 'PASSWORD',
        'test_domain': 'DOMAIN.NAME',
    },
]
```

run `nosetests tests` in root directory
