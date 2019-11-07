import os
import json
import requests

from typing import Dict, List
from logging import StreamHandler


class HumioUnstructuredMessage:
    def __init__(self, source: str, environment: str, message: str):
        self.source = source
        self.environment = environment
        self.message = message


    @property
    def built_message(self) -> List:
        built_message = [
            {
                'fields': {
                    'source': self.source,
                    'env': self.environment,
                    'message': self.message
                },
                'messages': [self.message] 
            }
        ]
        return built_message


    def to_string(self) -> str:
        return json.dumps(self.built_message)

    
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

    def emit(self, record):
        msg = self.format(record)
        built_message = HumioUnstructuredMessage(self.source, self.environment, msg)

        send_response = requests.post(self.built_url, data=built_message.to_string(), headers=self.headers)
        
        if send_response.status_code is not 200:
            raise Exception('Error sending log to Humio')