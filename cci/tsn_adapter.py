#!/usr/bin/env python3

import sys
import os
import time
import pandas as pd
import uuid
import random

from dotenv import load_dotenv
from icecream import ic
load_dotenv()

import truflation.data.connectors.kwil as kwil
from truflation.data.connector import connector_factory
KWIL_PATH = os.environ['KWIL_PATH']
os.environ['PATH'] += f':{KWIL_PATH}'
ic(os.environ['PATH'])
KWIL_USER = os.environ['KWIL_USER']
DB_NAME = 'dispatch'

# Create KWIL connector
class TsnAdapter(kwil.ConnectorKwil):
    def __init__(self, db_name=DB_NAME):
        super().__init__(version="0.8.3+release.")
        self.db_name = db_name
        self.deploy(self.db_name, './dispatch.kf')
    def read_jobs(self):
        return self.read_all(f'{self.db_name}:job')
    def read_recent_jobs(self):
        return self.query(self.db_name, 'select * from job')

if __name__ == '__main__':
    connector = TsnAdapter()
    ic(connector.has_schema(DB_NAME))

    ic(connector.ping())
    ic(connector.list_databases())
    ic(connector.read_jobs())
    ic(connector.read_recent_jobs())
exit(0)

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

def write_to_kwil(db_name, table, data_frame):
    result = connector.write_all(data_frame, f'{db_name}:{table}')
    ic(result)
    print('Waiting for transaction to clear')
    ic(connector.query_tx_wait(result['result']['tx_hash']))
    ic(connector.read_all(f'{db_name}:prices'))


# Write data_frame_fail to KWIL
write_to_kwil(DB_NAME, "jobs", data_frame)

