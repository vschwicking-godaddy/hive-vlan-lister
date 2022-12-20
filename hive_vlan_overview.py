#!/usr/bin/env python

import sys
import re
import requests
from requests.auth import HTTPBasicAuth
from os import getenv
import argparse
from prettytable import PrettyTable


API_URL = "https://api.hive{0}.mass.systems/{0}/bridge-domain-vlans/vlans=0/bulk"
API_USER = getenv('API_USER')
API_PASSWORD = getenv('API_PASSWORD')
HIVES = [
    205, 206, 207,
    208, 210, 211,
    213, 215, 216,
    217, 220, 232,
    233, 301, 403,
    800, 802, 803,
    804, 805, 806
]


class ArgParser(object):
    def __init__(self):
        self.main_parser = argparse.ArgumentParser()
        self.addArgs()
        self.verbose = False

    def addArgs(self):
        self.main_parser.add_argument(
            '-s',
            '--sort-by',
            default='vlan_name',
            required=False,
            dest='sort_by',
            help='Sort result by "vlan_id" or "vlan_name" (default: vlan_name)'
        )

        self.main_parser.add_argument(
            '-i',
            '--hive-id',
            type=str,
            default='205',
            dest='hive_id',
            help='The hive to query, supports "all" for all hives and "210,213" for a subset of hives (default: 205)'
        )

    def parseArgs(self):
        return self.main_parser.parse_args()


def http_request(url=None, user=None, passwd=None, hive_id=None):
    '''
    Helper function to run http-requests
    '''
    header = {'X-Requested-Hive': f"hive{hive_id}"}
    auth = HTTPBasicAuth(user, passwd)
    try:
        data = requests.get(
            url=url,
            verify=True,
            timeout=30,
            headers=header,
            auth=auth
        )
    # except all requests-exceptions, HTTPError, HTTPTimeout, etc.
    except requests.exceptions.RequestException as api_exec:
        raise requests.exceptions.RequestException(
            'Failed to execute request:', str(api_exec))

    if data.status_code != 200:
        raise requests.exceptions.RequestException(
            'Request failed: {0}'.format(data)
        )
    else:
        return (data.text, data.status_code)


def fetch_data(hive_id=None, sort_by='vlan_name'):
    print(f"Fetching VLANs from hive{hive_id}")

    data = http_request(
        url=API_URL.format(hive_id),
        user=API_USER,
        passwd=API_PASSWORD,
        hive_id=hive_id
    )

    vlan_data = {}

    for line in data[0].split('\n'):
        if len(line.strip()) <= 0:
            continue

        # We need to parse lines like this
        # INSERT INTO lookup VALUES ('4000','SXB1-S4Y-4000','10.213.1.25','L24.r3-2.sxb1','EX3300-48T-BF','juniper','GF0212014822','12.3R11.2');

        # Get rid of the leading INSERTY INTO...
        parsed_line = re.match(
            '^INSERT INTO lookup VALUES (.*)$', line).groups()[0]

        # ('4000','SXB1-S4Y-4000','10.213.1.25','L24.r3-2.sxb1','EX3300-48T-BF','juniper','GF0212014822','12.3R11.2');
        # strip semikolon and braces from string
        parsed_line = parsed_line.strip(';')
        parsed_line = parsed_line.strip('()')

        # '4000','SXB1-S4Y-4000','10.213.1.25','L24.r3-2.sxb1','EX3300-48T-BF','juniper','GF0212014822','12.3R11.2'
        fields = parsed_line.split(',')

        # ["'4000'","'SXB1-S4Y-4000'","'10.213.1.25'","'L24.r3-2.sxb1'","'EX3300-48T-BF'","'juniper'","'GF0212014822'","'12.3R11.2'"]
        # strip ' from strings in list
        fields = [f.strip("'") for f in fields]

        # we should have a a workable list like this now
        # ["4000","SXB1-S4Y-4000","10.213.1.25","L24.r3-2.sxb1","EX3300-48T-BF","juniper","GF0212014822","12.3R11.2"]

        # Just add all vlans by name as key with vlanid as values
        if sort_by == 'vlan_name':
            vlan_data[fields[1]] = []
            vlan_data[fields[1]].append(int(fields[0]))

        # Add vlanid as key with vlan names as values
        elif sort_by == 'vlan_id':
            # only create new vlan list if it does not yet exist
            if fields[0] in vlan_data:
                # vlan already exists, dont add same vlan name multiple times
                if fields[1] not in vlan_data[fields[0]]:
                    vlan_data[fields[0]].append(fields[1])
            else:
                vlan_data[fields[0]] = []
                vlan_data[fields[0]].append(fields[1])
        else:
            print("No idea what to sort by")
            sys.exit(1)

    return vlan_data


if __name__ == '__main__':
    args = vars(ArgParser().parseArgs())
    print(args)
    hive_id = args['hive_id']

    # collects all vlan_data fetched from hives
    all_vlans = {}

    # Check if we have a single hive_id
    if re.match('^[0-9]+$', hive_id):
        hive_data = fetch_data(hive_id, sort_by=args['sort_by'])
        all_vlans.update({hive_id: hive_data})
    # Check if we should query all hives
    elif hive_id == 'all':
        for hive in HIVES:
            hive_data = fetch_data(hive, sort_by=args['sort_by'])
            all_vlans.update({hive: hive_data})
    # Check for a comma separated subset of hives
    elif ',' in hive_id:
        HIVES = hive_id.split(',')
        for hive in HIVES:
            hive_data = fetch_data(hive, sort_by=args['sort_by'])
            all_vlans.update({hive: hive_data})
    else:
        print("")
        print(f"ERROR: please supply just the hives ID, nothing else!\n")
        print(f"EXAMPLE: {sys.argv[0]} 213")
        print("")
        sys.exit(1)

    # Output sorted by vlan_name
    if args['sort_by'] == 'vlan_name':
        for hive, vlans in all_vlans.items():
            t = PrettyTable()
            t.field_names = [f"Hive{hive} VLAN_Name", "VLAN_Id"]
            for name, vids in vlans.items():
                t.add_row([name, ','.join(str(x) for x in vids)])
            print(t)

    # Output sorted by vlan_id
    elif args['sort_by'] == 'vlan_id':
        print(all_vlans.keys())
        for hive, vlans in all_vlans.items():
            t = PrettyTable()
            t.field_names = [f"Hive{hive} VLAN_Ids", "VLAN_Names"]
            for vid, names in vlans.items():
                t.add_row([vid, ','.join(names)])
            print(t)

    else:
        print("No output formatter found!")
