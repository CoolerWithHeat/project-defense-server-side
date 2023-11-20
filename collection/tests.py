from django.test import TestCase
import requests

headers={
    'Authorization': 'Token 79dde1e1c11dcd9a8c2a4f6833cc5e872083dfae'
}
# request = requests.post('http://127.0.0.1:8000/CreateCl/', headers=headers, json={'name':'nice pussies owned by Mansur', 'description':'ladies that was attracted to me', 'topic':'1', 'customFields':[['fucked', 'date']]})
request = requests.post('http://127.0.0.1:8000/CreateIT/7/', headers=headers, json={'name':'armina', 'tags':['wines', 'drinks', 'alcoholic'], 'additionalFields':{'fucked':'yesterday'}})
# request = requests.get('http://127.0.0.1:8000/getItem/134/')
# request = requests.get('http://127.0.0.1:8000/Get-All-Items/1/', headers=headers)
print(request.json())