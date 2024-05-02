from multiagents.registry import Registry

selector_registry = Registry(name="SelectorRegistry")

from .base import BaseSelector
from .basic import BasicSelector