"""
AlcorCyclope Client Module
--------------------------

This module provides the `AlcorCyclopeClient` class, which facilitates
communication with the Alcor Cyclope server. The client enables connection
setup, command execution, measurement data retrieval, and system status
queries.

Example Usage:
--------------
```python
from alcor_cyclope import AlcorCyclopeClient

client = AlcorCyclopeClient("server_host")
client.connect()

status = client.get_status()
data = client.get_data()

client.close()
```
"""

from .client import AlcorCyclopeClient

__all__ = ["AlcorCyclopeClient"]
