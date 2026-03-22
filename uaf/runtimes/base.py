class BaseRuntime:
    def __init__(self, loader):
        self.loader = loader

    def load(self, **kwargs):
        raise NotImplementedError
