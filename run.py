#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
import vobject
from urllib.parse import urljoin


def panic(msg):
    import sys
    logging.error(msg)
    sys.exit(1)


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-c', '--conf', required=True)
    return p.parse_args()


def load_conf(path):
    from configparser import ConfigParser
    c = ConfigParser()
    if not c.read(path):
        panic('unable to read from ' + path)
    return c


def fetch_vobjects(url, username, password):
    from requests.auth import HTTPBasicAuth
    import re
    headers = {'Content-Type': 'text/xml', 'Depth': '1'}
    data = '<propfind xmlns="DAV:"><prop><address-data xmlns="urn:ietf:params:xml:ns:carddav"/></prop></propfind>'
    try:
        r = requests.request('PROPFIND', url, auth=HTTPBasicAuth(username, password), headers=headers, data=data)
        if r.status_code != 207:
            panic('unexpected response from PROPFIND on ' + url)
        vcard_regex = re.compile(r'BEGIN:VCARD([\s\S]*?)END:VCARD', re.MULTILINE)
        vcards = []
        for match in vcard_regex.finditer(r.text):
            contents = match.group(0) \
                .replace('&#13;', '') \
                .replace('&quot;', '')
            vcards.append(vobject.readOne(contents))
        return vcards
    except Exception as e:
        panic(e)


def main():
    args = get_args()
    conf = load_conf(args.conf)
    vcards = fetch_vobjects(conf.get('carddav', 'url'), conf.get('carddav', 'user'), conf.get('carddav', 'pass'))
    print(len(vcards))


if __name__ == '__main__':
    main()
