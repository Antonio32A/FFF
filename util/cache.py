class Cache:
    """
    A simple class for managing the bot cache
    """
    def __init__(self):
        self.data = {}

    def get(self):
        """
        Gets the cache
        :returns: (dict) cache
        """
        return self.data

    def set(self, data: dict):
        """
        Sets the cache to the value
        :param (dict) data: The data to set the cache to
        """
        self.data = data
