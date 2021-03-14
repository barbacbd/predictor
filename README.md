# UCSMDE Maneuver Operations

The purpose of the project is to integrate SAS with the UCSMDE framework for maneuvering operations including (but not limited to):

1. Zones (Keep in and Keep out zones)
2. Operational Mode
3. Behavior Translation

# Prerequisites

The JANUS project only utilizes Red Hat but CentOS will also work. In that case the user will have to ensure
that yum or dnf (if you prefer this package) are in working states.

**Please Ensure that your repos are setup correctly, include yum/dnf and pip**

- scs-idls
- ctoc
- ctoc-devel
- caracas-behavior-msgs
- caracas-behavior-msgs-devel
- caracas-executive-msgs
- caracas-executive-msgs-devel
- caracas-geometry-msgs
- caracas-geometry-msgs-devel
- caracas-navigation-msgs
- caracas-navigation-msgs-devel
- caracas-perception-msgs
- caracas-perception-msgs-devel
- caracas-vehicle-msgs
- caracas-vehicle-msgs-devel
- ctoc-transport-msgs
- ctoc-transport-msgs-devel
- mission-status-msgs
- mission-status-msgs-devel
- python37
- python37-devel
- sis-ctoc-health-msgs-python37
- sis-mission-status-msgs-python37

# Requirements

The following dependencies can be obtained from the SIS repo:

- pyctoc
- py-caracas-behavior-msgs
- py-caracas-executive-msgs
- py-caracas-geometry-msgs
- py-caracas-navigation-msgs
- py-caracas-perception-msgs
- py-caracas-vehicle-msgs
- py-ctoc-transport-msgs
- sis-ucsmde-utilities

# Installation

The modules **should** be installed with python3.7 to ensure that asynchronous functionality is
up to date.

## Native

```bash
[sudo] pip3.7 install ucsmde-maneuver-operations
```

*NOTE: if you are installing the local package use `.` instead of the full package name.*

Add the following tag to update the package:
```bash
--upgrade
```

## Virtual Environment

```bash
python3.7 -m venv /dir/to/venv
```
This will create the Virtual environment.

```bash
source /dir/to/venv/activate
```
To activate your virtual environment that was just created. You may now install your package with`pip`.

# Coding style

1. Class names are to be Camel cased
2. File names are to be snake cased
3. package names are to be snake cased
4. At the top of each SIS file, the following shall be included:
```python
"""
Distribution Statement F: Further dissemination only as directed by
The Strategic Capabilities Office, 675 N. Randolph St. Arlington, VA 22203, 28 Aug 2018

© {YEAR} Spatial Integrated Systems, Inc. Unpublished-rights reserved under the
copyright laws of the United States

Author: {USER}
Date: {DATE}
"""
```

# Versions

Example Version: 1.4.3

The major version is 1, the minor version is 4, and the bog fix or testing version is 3.

Major versions consist of Milestones in the project and/or major structural changes that will severely alter
another projects ability to use this package.

Minor versions generally coincide with the end of a sprint or addition of new modules but
no changes to current software is required.

Bug fixes are generally linked to tickets and testing during sprints or integration events.