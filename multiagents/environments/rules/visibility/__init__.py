from typing import Dict

from multiagents.registry import Registry

visibility_registry = Registry(name="VisibilityRegistry")

from .base import BaseVisibility
from .all import AllVisibility
from .oneself import OneselfVisibility