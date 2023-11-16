import json
from datetime import datetime
from .models import Collection, Tag

def processTag(tagName):
    return tagName.capitalize()

class dataManager:
    @staticmethod
    def sort_item_data(collection_instance, data):
        try:
            name = data.get('name', None)
            tags = data.get('tags', None)
            customFields = data.get('additionalFields', None)
            valid_customFields = checkData(collection_instance, customFields) if customFields else {}
            tag_instances = []
            if name and collection_instance:
                    for eachTag in tags:
                        addedTag = Tag.objects.get_or_create(name=processTag(eachTag))
                        tag_instances.append(addedTag[0])
                    return {'name':name, 'collection':collection_instance, 'additional_field_data': valid_customFields}, tag_instances
            else:
                return False, False
        except:
            return False, False
        
def checkData(structureInstance, data):
    structure = structureInstance.custom_fields if structureInstance.custom_fields else []
    
    structure_dict = {key: value for key, value in structure}

    if not any(key in data for key in structure_dict):
        return False
    
    for key, value_type in structure:
        if key in data:
            if value_type.lower() == 'string' and not isinstance(data[key], str):
                return False

    return data



def extract_collection_fields(model_instance):
    custom_fields = model_instance.custom_fields if model_instance.custom_fields else []
    return custom_fields

def save_custom_field(model_instance, field_name, field_data_type, value):
    custom_fields = model_instance.custom_fields if model_instance.custom_fields else []

    if field_data_type == 'integer':
        value = int(value)
    elif field_data_type == 'boolean':
        value = bool(value)
    elif field_data_type == 'date':
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d')
    elif field_data_type == 'string':

        if not isinstance(value, str):
            value = str(value)

    custom_field = [field_name, field_data_type, value]
    custom_fields.append(custom_field)
    model_instance.custom_fields = custom_fields
    model_instance.save()

def extract_custom_fields(model_instance, *args, **kwargs):
    custom_fields = model_instance.custom_fields if model_instance.custom_fields else []
    extracted_fields = {}

    # Extract each custom field and its data
    for field in custom_fields:
        field_name, field_data_type, value = field

        # Convert data to appropriate Python types
        if field_data_type == 'integer':
            value = int(value) if value is not None else None
        elif field_data_type == 'boolean':
            value = bool(value) if value is not None else None
        elif field_data_type == 'date':
            value = datetime.strptime(value, '%Y-%m-%d')

        extracted_fields[field_name] = value

    return extracted_fields