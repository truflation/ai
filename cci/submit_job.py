#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
from dotenv import load_dotenv
from icecream import ic
from tsn_adapter import TsnAdapter
load_dotenv()

KWIL_PATH = os.environ['KWIL_PATH']
os.environ['PATH'] += f':{KWIL_PATH}'
ic(os.environ['PATH'])
KWIL_USER = os.environ['KWIL_USER']
DB_NAME = 'dispatch'

if __name__ == '__main__':
    connector = TsnAdapter()
    ic(connector.has_schema(DB_NAME))

    ic(connector.ping())
    ic(connector.list_databases())
    ic(connector.read_jobs())
    ic(connector.read_recent_jobs("f235dda4-2a52-4a2c-b8ff-5a963967e464"))
    ic(connector.submit_job(
        "f235dda4-2a52-4a2c-b8ff-5a963967e464",
        {"text": "U.S. economy"}
    ))
    ic(connector.read_recent_jobs("f235dda4-2a52-4a2c-b8ff-5a963967e464"))
