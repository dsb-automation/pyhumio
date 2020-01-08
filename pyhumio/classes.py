import json
import asyncio

import aiohttp
import requests

from datetime import datetime, timezone
from typing import Dict, List


class HumioStructuredMessage:
    def __init__(self, host: str, source: str, attributes: Dict, timestamp: str = None):
        self.host = host
        self.source = source
        self.attributes = attributes
        self.timestamp = timestamp if timestamp else datetime.utcnow().astimezone().isoformat()

    @property
    def built_message(self) -> List:
        return [
            {
                'tags': {
                    'host': self.host,
                    'source': self.source
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
        event = HumioStructuredMessage(self.host, self.source, attributes, timestamp)    
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
        event = HumioStructuredMessage(self.host, self.source, attributes, timestamp)    
    
        async with aiohttp.ClientSession() as session:
                response = await self.post_async(session, event)
                if response.status is not 200:
                    raise Exception('Error sending event to Humio')
                return response