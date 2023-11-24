from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .permissions import *
from .serializers import *
from .parsers import GoogleResponseParser, FacebookResponseParser
from django.contrib.auth import get_user_model
from .customFields import *
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
import json, random, string, requests
from rest_framework.parsers import MultiPartParser
import algoliasearch_django as algoliasearch
from algoliasearch_django import AlgoliaIndex
from .consumers import retrieveTime
from django.db.models import Count
from django.contrib.auth.hashers import make_password


def ItemSearch(key):
    result = algoliasearch.raw_search(Item, key)
    return result

def PerformSearch(keyword):
    
    items_result = []
    collections_result = []
    comments_result = []

    search_indices = {
        0: items_result,
        1: collections_result,
        2: comments_result, 
    }
    
    models_instances = {
        0: Item,
        1: Collection,
        2: Comment,
    }

    for process_index in range(3):
        search_results = algoliasearch.raw_search(models_instances[process_index], keyword) if (process_index == 1) or (process_index == 2) else ItemSearch(keyword)
        if search_results.get('hits'):
            if process_index == 0:
                for each in search_results['hits']:
                    data_object = {'id': each.get('objectID'), 'name': each.get('name')}
                    items_result.append(data_object)
            elif process_index == 1:
                for each in search_results['hits']:
                    data_object = {'id': each.get('objectID'), 'name': each.get('name'), 'topic': each.get('topic'), 'image': f'https://djangostaticfileshub.s3.amazonaws.com/{each.get("image")}' if each.get("image") else None}
                    collections_result.append(data_object)
            elif process_index == 2:
                for each in search_results['hits']:
                    try:
                        comment = Comment.objects.get(id=each.get('objectID'))
                        processed_data = {'id': comment.item.id, 'text': comment.text}
                        comments_result.append(processed_data)
                    except:
                        pass

    return {'items': items_result, 'collections': collections_result, 'comments': comments_result}


class SearchDB(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        keyword = data.get('keyword')
        search_result = PerformSearch(keyword)
        return Response({'search_result': search_result}, status=200)


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
    parser_classes = [MultiPartParser]
    def post(self, request, *args, **kwargs):
        data = request.data or {}
        user = request.user
        topic = TOPIC_CHOICES[int(data.get('topic')) - 1][0]
        description = data.get('description', None)
        image = data.get('image', None)
        processedData = {
            'name': data.get('name', None), 
            'topic':topic, 
            'author': user.id,
        }
        if not description == 'null':
            processedData['description'] = description

        if not image == 'null':
            processedData['image'] = image
        serializer = CollectionSerializer(data=processedData)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({'collection':serializer.data})
        return Response({'error':'invalid or insufficient data'}, status=500)

    
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
            if tags:
                for tag in tags:
                    item_instance.tags.add(tag)
            return Response({'item': serializedItem.data}, status=200)
        else:
            return Response({'error': 'invalid or insufficient data'}, status=500)
        
class GetItem(APIView):
    def get(self, request, item_id, *args, **kwargs):
        requested_item = get_object_or_404(Item, id=item_id)
        comments = []
        item_comments = Comment.objects.filter(item=requested_item)
        if item_comments:
            for eachComment in item_comments:
                comments.append({'id':eachComment.id, 'text': eachComment.text, 'commenter':eachComment.user.full_name, 'date':retrieveTime(eachComment.timestamp)})
        serializedItem = ItemSerializer(requested_item, many=False)  
        return Response({'item': serializedItem.data, 'comments':comments}, status=200)
    
class get_Collection_items(APIView):
    def get(self, request, CL_id, *args, **kwargs):
        requested_collection = get_object_or_404(Collection, id=CL_id)
        items = Item.objects.filter(collection=requested_collection)
        serializedItem = ItemSerializer(items, many=True)  
        return Response({'items': serializedItem.data}, status=200)

class get_Collections(APIView):
    def get(self, request, *args, **kwargs):
        requested_collections = Collection.objects.all()
        Serialized_Collections = CollectionSerializer(requested_collections, many=True)  
        return Response({'collections': Serialized_Collections.data}, status=200)
    
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
                if passCode1 == passCode2:

                    user = get_user_model().objects.create(full_name=Name, email=email, password=make_password(passCode1), authenticated_by=authentication_options[2][0])
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'success': True, 'token': str(token)}, status=200)
                
                return Response({'success': False, 'error': 'invalid credentials!'}, status=500)
            
            except:
                return Response({'success': False, 'error': 'this user already Exists!'}, status=500)
        else:

            SpecifiedCredentials = parserClasses[Auth_type](data)
            email = SpecifiedCredentials.get_EmailAdress
            Name = SpecifiedCredentials.get_FirstName + ' ' +  SpecifiedCredentials.get_LastName
     
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

class edit_item(APIView):
    permission_classes = [DenyAnonymousPermission] 
    def post(self, request, item_id, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        if data:
            try:
                user = request.user
                edited_item = Item.objects.get(id=item_id)
                eligible_user = edited_item.collection.author == user or user.admin
                if eligible_user:
                    edited_item.name = data.get('name', None)
                    saved_item = edited_item.save()
                    serializedItem = ItemSerializer(edited_item, many=False)
                    return Response({'item': serializedItem.data}, status=200)
            except:
                return Response({'result': False}, status=500)

class delete_item(APIView):
    permission_classes = [DenyAnonymousPermission] 
    def post(self, request, item_id, *args, **kwargs):
        requestd_item = get_object_or_404(Item, id=item_id)
        eligible_user = requestd_item.collection.author == request.user or request.user.admin
        if requestd_item and eligible_user:
            requestd_item.delete()
            return Response({'id': item_id}, status=200)
        else:
            return Response({'id': None}, status=500)

class RetrieveCustomFields(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, CL_id, *args, **kwargs):
        try:
            requested_collection = get_object_or_404(Collection, id=CL_id)
            custom_fields = requested_collection.custom_fields
            return Response(custom_fields if custom_fields else [], status=200)
        except:
            return Response({'result': False}, status=500)
        
class delete_collection(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        collection_IDs = data.get('requested_ids', None)
        deleted_ones = []
        for each_ID in collection_IDs:
            try:
                requested_collection = Collection.objects.get(id=each_ID)
                requested_collection.delete()
                deleted_ones.append(each_ID)
            except:
                pass
        return Response({'deleted_IDs': deleted_ones})
    
class SaveCustom_Field(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, CL_ID, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        try:

            requested_collection = Collection.objects.get(id=CL_ID)
            if data:
                requested_collection.custom_fields = data
                requested_collection.save()
                serializedCL = CollectionSerializer(requested_collection, many=False)
                return Response({'collection': serializedCL.data}, status=200)
            else:
                serializedCL = CollectionSerializer(requested_collection, many=False)
                return Response({'collection': serializedCL.data}, status=200)
        except:
            return Response(status=500)
        
class Save_Comment(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def post(self, request, IT_ID, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        try:
            requested_item = Item.objects.get(id=IT_ID)
            comment  = Comment.objects.create(item = requested_item, user=request.user, text=data.get('text'))
            return Response(status=200)
        except:
            return Response(status=500)
        
class MainDisplay(APIView):
    def get(self, request, *args, **kwargs):
        try:
            items = Item.objects.annotate(tag_count=Count('tags')).filter(tag_count__gte=2)
            collections = Collection.objects.annotate(item_count=Count('item'))
            serialized_items = ItemSerializer(items, many=True)
            serialized_collections = CollectionSerializer(collections, many=True)
            tags = Tag.objects.all()[:28]
            serializedTags = []
            for eachTag in tags:
                serializedTags.append(eachTag.name)
            return Response({'collections': serialized_collections.data, 'items': serialized_items.data, 'tags':serializedTags})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class GetIndividualCollections(APIView):
    permission_classes = [DenyAnonymousPermission]
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        if data:
            try:
                requested_collection = Collection.objects.get(id=data.get('id'))
                serializedCollection  = CollectionSerializer(requested_collection, many=False)
                return Response({'collection': serializedCollection.data}, status=200)
            except:
                return Response({'collection': False}, status=500)


class GetUsers(APIView):
    permission_classes = [DenyAnonymousPermission, OnlyAdmin]
    def get(self, request, *args, **kwargs):
        users = get_user_model().objects.all()
        serialized_data = UserSerializer(users, many=True)
        return Response({'users': serialized_data.data}, status=200)
    
class CollectionsForAdmins(APIView):
    permission_classes = [DenyAnonymousPermission]
    def get(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        if data:
            try:
                requested_collection = Collection.objects.get(id=data.get('id'))
                serializedCollection  = CollectionSerializer(requested_collection, many=False)
                return Response({'collection': serializedCollection.data}, status=200)
            except:
                return Response({'result': False}, status=500)
            
class BlockUser(APIView):
    permission_classes = [DenyAnonymousPermission, OnlyAdmin]
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        selfDestroyed = False
        if data and data.get('id_list'):
            try:
                IDs = data.get('id_list')
                for each in IDs:
                    requested_user = get_user_model().objects.get(id=each)
                    if requested_user == request.user:
                        selfDestroyed = not selfDestroyed
                    requested_user.is_active = False
                    requested_user.save()
                updated_users = get_user_model().objects.all()
                serializedData = UserSerializer(updated_users, many=True)
                return Response({'updated_users': serializedData.data, 'selfDestroyed':selfDestroyed}, status=200)
            except:
                return Response({'result': False}, status=500)
        else:
            return Response({'result': False}, status=500)
        
class UnBlockUser(APIView):
    permission_classes = [DenyAnonymousPermission, OnlyAdmin]
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        if data and data.get('id_list'):
            try:
                IDs = data.get('id_list')
                for each in IDs:
                    requested_user = get_user_model().objects.get(id=each)
                    requested_user.is_active = True
                    requested_user.save()
                updated_users = get_user_model().objects.all()
                serializedData = UserSerializer(updated_users, many=True)
                return Response({'updated_users': serializedData.data}, status=200)
            except:
                return Response({'result': False}, status=500)
        else:
            return Response({'result': False}, status=500)

class DeleteUser(APIView):
    permission_classes = [DenyAnonymousPermission, OnlyAdmin]
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        selfDestroyed = False
        if data and data.get('id_list'):
            try:
                IDs = data.get('id_list')
                for each in IDs:
                    requested_user = get_user_model().objects.get(id=each)
                    if requested_user == request.user:
                        selfDestroyed = not selfDestroyed
                    requested_user.delete()
                updated_users = get_user_model().objects.all()
                serializedData = UserSerializer(updated_users, many=True)
                return Response({'updated_users': serializedData.data, 'selfDestroyed':selfDestroyed}, status=200)
            except:
                return Response({'result': False}, status=500)
        else:
            return Response({'result': False}, status=500)

class Login(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        if data and data.get('email'):
            try:    
                email = data.get('email')
                password = data.get('password')
                user = get_user_model().objects.get(email=email)
                if user.check_password(password):
                    key, token = Token.objects.get_or_create(user=user)
                    return Response({'token': str(key), 'is_admin': user.admin}, status=200)
                else:
                    return Response({'error': 'invalid credentials'}, status=500)
            except:
                return Response({'error': 'something wrong'}, status=500)
        else:
            return Response({'error': 'something wrong'}, status=500)

class CheckAdmin(APIView):
    permission_classes  = [DenyAnonymousPermission] 
    def get(self, request, *args, **kwargs):
        statusCode = 200 if (request.user.admin and request.user.is_active) else 500
        return Response(status=statusCode)

class GrantAdmin(APIView):
    permission_classes  = [DenyAnonymousPermission, OnlyAdmin] 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        selfDestroyed = False
        if data and data.get('id_list'):
            try:
                IDs = data.get('id_list')
                for each in IDs:
                    requested_user = get_user_model().objects.get(id=each)
                    if requested_user == request.user:
                        selfDestroyed = not selfDestroyed
                    requested_user.admin = True
                    requested_user.save()
                updated_users = get_user_model().objects.all()
                serializedData = UserSerializer(updated_users, many=True)
                return Response({'updated_users': serializedData.data, 'selfDestroyed':selfDestroyed}, status=200)
            except:
                return Response({'result': False}, status=500)
        else:
            return Response({'result': False}, status=500)

class RemoveAdmin(APIView):
    permission_classes  = [DenyAnonymousPermission, OnlyAdmin] 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if request.body else None
        selfDestroyed = False
        if data and data.get('id_list'):
            try:
                IDs = data.get('id_list')
                for each in IDs:
                    requested_user = get_user_model().objects.get(id=each)
                    if requested_user == request.user:
                        selfDestroyed = not selfDestroyed
                    requested_user.admin = False
                    requested_user.save()
                updated_users = get_user_model().objects.all()
                serializedData = UserSerializer(updated_users, many=True)
                return Response({'updated_users': serializedData.data, 'selfDestroyed':selfDestroyed}, status=200)
            except:
                return Response({'result': False}, status=500)
        else:
            return Response({'result': False}, status=500)