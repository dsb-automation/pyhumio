import os
import json
import logging

import requests

from typing import Dict, List


LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'


# TODO: Create humio message base class
# TODO: Change source to host
class HumioUnstructuredMessage:
    def __init__(self, source: str, environment: str, level: str, message: str):
        self.source = source
        self.environment = environment
        self.level = level
        self.message = message


    @property
    def built_message(self) -> List:
        built_message = [
            {
                'fields': {
                    'source': self.source,
                    'env': self.environment,
                    'level': self.level,
                    'message': self.message
                },
                'messages': [self.message] 
            }
        ]
        return built_message


    def to_string(self) -> str:
        return json.dumps(self.built_message)

    
class HumioHandler(logging.StreamHandler):
    
    def __init__(self, source: str, environment: str, humio_token: str):
        logging.StreamHandler.__init__(self)

        formatter = logging.Formatter(LOG_FORMAT)
        formatter.default_msec_format = '%s.%03d'
        self.setFormatter(formatter)

        self.token = humio_token
        self.source = source
        self.environment = environment
        self.base_url = 'https://cloud.humio.com'
        self.built_url = f'{self.base_url}/api/v1/ingest/humio-unstructured'


    @property
    def headers(self) -> Dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def emit(self, record):
        msg = self.format(record)
        built_message = HumioUnstructuredMessage(source=self.source, 
                                                 environment=self.environment,
                                                 level=record.levelname, 
                                                 message=msg)

        send_response = requests.post(self.built_url, data=built_message.to_string(), headers=self.headers)

        if send_response.status_code is not 200:
            raise Exception('Error sending log to Humio')