from django.test import TestCase
import requests

headers={
    'Authorization': 'Token a3c837585b9b038d8f5d1a7938f77f47a1dfec50'
}
# request = requests.post('http://127.0.0.1:8000/CreateCl/', json={'name':'hennesies', 'description':'cool collection of wines!', 'topic':'3', 'customFields':[['published', 'date'], ['funded', 'date']]})
# request = requests.post('http://127.0.0.1:8000/CreateIT/1/', json={'name':'specialAlcohol', 'tags':['wines', 'drinks', 'alcoholic'], 'additionalFields':{'fucked':'yesterday'}})
# request = requests.get('http://127.0.0.1:8000/getItem/134/')
request = requests.get('http://127.0.0.1:8000/Get-All-Items/1/', headers=headers)
print(request.json())