import os
import json
import pytest
import logging
import datetime

from unittest.mock import MagicMock, patch

from pyhumio.humio_handler import HumioUnstructuredMessage, HumioHandler, LOG_FORMAT

CORRECT_HUMIO = 'correct_token'


def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if not CORRECT_HUMIO in kwargs['headers']['Authorization']:
        return MockResponse({"humio_auth": "failed"}, 403)

    return MockResponse({"humio_auth": "success"}, 200)


class TestHumoHandler:

    def test_humio_unstructured_message(self):
        source = 'test'
        environment = 'dev'
        level = 'info'
        my_log_message = 'formatted log'
        message = HumioUnstructuredMessage(source=source, 
                                           environment=environment, 
                                           level=level,
                                           message=my_log_message)

        assert message.built_message == [
            {
                'fields': {
                    'source': source,
                    'env': environment,
                    'level': level,
                    'message': my_log_message
                },
                'messages': [my_log_message] 
            }
        ]


    @patch('pyhumio.humio_handler.HumioHandler.format')
    @patch('pyhumio.humio_handler.requests.post', side_effect=mocked_requests)
    def test_humio_handler_correct_token_no_exception(self, mock_requests, mock_format):
        formatted_message = 'formatted log'
        mock_format.return_value = formatted_message
        
        handler = HumioHandler(source='test', environment='dev', humio_token=CORRECT_HUMIO)


    @patch('pyhumio.humio_handler.HumioHandler.format')
    @patch('pyhumio.humio_handler.requests.post', side_effect=mocked_requests)
    def test_requests_called_with_correct_params(self, mock_requests, mock_format):
        source = 'test'
        environment = 'dev'
        level = 'INFO'
        message = 'formatted log'
        mock_format.return_value = message


        handler = HumioHandler(source=source, environment=environment, humio_token=CORRECT_HUMIO)

        expected_data = [
            {
                'fields': {
                    'source': source,
                    'env': environment,
                    'level': level,
                    'message': message
                },
                'messages': [message] 
            }
        ]
        expected_string = json.dumps(expected_data)

        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info(message)

        mock_requests.assert_called_once_with(
            'https://cloud.humio.com/api/v1/ingest/humio-unstructured', 
            data=expected_string, 
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CORRECT_HUMIO}'}
        )


    @patch('pyhumio.humio_handler.requests.post', side_effect=mocked_requests)
    def test_no_exception_thrown_when_logging(self, mock_requests):
        source = 'test'
        environment = 'dev'

        handler = HumioHandler(source=source, environment=environment, humio_token=CORRECT_HUMIO)
        
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info('This is a test')


    @patch('pyhumio.humio_handler.requests.post', side_effect=mocked_requests)
    def test_exception_thrown_when_token_is_wrong(self, mock_requests):
        source = 'test'
        environment = 'dev'

        handler = HumioHandler(source=source, environment=environment, humio_token='blah')
        
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        with pytest.raises(Exception):
            logger.info('This is a test')
