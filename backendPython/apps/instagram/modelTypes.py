import typing

Caption = typing.NewType("Caption", dict[str, list[str]])
Hashtags = typing.NewType("Hashtags", dict[str, list[str]])
Usertags = typing.NewType("Usertags", dict[str, int])
Location = typing.NewType("Location", dict[str, int])
