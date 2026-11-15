# Importing the model modules runs their class definitions,
# which registers each version in _REGISTRY (see base.py).
from dive.schemas import v1, v2

__all__ = ["v1", "v2"]
