import os
from typing import Final

USER: Final[str] = os.getenv('USER', 'unknown')
