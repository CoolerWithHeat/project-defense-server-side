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
            valid_customFields = customFields
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

    for field in custom_fields:
        field_name, field_data_type = field
        if field_data_type == 'integer':
            value = int(value) if value is not None else None
        elif field_data_type == 'boolean':
            value = bool(value) if value is not None else None
        elif field_data_type == 'date':
            value = datetime.strptime(value, '%Y-%m-%d')

        extracted_fields[field_name] = value

    return extracted_fields

def validate_custom_fields(data):
    if not isinstance(data, list):
        return False  # Ensure the received data is a list

    for field in data:
        if not isinstance(field, list):
            return False  # Each field should be a list
        
        # Ensure the first element in the inner list is a string (field name)
        if not isinstance(field[0], str):
            return False

        # No restriction on the second element, it can be any data type
        if len(field) < 2:
            return False  # Each field should have at least two elements

    return True  # If all checks pass, return True