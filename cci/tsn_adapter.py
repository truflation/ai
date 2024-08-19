#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import sys
import os
import uuid
import random
import pandas as pd

from dotenv import load_dotenv
from icecream import ic
from truflation.data.connectors import kwil
load_dotenv()


KWIL_PATH = os.environ['KWIL_PATH']
os.environ['PATH'] += f':{KWIL_PATH}'
ic(os.environ['PATH'])
KWIL_USER = os.environ['KWIL_USER']
DB_NAME = 'dispatch'

# Create KWIL connector
class TsnAdapter(kwil.ConnectorKwil):
    def __init__(self, db_name=DB_NAME, version=None):
        super().__init__(version=version)
        self.db_name = db_name
        self.deploy(self.db_name, './dispatch.kf')
    def read_jobs(self):
        return self.read_all(f'{self.db_name}:job')
    def read_recent_jobs(self):
        return self.query(self.db_name, 'select * from job')
    def write_result(self, output):
        return {}
    def write_to_table(self, table, data_frame):
        result = self.write_all(data_frame, f'{self.db_name}:{table}')
        ic(result)
        print('Waiting for transaction to clear')
        ic(self.query_tx_wait(result['result']['tx_hash']))

if __name__ == '__main__':
    connector = TsnAdapter()
    ic(connector.has_schema(DB_NAME))

    ic(connector.ping())
    ic(connector.list_databases())
    ic(connector.read_jobs())
    ic(connector.read_recent_jobs())
    sys.exit(0)

    #result = ic(connector.add_admin(DB_NAME, KWIL_USER))
    #ic(connector.query_tx_wait(result['result']['tx_hash']))
    #ic(connector.query(DB_NAME, 'select * from admin_users'))
    #exit(0)



    # Generate pseudo-random UUIDs for data_frame_success
    random.seed(42)
    uuids = [ uuid.uuid4() for i in range(5)]

    # Sample data
    data_frame_data = [
        {"id": str(uuids[0]), "status": "new", "created_at": 123},
    ]
    # Create DataFrame
    data_frame = pd.DataFrame(data_frame_data)

    # Print the DataFrame
    print(data_frame)

    # Write data_frame_fail to KWIL
    connector.write_table("jobs", data_frame)
