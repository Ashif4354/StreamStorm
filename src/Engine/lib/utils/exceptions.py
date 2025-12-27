
class ElementNotFound(Exception):
    pass

class BrowserClosedError(Exception):
    pass

__all__: list[str] = ['ElementNotFound', 'BrowserClosedError']