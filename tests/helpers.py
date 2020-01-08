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
