import requests, json

class NetworkHelper:
    base_url = 'http://127.0.0.1:6363/'
    
    def login(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'username': 'adminadmin',
            'password': '1234'
        }
        response = requests.post(url=f"{self.base_url}api/login/", headers=headers, data=json.dumps(data))

        session_cookie = response.cookies.get('sessionid', None)
        try:
            json_data = response.json()
        except ValueError:
            json_data = {}

        return {
            'status_code': response.status_code,
            'json': json_data,
            'sessionid': session_cookie
        }
    
    def send(self, method, endpoint, data=None, headers=None, params=None, sessionid=None):
        method = method.upper()
        if headers is None:
            headers = {}
        headers.setdefault('Content-Type', 'application/json')
        headers['Authorization'] = json.dumps({"username": "adminadmin", "password": "1234"})

        cookies = {}
        if sessionid:
            cookies['sessionid'] = sessionid

        if method == 'GET':
            response = requests.get(self.base_url+endpoint, headers=headers, params=params, cookies=cookies)
        elif method == 'POST':
            response = requests.post(self.base_url+endpoint, headers=headers, json=data, cookies=cookies)
        elif method == 'PUT':
            response = requests.put(self.base_url+endpoint, headers=headers, json=data, cookies=cookies)
        elif method == 'DELETE':
            response = requests.delete(self.base_url+endpoint, headers=headers, json=data, cookies=cookies)

        try:
            resp_json = response.json()
        except ValueError:
            resp_json = {}

        return {
            'status_code': response.status_code,
            'json': resp_json
        }

