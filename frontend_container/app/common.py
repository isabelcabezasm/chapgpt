from enum import Enum
import sys
from typing import Any
from azure.identity import DefaultAzureCredential
from cap import Cap

def log(message: str) -> None:
    print(message, file=sys.stderr)


def credentials() -> DefaultAzureCredential:
    return DefaultAzureCredential()


class Role(Enum):
    BOT = "BOT"
    USER = "user"


class Message:
    def __init__(self, role: Role, text_content: str) -> None:
        self.role = role
        self.text = text_content

# a message can be :
# - only text, 
# - an image from the user (uploaded image, or cropped cap), 
# - an image and a list of points from the bot (a cap in the image was found "between" these points)
# - a list of caps from the bot (a list of Caps objects)

class ImageMessage(Message):
    def __init__(self, role: Role, text_content: str, image: Any) -> None:
        super().__init__(role, text_content)
        self.image = image  # TODO: image now can be any format, change this to unify

class FoundCapMessage(Message):
    def __init__(self, role: Role, text_content: str, image: Any, points: list[int]) -> None:
        super().__init__(role, text_content)
        self.image = image
        self.points = points

class FoundSimilarCapsMessage(Message):
    def __init__(self, role: Role, text_content: str, caps: list[Cap]) -> None:
        super().__init__(role, text_content)
        self.caps = caps

class CapInformation(Message):
    def __init__(self, role: Role, text_content: str, cap: Cap) -> None:
        super().__init__(role, text_content)
        self.cap = cap