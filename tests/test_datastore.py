import pytest
from finn_codesubmit.datastore import InMemoryDataStore


@pytest.fixture
def datastore():
    return InMemoryDataStore()


@pytest.mark.asyncio
async def test_double_insert_raises_key_error(datastore):
    # Arrange
    key = "my_key"
    value1 = "my_value1"
    value2 = "my_value2"

    # Act
    await datastore.insert(key, value1)

    # Assert
    with pytest.raises(KeyError):
        await datastore.insert(key, value2)
