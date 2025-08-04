class NamespaceMeta(type):
    __ns__: str

    def __getattr__(cls, item: str) -> str:
        return "{" + cls.__ns__ + "}" + item

    def __getitem__(cls, item: str) -> str:
        return "{" + cls.__ns__ + "}" + item


class Namespace(metaclass=NamespaceMeta):
    pass


class xsi(Namespace):
    __ns__ = "http://www.w3.org/2001/XMLSchema-instance"


class premis(Namespace):
    __ns__ = "http://www.loc.gov/premis/v3"


class mods(Namespace):
    __ns__ = "http://www.loc.gov/mods/v3"


class schema(Namespace):
    __ns__ = "https://schema.org/"


class dcterms(Namespace):
    __ns__ = "http://purl.org/dc/terms/"
