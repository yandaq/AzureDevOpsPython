Azure DevOps Python
===================

Some simple scripts to extract data out of Azure DevOps
* cttd.py - Cycle Time To Date for Active work items
* cycletime.py - Cycle Time for Closed work items
* timeincolumn.py - Calculates the time in column of Active work items

Requirements
------------

* Python 3

Usage
-----
CTTD.py:
```sh
$ python3 -W ignore cttd.py
```

cycletime.py:
```sh
$ python3 -W ignore cycletime.py
```

timeincolumn.py:
```sh
$ python3 -W ignore timeincolumn.py
```

Setup
-----
Before running the scripts, please edit each script and complete the following credentials:
* Personal access token
* Username
* URL to your instance of Azure DevOps
* queryFilter - the filter used to get your list of work items
If you get an error when running the scripts, please double check your credentials and queryFilter carefully before raising an issue here.
