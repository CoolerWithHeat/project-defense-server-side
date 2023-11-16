class GoogleResponseParser:
    def __init__(self, data_file):
        self.data_file = data_file


    @property
    def get_FirstName(self):
        raw_data = self.data_file['google']['user']['displayName']
        processed = raw_data.split(' ')
        return processed[0]

    @property
    def get_LastName(self):
        raw_data = self.data_file['google']['user']['displayName']
        processed = raw_data.split(' ')
        return processed[1]

    @property
    def get_EmailAdress(self):
        return self.data_file['google']['user']['email']
    

    @property
    def get_PHOTO_url(self):
        return self.data_file['google']['user']['photoURL']
    
    @property
    def get_PhoneNumber(self):
        return self.data_file['google']['user']['providerData'][0]['phoneNumber']
    
class FacebookResponseParser:
    def __init__(self, data_file):
        self.data_file = data_file


    @property
    def get_FirstName(self):
        raw_data = self.data_file['facebook']['user']['displayName']
        processed = raw_data.split(' ')
        return processed[0]

    @property
    def get_LastName(self):
        raw_data = self.data_file['facebook']['user']['displayName']
        processed = raw_data.split(' ')
        return processed[1]

    @property
    def get_EmailAdress(self):
        return self.data_file['facebook']['user']['providerData'][0]['email']
    

    @property
    def get_PHOTO_url(self):
        return self.data_file['facebook']['user']['photoURL']
    
    @property
    def get_PhoneNumber(self):
        return self.data_file['facebook']['user']['providerData'][0]['phoneNumber']