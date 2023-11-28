from django.test import TestCase
import requests

headers={
    'Authorization': 'Token 6b9287ea3f6963b7bbdd242b25115b691000ffb8'
}
# request = requests.post('http://127.0.0.1:8000/CreateCl/', headers=headers, json={'name':'nice pussies owned by Mansur', 'description':'ladies that was attracted to me', 'topic':'1', 'customFields':[['fucked', 'date']]})
# request = requests.post('http://127.0.0.1:8000/CreateIT/2/', headers=headers, json={'name':'armina', 'tags':['wines', 'drinks', 'alcoholic'], 'additionalFields':{'fucked':'yesterday'}})
request = requests.get('http://127.0.0.1:8000/AllCollections-Admin/')
# request = requests.get('http://127.0.0.1:8000/Get-All-Items/1/', headers=headers)
# request = requests.get('http://127.0.0.1:8000/advancedSearch/')
print(request.json()) 