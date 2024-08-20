#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import sys
import os
import uuid
import random
import pandas as pd

from loguru import logger
from datetime import datetime, timezone
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
        out = self.deploy(self.db_name, './dispatch.kf')
        if out['error'] != "":
            logger.error(out['error'])
            raise ValueError()
    def submit_job(self, jobclass, params):
        jobid = uuid.uuid4()
        current_utc_timestamp = datetime.now(timezone.utc)
        timestamp = int(current_utc_timestamp.timestamp() * 1_000_000_000)
        ic(self.database_execute(
            self.db_name,
            "insert_job", {
                "jobid": jobid,
                "jobclass": jobclass,
                "status": "new",
                "created_at": timestamp
            }
        ))
        for key, value in params.items():
            ic(self.database_execute(
                self.db_name,
                "insert_params", {
                    "jobid": jobid,
                    "param": key,
                    "value": str(value),
                    "val_type": "string",
                    "created_at": timestamp
                }
            ))
        return jobid
    def set_job_status(self, jobid, status):
        ic(self.database_execute(
            self.db_name,
            "set_job_status", {
                "jobid": jobid,
                "status": status
            }
        ))
    def read_jobs(self):
        return self.query(
            self.db_name,
            "select * from jobs"
        )
    def read_params(self, jobid):
        return self.query(
            self.db_name,
            f"select * from params jobs where jobid = '{jobid}'::uuid"
        )

    def read_recent_jobs(self, jobclass):
        return self.query(
            self.db_name,
            f"select * from jobs where status = 'new' and jobclass == '{jobclass}'::uuid"
        )
    def write_result(self, output):
        return {}
    def write_to_table(self, table, data_frame):
        result = self.write_all(data_frame, f'{self.db_name}:{table}')
        ic(result)
        print('Waiting for transaction to clear')
        ic(self.query_tx_wait(result['result']['tx_hash']))
    def database_execute(self, dbid: str, action: str, params: dict):
        args = [
            'database',
            'execute'
        ] + [
            f'${key}:{value}'
            for key, value in params.items()
        ] + [
            '-a',
            action
        ] +  self._get_db_arg(dbid)
        ic(args)
        return self.execute_command_json(
            *args
        )

if __name__ == '__main__':
    connector = TsnAdapter()
    ic(connector.has_schema(DB_NAME))

    ic(connector.ping())
    ic(connector.list_databases())
    ic(connector.read_jobs())
    ic(connector.read_recent_jobs())
    ic(connector.submit_job(
        "f235dda4-2a52-4a2c-b8ff-5a963967e464",
        {"text": "U.S. economy"}
    ))
    ic(connector.read_recent_jobs())
    
    #result = ic(connector.add_admin(DB_NAME, KWIL_USER))
    #ic(connector.query_tx_wait(result['result']['tx_hash']))
    #ic(connector.query(DB_NAME, 'select * from admin_users'))
    #exit(0)



    # Generate pseudo-random UUIDs for data_frame_success
    #random.seed(42)
    #uuids = [ uuid.uuid4() for i in range(5)]

    # Sample data
    # Create DataFrame
    #data_frame = pd.DataFrame(data_frame_data)

    # Print the DataFrame
    #print(data_frame)

    # Write data_frame_fail to KWIL
    #connector.write_table("jobs", data_frame)
