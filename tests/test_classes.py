import json
import pytest
import asyncio

from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from pyhumio.classes import HumioStructuredMessage, HumioEventSender

from tests.helpers import ( 
    CORRECT_HUMIO, mocked_requests, MockResponse, build_structured_message, build_event_sender
)

class TestHumioMessageClasses:

    @freeze_time('2020-09-01')
    def test_humio_structured_message_without_timestamp(self):
        message = build_structured_message()
        iso_now = datetime.utcnow().astimezone().isoformat()
        
        expected_message = [
            {
                'tags': {'host': message.host, 'source': message.source, 'env': message.environment}, 
                'events': [{'timestamp': iso_now, 'attributes': {'status': True, 'eventType': 'testEvent'}}]
            }
        ]

        assert expected_message == message.built_message


    def test_humio_structured_message_with_timestamp(self):
        iso_now = datetime.utcnow().astimezone().isoformat()
        message = build_structured_message(iso_now)

        expected_message = [
            {
                'tags': {'host': message.host, 'source': message.source, 'env': message.environment}, 
                'events': [{'timestamp': iso_now, 'attributes': {'status': True, 'eventType': 'testEvent'}}]
            }
        ]

        assert expected_message == message.built_message


    @freeze_time('2020-11-16')
    def test_humio_structured_message_to_string(self):
        message = build_structured_message()
        iso_now = datetime.utcnow().astimezone().isoformat()
        
        expected_message = json.dumps(
            [
                {
                    'tags': {'host': message.host, 'source': message.source, 'env': message.environment}, 
                    'events': [
                        {'timestamp': iso_now, 'attributes': {'status': True, 'eventType': 'testEvent'}}
                    ]
                }
            ]
        )

        assert expected_message == message.to_string()


    @pytest.mark.asyncio
    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.aiohttp.ClientSession')
    @patch('pyhumio.classes.HumioEventSender.post_async')
    async def test_send_humio_structured_message_post_args(self, 
                                                           mock_session, 
                                                           mock_post_async):
        f = asyncio.Future()
        f.set_result(MockResponse({}, 200))
        mock_post_async.return_value = f

        token = CORRECT_HUMIO
        attributes = {'status': 'blah', 'eventType': 'failed'}
        event_sender = build_event_sender(token)
        
        event_sender.post_async = mock_post_async

        assert mock_post_async.called_once_with(event_sender, mock_session)


    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.requests.post', side_effect=mocked_requests)
    def test_send_humio_structured_message_happy_path(self, mock_post):
        token = CORRECT_HUMIO
        attributes = {'status': 'blah', 'eventType': 'failed'}
        event_sender = build_event_sender(token)

        send_async = event_sender.send_event(attributes)

        assert send_async.status_code is 200


    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.requests.post', side_effect=mocked_requests)
    def test_send_humio_structured_message_sad_path(self, mock_post):
        token = 'blah'
        attributes = {'status': 'blah', 'eventType': 'failed'}
        event_sender = build_event_sender(token)

        with pytest.raises(Exception):
            event_sender.send_event(attributes)


    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.requests.post', side_effect=mocked_requests)
    def test_send_humio_structured_message_call_args(self, mock_post):
        token = CORRECT_HUMIO
        event_sender = build_event_sender(token)
        message = build_structured_message()
        attributes = {'status': 'blah', 'eventType': 'failed'}
        iso_now = datetime.utcnow().astimezone().isoformat()

        expected_data = [
            {
                'tags': {
                    'host': message.host, 
                    'source': message.source,
                    'env': message.environment
                }, 
                'events': [
                    {
                        'timestamp': iso_now, 
                        'attributes': attributes
                    }
                ]
            }
        ]

        expected_string = json.dumps(expected_data)

        event_sender.send_event(attributes)

        mock_post.assert_called_once_with(
            'https://cloud.humio.com/api/v1/ingest/humio-structured', 
            data=expected_string, 
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CORRECT_HUMIO}'}
        )


    @pytest.mark.asyncio
    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.HumioEventSender.post_async')
    async def test_async_send_humio_structured_message_happy_path(self, 
                                                                  mock_post_async):
        f = asyncio.Future()
        f.set_result(MockResponse({}, 200))
        mock_post_async.return_value = f

        token = CORRECT_HUMIO
        attributes = {'status': 'blah', 'eventType': 'failed'}
        event_sender = build_event_sender(token)
        
        event_sender.post_async = mock_post_async

        send_async = await event_sender.send_event_async(attributes)

        assert send_async.status_code is 200


    @pytest.mark.asyncio
    @freeze_time('2020-11-16')
    @patch('pyhumio.classes.HumioEventSender.post_async')
    async def test_async_send_humio_structured_message_sad_path(self, mock_post_async):
        f = asyncio.Future()
        f.set_result(MockResponse({}, 400))
        mock_post_async.return_value = f

        token = CORRECT_HUMIO
        attributes = {'status': 'blah', 'eventType': 'failed'}
        event_sender = build_event_sender(token)        
        event_sender.post_async = mock_post_async

        with pytest.raises(Exception):
            await event_sender.send_event_async(attributes)