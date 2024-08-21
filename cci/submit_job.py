#!/usr/bin/env python3

"""
Usage: script.py <text> ...

Options:
  <text> The text to process

SPDX-License-Identifier: Apache-2.0
"""
from docopt import docopt
from icecream import ic
from tsn_adapter import TsnAdapter

if __name__ == '__main__':
    args = docopt(__doc__)
    connector = TsnAdapter()
    jobids = ic([connector.submit_job(
        "f235dda4-2a52-4a2c-b8ff-5a963967e464",
        {"text": text}
    ) for text in args["<text>"]])
    ic(connector.wait_results(jobids))
