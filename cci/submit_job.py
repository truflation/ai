#!/usr/bin/env python3

"""
Usage: script.py <text>

Options:
  <text> The text to process

SPDX-License-Identifier: Apache-2.0
"""



import os
import time
from dotenv import load_dotenv
from icecream import ic
from tsn_adapter import TsnAdapter
from docopt import docopt

load_dotenv()



KWIL_PATH = os.environ['KWIL_PATH']
os.environ['PATH'] += f':{KWIL_PATH}'
ic(os.environ['PATH'])
KWIL_USER = os.environ['KWIL_USER']
DB_NAME = 'dispatch'

def main(text):
    connector = TsnAdapter()
    ic(connector.has_schema(DB_NAME))

    ic(connector.ping())
    ic(connector.list_databases())
    ic(connector.read_jobs())
    ic(connector.read_recent_jobs("f235dda4-2a52-4a2c-b8ff-5a963967e464"))
    jobid = ic(connector.submit_job(
        "f235dda4-2a52-4a2c-b8ff-5a963967e464",
        {"text": text}
    ))
    ic(connector.read_recent_jobs("f235dda4-2a52-4a2c-b8ff-5a963967e464"))
    while True:
        results = ic(connector.read_results(jobid))
        if len(results) > 0:
            break
        time.sleep(1)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args["<text>"])
