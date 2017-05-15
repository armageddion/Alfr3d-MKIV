#!/usr/bin/python

"""
This file is used for all arduino related functions.
"""
# Copyright (c) 2010-2017 LiTtl3.1 Industries (LiTtl3.1).
# All rights reserved.
# This source code and any compilation or derivative thereof is the
# proprietary information of LiTtl3.1 Industries and is
# confidential in nature.
# Use of this source code is subject to the terms of the applicable
# LiTtl3.1 Industries license agreement.
#
# Under no circumstances is this component (or portion thereof) to be in any
# way affected or brought under the terms of any Open Source License without
# the prior express written permission of LiTtl3.1 Industries.
#
# For the purpose of this clause, the term Open Source Software/Component
# includes:
#
# (i) any software/component that requires as a condition of use, modification
#     and/or distribution of such software/component, that such software/
#     component:
#     a. be disclosed or distributed in source code form;
#     b. be licensed for the purpose of making derivative works; and/or
#     c. can be redistributed only free of enforceable intellectual property
#        rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#      or in part) from, or statically or dynamically links against any
#      software/component specified under (i).
#

import json
import requests
import psutil

cpu = psutil.cpu_percent()
disks = psutil.disk_usage('/')
memory = psutil.virtual_memory()

data = {
	"status": "online",
	"cpu": cpu,
	"disks":disks.percent,
	"memory":memory.percent
}

host = "http://dweet.io/dweet/for/alfr3d.mkv?"
headers = {"content-type":"application/json","Accept":"text/plain"}

r = requests.post(host, data=json.dumps(data), headers=headers)