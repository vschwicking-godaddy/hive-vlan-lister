# Hive VLAN List Utility
Fetches VLANs from a hives API and displays them in readable table.

# Usage
```
$ ./hive_vlan_overview.py -h
usage: hive_vlan_overview.py [-h] [-s SORT_BY] [-i HIVE_ID]

options:
  -h, --help            show this help message and exit
  -s SORT_BY, --sort-by SORT_BY
                        Sort result by "vlan_id" or "vlan_name" (default: vlan_name)
  -i HIVE_ID, --hive-id HIVE_ID
                        The hive to query for data (default: 205)
```

The Hive-API requires HTTP-Basic authentication. Username and password are available in AWS
Secretsmanager in account "gd-aws-usa-cio-nettmsecr0-dev-private" account in the secret "Hive-Instances-API-Credentials".

These need to be put into the environment before executing the script.
```
export API_USER=<username>
export API_PASSWORD=<api_password>

$ ./hive_vlan_overview.py -i 213 -s vlan_id
{'sort_by': 'vlan_id', 'hive_id': '213'}
Fetching VLANs from hive213
+------------------+-----------------------------------------------------+
| Hive213 VLAN_Ids |                      VLAN_Names                     |
+------------------+-----------------------------------------------------+
|        1         |                 DEFAULT_VLAN,default                |
|        8         |                 HIVE213-UPLINK,vlan8                |
...
```

# Examples
List VLANs by VLAN-Name from hive213
```
$ ./hive_vlan_overview.py -i 213 -s vlan_name
{'sort_by': 'vlan_name', 'hive_id': '213'}
Fetching VLANs from hive213
+---------------------------------------------+---------+
|              Hive213 VLAN_Name              | VLAN_Id |
+---------------------------------------------+---------+
|                 DEFAULT_VLAN                |    1    |
|                   default                   |    1    |
...
```

List VLANs from Hive213 sorted by VLAN-Id
```
$ ./hive_vlan_overview.py -i 213 -s vlan_id
{'sort_by': 'vlan_id', 'hive_id': '213'}
Fetching VLANs from hive213
+------------------+-----------------------------------------------------+
| Hive213 VLAN_Ids |                      VLAN_Names                     |
+------------------+-----------------------------------------------------+
|        1         |                 DEFAULT_VLAN,default                |
|        8         |                 HIVE213-UPLINK,vlan8                |
|        12        |                   CSE-DRAC,vlan12                   |
...
```

List VLANs from hive205 and hive213 sorted by VLAN-Name
```
$ ./hive_vlan_overview.py -s vlan_name -i 205,213
{'sort_by': 'vlan_name', 'hive_id': '205,213'}
Fetching VLANs from hive205
Fetching VLANs from hive213
+-----------------------------------+---------+
|         Hive205 VLAN_Name         | VLAN_Id |
+-----------------------------------+---------+
|              default              |    1    |
|         HIVE Public Uplink        |    8    |
|               vlan8               |    8    |
|              api.hive             |    9    |
|       HIVE API Public Uplink      |    9    |
...
+-----------------------------------+---------+
+---------------------------------------------+---------+
|              Hive213 VLAN_Name              | VLAN_Id |
+---------------------------------------------+---------+
|                 DEFAULT_VLAN                |    1    |
|                   default                   |    1    |
|                HIVE213-UPLINK               |    8    |
|                    vlan8                    |    8    |
|                   CSE-DRAC                  |    12   |
|                    vlan12                   |    12   |
|              ROUTE-INJ-AUT-HOST             |    15   |
...
```


List VLANs from hive205 and hive213 sorted by VLAN-Id
```
$ ./hive_vlan_overview.py -s vlan_id -i 205,213
{'sort_by': 'vlan_id', 'hive_id': '205,213'}
Fetching VLANs from hive205
Fetching VLANs from hive213
dict_keys(['205', '213'])
+------------------+---------------------------------------------+
| Hive205 VLAN_Ids |                  VLAN_Names                 |
+------------------+---------------------------------------------+
|        1         |                   default                   |
|        8         |           HIVE Public Uplink,vlan8          |
|        9         |    api.hive,HIVE API Public Uplink,vlan9    |
|        11        |           Nagios Nodes SXB1,vlan11          |
|        12        |               CSE-DRAC,vlan12               |
...
+------------------+---------------------------------------------+
+------------------+-----------------------------------------------------+
| Hive213 VLAN_Ids |                      VLAN_Names                     |
+------------------+-----------------------------------------------------+
|        1         |                 DEFAULT_VLAN,default                |
|        8         |                 HIVE213-UPLINK,vlan8                |
|        12        |                   CSE-DRAC,vlan12                   |
|        15        |              ROUTE-INJ-AUT-HOST,vlan15              |
|        23        |              Management,noc-mgmt,vlan23             |
|        24        |                INFRASTRUCTURE,vlan24                |
|        29        |                        vlan29                       |
|        30        |            GDE DS CORE-DC Private,vlan30            |
...
```
