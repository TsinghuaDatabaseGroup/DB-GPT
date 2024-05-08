from multiagents.registry import Registry

updater_registry = Registry(name="UpdaterRegistry")

from .base import BaseUpdater
from .basic import BasicUpdater