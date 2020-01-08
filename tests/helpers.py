from pyhumio.classes import HumioStructuredMessage, HumioEventSender

CORRECT_HUMIO = 'correct_token'


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    @property
    def status(self):
        return self.status_code


def mocked_requests(*args, **kwargs):
    
    if not CORRECT_HUMIO in kwargs['headers']['Authorization']:
        return MockResponse({"humio_auth": "failed"}, 403)

    return MockResponse({"humio_auth": "success"}, 200)


def build_structured_message():
        return HumioStructuredMessage(host='humio_tests', 
                                      source='test_source', 
                                      environment='dev', 
                                      attributes={'status': True, 'eventType': 'testEvent'})



def build_event_sender(token):
        host = 'humio_tests'
        source = 'test_source'
        environment = 'dev'
        return HumioEventSender(host=host, 
                                source=source, 
                                environment=environment,
                                token=token)
