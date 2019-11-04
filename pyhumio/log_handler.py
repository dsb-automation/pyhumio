import os
import json
import requests

from typing import Dict, List
from logging import StreamHandler


class HumioHandler(StreamHandler):
    
    def __init__(self, source: str, environment: str, humio_token: str):
        StreamHandler.__init__(self)

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


    def build_message(self, message: str) -> List[Dict]:
        built_message = [
            {
                "fields": {
                    "source": self.source,
                    "env": self.environment
                },
                "messages": [message]
            }
        ]
        return built_message


    def emit(self, record):
        msg = self.build_message(self.format(record))
        send_response = requests.post(self.built_url, data=json.dumps(msg), headers=self.headers)
        if send_response.status_code is not 200:
            raise Exception('Error sending log to Humio')
        