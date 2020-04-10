class MockStorage:
    def get(self, key, name):
        print("{} - retrieving {} - {}".format(self.__class__.__name__, key, name))
        return []

    def save(self, key, name, value=None):
        print("{} - saving {} - {}".format(self.__class__.__name__, key, name, value))
        return True
    
    def record_exists(self, *args, **kwargs):
        return False
