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
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pygodaddy',
    version = '0.2.2',
    description = '3rd Party Client Library for Manipulating Go Daddy DNS Records.',
    long_description=open('README.rst').read()+'\n\n'+open('HISTORY.rst').read(),
    url = 'https://github.com/observerss/pygodaddy',
    author = 'Jingchao Hu(observerss)',
    author_email = 'jingchaohu@gmail.com',
    packages = ['pygodaddy'],
    package_data={'': ['LICENSE']},
    package_dir = {'pygodaddy':'pygodaddy'},
    install_requires = ['requests>=1.2.3', 'tldextract>=1.5.1'],
    license = open('LICENSE').read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
