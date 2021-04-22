class State(object):
    """
    A class holding state information

    Attributes:
        element (NamedTuple): The last found element coordinates
        map_images (dict): A dictionary holding label and filepath for images
    """
    _initialized = False

    def __init__(self):
        self.element = None
        self.map_images = dict()


class SingleState(State):
    """
    Singleton class holding state information
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleState, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self._initialized:
            super(SingleState, self).__init__(*args, **kwargs)
            self._initialized = True
