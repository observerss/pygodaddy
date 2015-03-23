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

from collections import defaultdict, namedtuple

import requests
import logging
import re
import time
import tldextract

__all__  = ['LoginError', 'GoDaddyClient', 'GoDaddyAccount']

logger = logging.getLogger(__name__)

DNSRecord = namedtuple('DNSRecord', 'index, hostname, value, ttl, host_td, points_to, rec_modified')

class LoginError(Exception):
    pass

class GoDaddyAccount(object):
    """ This is a context manager for GoDaddyClient

    Usage:

    >>> from pygodaddy import GoDaddyAccount
    >>> with GoDaddyAccount(username, password) as client:
    ...    client.update_dns_record('sub1.exmaple.com', '1.2.3.4')
    ...    client.update_dns_record('sub2.exmaple.com', '1.2.3.5')
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        self.client = GoDaddyClient()
        if not self.client.login(self.username, self.password):
            # set client to `None`, force context manager to fail quickly
            self.client = None
        return self.client

    def __exit__(self, exec_type, exc_value, traceback):
        # suppress exceptions
        return True

class GoDaddyClient(object):
    """ GoDaddy Client Library

    Typical Usage:

    >>> from pygodaddy import GoDaddyClient
    >>> client = GoDaddyClient()
    >>> if client.login(username, password):
    ...     client.update_dns_record('sub.example.com', '1.2.3.4')
    """
    def __init__(self):
        self.logged_in = False
        self.default_url = 'https://dns.godaddy.com/default.aspx'
        self.zonefile_url = 'https://dns.godaddy.com/ZoneFile.aspx?zoneType=0&sa=&zone={domain}'
        self.zonefile_ws_url = 'https://dns.godaddy.com/ZoneFile_WS.asmx'
        self.session = requests.Session()
        self.sec=""

    def is_loggedin(self, html=None):
        """ Test login according to returned html, then set value to self.logged_in

        :param html: the html content returned by self.session.get/post
        :returns: `True` if there's welcome message, else `False`
        """
        if html is None:
            html = self.session.get(self.default_url).text
        self.logged_in = bool(re.compile(r'Welcome:&nbsp;<span id="ctl00_lblUser" .*?\>(.*)</span>').search(html))
        return self.logged_in


    def login(self, username, password):
        """ Login to a godaddy account

        :param username: godaddy username
        :param password: godaddy password
        :returns:  `True` if login is successful, else `False`
        """
        r = self.session.get(self.default_url)
        try:
            viewstate = re.compile(r'id="__VIEWSTATE" value="([^"]+)"').search(r.text).group(1)
        except:
            logger.exception('Login routine broken, godaddy may have updated their login mechanism')
            return False
        data = {
                'Login$userEntryPanel2$LoginImageButton.x' : 0,
                'Login$userEntryPanel2$LoginImageButton.y' : 0,
                'Login$userEntryPanel2$UsernameTextBox' : username,
                'Login$userEntryPanel2$PasswordTextBox' : password,
                '__VIEWSTATE': viewstate,
        }
        r = self.session.post(r.url, data=data)
        return self.is_loggedin(r.text)

    def find_domains(self):
        """ return all domains of user """
        html = self.session.get(self.default_url).text
        return re.compile(r'''GoToZoneEdit\('([^']+)''').findall(html)

    def find_dns_records(self, domain, record_type='A'):
        """ find all dns reocrds of a given domain

        :param domain: a typical domain name, e.g. "example.com"
        :returns: a dict of (hostname -> DNSRecord)
        """
        html = self.session.get(self.zonefile_url.format(domain=domain)).text

        #Update the security token while we're at it.
        sec_pattern = 'nonce=\"([0-9A-Za-z]+)\"'
        self.sec = re.compile(sec_pattern).findall(html)[0]

        pattern = "Undo{rt}Edit\\('tbl{rt}Records_([0-9]+)', '([^']+)', '([^']+)', '([^']+)', '([^']+)', '([^']+)', '([^']+)'\\)".format(rt=record_type)
        try:
            results = map(DNSRecord._make, re.compile(pattern).findall(html))
        except:
            logger.exception('find domains broken, maybe godaddy has changed its web structure')
            return []
        return results

    def update_dns_record(self, hostname, value, record_type='A', new=True):
        """ Update a dns record

        :param hostname: hostname to update
        :param value: value for hostname to point to, for A record, it's like 'XX.XX.XX.XX'
        :param record_type: only 'A' is implemented for now
        :param new: if `True`, will create a new record if necessary, default to `True`
        :returns: `True` if update is successful, else `False`
        """
        if record_type != 'A':
            raise NotImplementedError('Only A Record Update is supported for now')

        prefix, domain = self._split_hostname(hostname)

        records = list(self.find_dns_records(domain, record_type))
        for record in records:
            if record.hostname == prefix:
                if record.value != value:
                    if not self._edit_record(value=value, index=record.index, record_type=record_type):
                        return False
                    time.sleep(1) # godaddy seems to reject the save if there isn't a pause here
                    if not self._save_records(domain=domain, index=record.index, record_type=record_type):
                        return False
                    return True
                logger.info('Update was not required.')
                break
        else:
            # record.hostname == prefix not found
            if new:
                # let's create a new record
                index = int(records[-1].index)+1 if records else 0

                if not self._add_record(prefix=prefix, value=value, index=index, record_type=record_type):
                    return False
                time.sleep(1)# godaddy seems to reject the save if there isn't a pause here
                if not self._save_records(domain=domain, index=index, record_type=record_type):
                    return False
                return True

        return False

    def delete_dns_record(self, hostname, record_type='A'):
        """ delete hostname in accounts

        :param hostname: hostname to be deleted
        :param record_type: only 'A' is implemented for now
        :returns: `True` if successful, else `False`
        """
        if record_type != 'A':
            raise NotImplementedError('Only A Record Update is supported for now')

        prefix, domain = self._split_hostname(hostname)

        for record in self.find_dns_records(domain, record_type):
            if record.hostname == prefix:
                if not self._delete_record(record.index, record_type=record_type):
                    return False
                time.sleep(1)# godaddy seems to reject the save if there isn't a pause here
                if not self._save_records(domain=domain, index=record.index, record_type=record_type):
                    return False
                return True

        return False

    def _split_hostname(self, hostname):
        """ split hostname into prefix + domain """
        ext = tldextract.extract(hostname)
        prefix = ext.subdomain
        domain = ext.registered_domain
        if not prefix:
            prefix = '@'
        return prefix, domain

    def _delete_record(self, index, record_type='A'):
        """ delete old record, return `True` if successful """
        data = {'sInput':"{index}|true".format(index=index)}
        r = self.session.post(self.zonefile_ws_url + '/Flag{rt}RecForDeletion'.format(rt=record_type), data=data)
        if not 'SUCCESS' in r.text:
            logger.error('Failed to delete record, has the website changed?')
            return False
        return True

    def _add_record(self, prefix, value, index, record_type='A'):
        """ add new record, return `True` if successful """
        data = {'sInput':'<PARAMS><PARAM name="lstIndex" value="{index}" /><PARAM name="host" value="{prefix}" /><PARAM name="pointsTo" value="{value}" /><PARAM name="ttl" value="600" /></PARAMS>'.format(index=index, prefix=prefix, value=value)}
        r = self.session.post(self.zonefile_ws_url + '/AddNew{rt}Record'.format(rt=record_type), data=data)
        if not 'SUCCESS' in r.text:
            logger.error('Failed to add record, has the website changed?')
            return False
        return True

    def _edit_record(self, index, value, record_type='A'):
        """ set value of record on `index` to `value`, return `True` if successful """
        data = {'sInput' : '<PARAMS><PARAM name="type" value="{rt}record" /><PARAM name="fieldName" value="data" /><PARAM name="fieldValue" value="{value}" /><PARAM name="lstIndex" value="{index}" /></PARAMS>'.format(value=value, index=index, rt=record_type.lower())}
        r = self.session.post(self.zonefile_ws_url + '/EditRecordField', data=data)
        if not 'SUCCESS' in r.text:
            logger.error('Failed to edit record, has the website changed?')
            return False
        return True

    def _save_records(self, domain, index, record_type='A'):
        """ save edit of `index` of `domain` """
        string = ('<PARAMS>'
                  '<PARAM name="domainName" value="{domain}" />'
                  '<PARAM name="zoneType" value="0" />'
                  '<PARAM name="aRecEditCount" value="1" />'
                  '<PARAM name="aRecEdit0Index" value="{index}" />'
                  '<PARAM name="nonce" value="{nonce}" />'
                  '</PARAMS>')

        string=string.format(domain=domain, index=index,nonce=self.sec)
        data = {'sInput' : string}
        r = self.session.post(self.zonefile_ws_url + '/SaveRecords', data=data)
        if not 'SUCCESS' in r.text:
            logger.error('Failed to save records, has the website changed?')
            return False
        return True

