import json
import asyncio

import aiohttp
import requests

from typing import Dict, List
from abc import ABC, abstractmethod
from datetime import datetime, timezone


class HumioMessage(ABC):

    @abstractmethod
    def __init__(self, host: str, source: str, environment: str):
        self.host = host
        self.source = source
        self.environment = environment

    @abstractmethod
    def built_message(self) -> List:
        raise NotImplementedError()

    @abstractmethod
    def to_string(self) -> str:
        raise NotImplementedError()


class HumioUnstructuredMessage(HumioMessage):
    
    def __init__(self, 
                 source: str, 
                 environment: str, 
                 level: str, 
                 message: str,
                 host=None):
        _host = host if host else source
        self.level = level
        self.message = message
        super(HumioUnstructuredMessage, self).__init__(_host, source, environment)


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
        

class HumioStructuredMessage(HumioMessage):

    def __init__(self, 
                 host: str, 
                 source: str, 
                 environment: str, 
                 attributes: Dict, 
                 timestamp: str = None):
        self.attributes = attributes
        self.timestamp = timestamp if timestamp else datetime.utcnow().astimezone().isoformat()
        super(HumioStructuredMessage, self).__init__(host, source, environment)

    @property
    def built_message(self) -> List:
        return [
            {
                'tags': {
                    'host': self.host,
                    'source': self.source,
                    'environment': self.environment
                },
                'events': [
                    {
                        'timestamp': self.timestamp,
                        'attributes': self.attributes
                    }
                ]
            }
        ]

    def to_string(self) -> str:
        return json.dumps(self.built_message)


class HumioEventSender:

    def __init__(self, source: str, token: str, environment: str, host: str = None):
        self.source = source
        self.token = token
        self.environment = environment
        self.humio_url = 'https://cloud.humio.com/api/v1/ingest/humio-structured'
        self.host = host if host else source
        
    @property
    def headers(self) -> Dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def send_event(self, attributes: Dict, timestamp: str = None):
        # Event should be dependency injected
        event = HumioStructuredMessage(self.host, self.source, self.environment, attributes, timestamp)    
        response = requests.post(self.humio_url,
                                 data=event.to_string(),
                                 headers=self.headers)
        if response.status is not 200:
            raise Exception('Error sending event to Humio')
        return response

    async def post_async(self, session, event):
        async with session.post(self.humio_url, 
                                data=event.to_string(), 
                                headers=self.headers) as response:
            return response

    async def send_event_async(self, attributes: Dict, timestamp: str = None):
        # Event should be dependency injected
        event = HumioStructuredMessage(self.host, self.source, self.environment, attributes, timestamp)    
    
        async with aiohttp.ClientSession() as session:
                response = await self.post_async(session, event)
                if response.status is not 200:
                    raise Exception('Error sending event to Humio')
                return response