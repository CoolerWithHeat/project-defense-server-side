from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .permissions import *
from .serializers import *
from .parsers import GoogleResponseParser, FacebookResponseParser
from django.contrib.auth import get_user_model
from .customFields import save_custom_field, extract_custom_fields, extract_collection_fields, checkData, dataManager
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
import json, random, string, requests

def GeneratePassword(length):

    def generateRawPassword(firstBatch, SecondBatch):
        data = ''.join(random.choices(string.ascii_lowercase + string.digits, k=firstBatch)) + ''.join(random.choices(string.ascii_uppercase + string.digits, k=SecondBatch))
        return data
    
    firstBatch = round(length/2)
    secondBatch = length-firstBatch
    return generateRawPassword(firstBatch, secondBatch)

def getAdditionFields(id):
    cl = get_object_or_404(Collection, id=id)
    return (cl.custom_fields)

class CreateCollection(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        user = get_user_model().objects.get(email='mansur@gmail.com')
        processedData = {**data, 'author': user.id}
        processedData['topic'] = TOPIC_CHOICES[int(processedData.get('topic', 0))][0]
        serializer = CollectionSerializer(data=processedData)
        if serializer.is_valid():
            serializer.save()
            return Response({'collection':serializer.data})
        else:
            return Response({'error': 'invalid or insufficient data'}, status=500)
    
class CreateItem(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, CL_id, *args, **kwargs):
        item_Fields = json.loads(request.body) if request.body else None
        requested_collection = get_object_or_404(Collection, id=CL_id)
        parsedFields, tags = dataManager.sort_item_data(requested_collection, item_Fields)
        if parsedFields:
            item_instance = Item(**parsedFields)
            serializedItem = ItemSerializer(item_instance, many=False)
            item_instance.save()
            print(parsedFields)
            if tags:
                for tag in tags:
                    item_instance.tags.add(tag)
            return Response({'item': serializedItem.data}, status=200)
        else:
            return Response({'error': 'invalid or insufficient data'}, status=500)
        
class GetItem(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def get(self, request, item_id, *args, **kwargs):
        requested_item = get_object_or_404(Item, id=item_id)
        serializedItem = ItemSerializer(requested_item, many=False)  
        return Response({'item': serializedItem.data}, status=200)
    
class get_Collection_items(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def get(self, request, CL_id, *args, **kwargs):
        requested_collection = get_object_or_404(Collection, id=CL_id)
        items = Item.objects.filter(collection=requested_collection)
        serializedItem = ItemSerializer(items, many=True)  
        return Response({'items': serializedItem.data}, status=200)
    

class Authentication(APIView):

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body) if request.body else {}

        parserClasses = {

            'Google': GoogleResponseParser,
            'Facebook': FacebookResponseParser,
        
        }

        Auth_type = 'Facebook' if data.get('facebook', None) else 'Google' if data.get('google', None) else 'Custom-Authentication'

        if Auth_type == 'Custom-Authentication':
            CredentialsBase = data['Custom-Authentication']
            email = CredentialsBase['email']
            Name = CredentialsBase['full_name']
            passCode1 = CredentialsBase['password1']
            passCode2 = CredentialsBase['password2']

            try:
                    
                user = get_user_model().objects.create(full_name=Name, email=email, password=passCode1, authenticated_by=authentication_options[2][0])
                token = Token.objects.get_or_create(user=user)
            
                return Response({'success': True, 'token': str(token)}, status=200)
            
            except:
                return Response({'success': False, 'error': 'this user already Exists!'}, status=500)
        else:

            SpecifiedCredentials = parserClasses[Auth_type](data)
            email = SpecifiedCredentials.get_EmailAdress
            Name = SpecifiedCredentials.get_FirstName +  SpecifiedCredentials.get_LastName
     
            try:
                
                user = get_user_model().objects.get(email=email)
                token = Token.objects.create(user=user) if Token.objects.get(user=user).delete() else None

                if user:
                    return Response({'success': True, 'token': str(token)}, status=200)
                    
            except:
                from django.core.files.base import ContentFile
                user = get_user_model().objects.create(full_name=Name, email=email, password=GeneratePassword(8))
                token = Token.objects.create(user=user)
                if Auth_type == 'Google':
                    imageRequest = requests.get(SpecifiedCredentials.get_PHOTO_url)
                    image_file = ContentFile(imageRequest.content)
                    image_name = SpecifiedCredentials.get_EmailAdress.split('@gmail.com')[0]
                    user.authenticated_by = authentication_options[0][0]
                    user.profile_image.save(f'{image_name}.jpg', image_file)
                    user.save()
                else:
                    image_name = SpecifiedCredentials.get_EmailAdress.split('@gmail.com')[0]
                    user.profile_image.save(f'{image_name}.jpg', models.IconsForFrontend.objects.get(file_code='default_user').file)
                    user.authenticated_by = authentication_options[1][0]
                    user.save()

                return Response({'success': True, 'token': str(token)}, status=200)