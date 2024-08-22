#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
TSN Adapter
"""

import os
import uuid
import time
import random
from typing import Any
from datetime import datetime, timezone

from loguru import logger
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
    def __init__(self, db_name: str=DB_NAME, version=None):
        super().__init__(version=version)
        self.db_name = db_name
        self.uuid = uuid.uuid4()
        out = self.deploy(self.db_name, './dispatch.kf')
        if out['error'] != "":
            logger.error(out['error'])
            raise ValueError()
    @staticmethod
    def get_value_type(value) -> str:
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, bool):
            return "bool"
        return "string"

    def submit_job(self, jobclass: str, params: dict) -> uuid.UUID:
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
                    "value": value,
                    "val_type": self.get_value_type(value),
                    "created_at": timestamp
                }
            ))
        return jobid

    def set_job_status(self, jobid: str, old_status: str, status: str) -> None:
        ic(self.database_execute(
            self.db_name,
            "set_job_status", {
                "jobid": jobid,
                "oldstatus": old_status,
                "status": status
            }
        ))
    def read_jobs(self) -> dict:
        return self.query(
            self.db_name,
            "select * from jobs"
        )
    def read_params(self, jobid: str) -> dict[str, Any]:
        d = {}
        for item in self.query(
            self.db_name,
            f"select * from params jobs where jobid = '{jobid}'::uuid"
        )['result']:
            if item['value_s'] is not None:
                d[item['param']] = item['value_s']
            elif item['value_b'] is not None:
                d[item['param']] = bool(item['value_b'])
            elif item['value_f'] is not None:
                d[item['param']] = float(item['value_f'])
            elif item['value_i'] is not None:
                d[item['param']] = int(item['value_i'])
            elif item['value_ref'] is not None:
                d[item['param']] = item['value_ref']
        return d

    def read_results(self, jobid: str) -> dict:
        d = {}
        for item in self.query(
            self.db_name,
            f"select * from results where jobid = '{jobid}'::uuid"
        )['result']:
            if item['value_s'] is not None:
                d[item['param']] = item['value_s']
            elif item['value_b'] is not None:
                d[item['param']] = bool(item['value_b'])
            elif item['value_f'] is not None:
                d[item['param']] = float(item['value_f'])
            elif item['value_i'] is not None:
                d[item['param']] = int(item['value_i'])
            elif item['value_ref'] is not None:
                d[item['param']] = item['value_ref']
        return d

    def read_recent_jobs(self, jobclass: str) -> dict:
        return self.query(
            self.db_name,
            f"select * from jobs where status = 'new' and jobclass == '{jobclass}'"
        )['result']

    def read_job_by_jobid(self, jobid: str) -> dict:
        result = ic(self.query(
            self.db_name,
            f"select * from jobs where jobid == '{jobid}'::uuid"
        )['result'])
        if result == "":
            return None
        else:
            return result[0]

    def write_result(self, jobid: str, params: dict):
        current_utc_timestamp = datetime.now(timezone.utc)
        timestamp = int(current_utc_timestamp.timestamp() * 1_000_000_000)
        for key, value in params.items():
            ic(self.database_execute(
                self.db_name,
                "insert_results", {
                    "jobid": jobid,
                    "param": key,
                    "value": value,
                    "val_type": self.get_value_type(value),
                    "created_at": timestamp
                }
            ))
    def database_execute(self, dbid: str, action: str, params: dict) -> dict:
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
    def run_loop(self, jobclass: str, function) -> None:
        while True:
            jobs = ic(self.read_recent_jobs(jobclass))
            ic(jobs)
            if len(jobs) == 0:
                time.sleep(random.randrange(5))
                continue
            jobid = random.choice(jobs)['jobid']
            job_status = "new"
            while job_status == "new":
                self.set_job_status(jobid, "new", f"working-{self.uuid}")
                job = self.read_job_by_jobid(jobid)
                if job is not None and 'status' in job:
                    job_status = job['status']
                time.sleep(5)
            if job_status != f"working-{self.uuid}":
                time.sleep(random.randrange(5))
                continue            
            params = ic(self.read_params(jobid))
            output = function(params)
            self.write_result(jobid, output)
            self.set_job_status(jobid, f"working-{self.uuid}", "done")
    def run_job(self, jobclass: str, params: dict) -> dict:
        jobid = ic(self.submit_job(
            jobclass,
            params
        ))
        while True:
            results = self.read_results(jobid)
            if len(results) > 0:
                ic(results)
                break
            time.sleep(0.2)
        return results

    def wait_results(self, jobids: list) -> dict:
        results_all = {}
        while True:
            for jobid in jobids:
                results = self.read_results(jobid)
                if len(results) > 0:
                    ic(results)
                    jobids.remove(jobid)
                    results_all[jobid] = results
            if len(jobids) == 0:
                break
            time.sleep(0.1)
        return results_all

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
