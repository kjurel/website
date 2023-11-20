from pydantic.dataclasses import dataclass


@dataclass
class File:
    name: str
    path: str
    import_string: str
