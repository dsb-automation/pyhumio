import json
import pytest

from unittest.mock import MagicMock, patch

from python_humio.log_handler import HumioHandler


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

    @patch('python_humio.log_handler.HumioHandler.format')
    @patch('python_humio.log_handler.requests.post', side_effect=mocked_requests)
    def test_humio_handler_wrong_token_raises_exception(self, mock_requests, mock_format):
        formatted_message = 'formatted log'
        mock_format.return_value = formatted_message
        bad_humio_token = 'bad_token'
        
        handler = HumioHandler(source='test', environment='dev', humio_token='bad_token')
        
        with pytest.raises(Exception):
            handler.emit(formatted_message)


    @patch('python_humio.log_handler.HumioHandler.format')
    @patch('python_humio.log_handler.requests.post', side_effect=mocked_requests)
    def test_humio_handler_correct_token_no_exception(self, mock_requests, mock_format):
        formatted_message = 'formatted log'
        mock_format.return_value = formatted_message
        
        handler = HumioHandler(source='test', environment='dev', humio_token=CORRECT_HUMIO)
        

    @patch('python_humio.log_handler.HumioHandler.format')
    @patch('python_humio.log_handler.requests.post', side_effect=mocked_requests)
    def test_humio_handler_message_format(self, mock_requests, mock_format):
        source = 'test'
        environment = 'dev'
        my_log_message = 'formatted log'

        
        handler = HumioHandler(source=source, environment=environment, humio_token=CORRECT_HUMIO)
        built_message = handler.build_message(my_log_message)

        assert built_message == [
            {
                'fields': {
                    'source': source,
                    'env': environment
                },
                'messages': [my_log_message]
            }
        ]


    @patch('python_humio.log_handler.HumioHandler.format')
    @patch('python_humio.log_handler.requests.post', side_effect=mocked_requests)
    def test_requests_called_with_correct_params(self, mock_requests, mock_format):
        source = 'test'
        environment = 'dev'
        formatted_message = 'formatted log'
        mock_format.return_value = formatted_message
        
        handler = HumioHandler(source=source, environment=environment, humio_token=CORRECT_HUMIO)

        expected_data = [
            {
                'fields': {
                    'source': source,
                    'env': environment
                },
                'messages': [formatted_message]
            }
        ]
        expected_string = json.dumps(expected_data)
        
        handler.emit(formatted_message)

        mock_requests.assert_called_once_with(
            'https://cloud.humio.com/api/v1/ingest/humio-unstructured', 
            data=expected_string, 
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CORRECT_HUMIO}'}
        )
