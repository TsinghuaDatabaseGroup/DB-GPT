from multiagents.registry import Registry
order_registry = Registry(name="OrderRegistry")

from .base import BaseOrder
from .sequential import SequentialOrder
from .random import RandomOrder
from .concurrent import ConcurrentOrder