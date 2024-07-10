from abc import ABC, abstractmethod
from typing import Any, Optional


class DataStore(ABC):
    """
    Abstract base class for a datastore that supports insertion and reading by key.

    This interface provides methods to insert a record with a given key and value into the datastore,
    check if a record with a given key exists in the datastore, and read the value of a record with
    a given key from the datastore.
    """

    @abstractmethod
    async def insert(self, key: str, value: Any) -> None:
        """
        Inserts a record with the given key and value into the datastore.

        Args:
            key: The key of the record.
            value: The value of the record.

        Raises:
            KeyError: If a record with the given key already exists in the datastore.
        """
        pass

    @abstractmethod
    async def read(self, key: str) -> Optional[Any]:
        """
        Reads the value of the record with the given key from the datastore.

        Args:
            key: The key of the record to read.

        Returns:
            The value of the record, or None if the record doesn't exist.
        """
        pass


class InMemoryDataStore(DataStore):
    """
    In-memory implementation of the DataStore interface.

    This implementation stores records in memory using a dictionary.
    """

    def __init__(self):
        self.data = {}

    async def insert(self, key: str, value: Any) -> None:
        """
        Inserts a record with the given key and value into the in-memory datastore.

        Args:
            key: The key of the record.
            value: The value of the record.

        Raises:
            KeyError: If a record with the given key already exists in the datastore.
        """
        if key in self.data:
            raise KeyError(f"Record with key '{key}' already exists.")
        self.data[key] = value

    async def read(self, key: str) -> Optional[Any]:
        """
        Reads the value of the record with the given key from the in-memory datastore.

        Args:
            key: The key of the record to read.

        Returns:
            The value of the record, or None if the record doesn't exist.
        """
        return self.data.get(key)
