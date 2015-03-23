############################################################################
#   Copyright 2013 observerss
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
############################################################################
#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .accounts import accounts
except:
    # no accounts avaible, quit testing
    exit(0)

import random
account = random.choice(accounts)

from nose import with_setup
from pygodaddy import GoDaddyClient, GoDaddyAccount

client = None

def test_login():
    global client
    if client is None:
        client = GoDaddyClient()
    assert client.login(account['username'], account['password']), 'Login Failed'

def test_can_find_target_domain():
    global client
    if client is None:
        client = GoDaddyClient()
    assert account['test_domain'] in client.find_domains(), 'domain not found'

def test_can_update_dns_record():
    global client
    if client is None:
        client = GoDaddyClient()
    domain = account['test_domain']
    prefix = 'test{}'.format(random.randint(10000, 99999))
    addr = '{}.{}.{}.{}'.format(random.randint(10, 20), random.randint(10, 20),
                                random.randint(10, 20), random.randint(10, 20))
    addr2 = '{}.{}.{}.{}'.format(random.randint(20, 30), random.randint(20, 30), \
                                random.randint(20, 30), random.randint(20, 30))
    # can create new record
    assert client.update_dns_record(prefix+'.'+domain, addr), 'Create DNS Failed'
    for record in client.find_dns_records(domain):
        if record.hostname == prefix:
            assert record.value == addr, 'DNS Record Doesnot Match Addr {}'.format(addr)
            break
    else:
        raise ValueError('DNS Record Cannot Created')

    # can update previous record
    assert client.update_dns_record(prefix+'.'+domain, addr2), 'Update DNS Failed'
    for record in client.find_dns_records(domain):
        if record.hostname == prefix:
            assert record.value == addr2, 'DNS Record Doesnot Match Addr2 {}'.format(addr2)
            break

    # can delete dns record
    assert client.delete_dns_record(prefix+'.'+domain), 'Delete DNS Failed'
    for record in client.find_dns_records(domain):
        if record.hostname == prefix:
            raise ValueError('DNS Record still exists')
