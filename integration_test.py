### integration_test.py
import requests

# Simulate front-end behavior
code = 'mock_auth_code_123'
token_res = requests.post('http://localhost:5000/token', data={'code': code})
token = token_res.json()['access_token']

res = requests.get('http://localhost:5001/books', headers={'Authorization': f'Bearer {token}'})
print(res.json())
