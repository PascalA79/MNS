import unittest
import requests
class TestApplication(unittest.TestCase):
    def setUp(self):
        self.url = 'http://localhost:80'
        response = requests.post('http://localhost:80' + '/token', data={'pseudo':'PascalA79', 'password':'qwerty123!'}).json()
        token = response.get('value')
        self.headers = {'Authorization': token}
    
    def test_create_streamer(self):
        response = requests.post(self.url + '/api/streamers', headers=self.headers, data={'pseudo':'PascalA79'})
        self.assertEqual(response.status_code, 201)

    def test_get_streamers(self):
        response = requests.get(self.url + '/api/streamers', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), True)

if __name__ == "__main__":
    unittest.main()