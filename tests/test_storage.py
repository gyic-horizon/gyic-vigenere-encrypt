import pytest
import shutil
from pathlib import Path
from core.storage import Storage
from core.exceptions import DuplicateIndexError, IndexNotFoundError


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> str:
    cache_dir = str(tmp_path / ".cache")
    yield cache_dir
    shutil.rmtree(cache_dir, ignore_errors=True)


@pytest.fixture
def storage(temp_cache_dir: str) -> Storage:
    return Storage(temp_cache_dir)


class TestStorage:
    def test_save_and_get(self, storage: Storage) -> None:
        storage.save("A8sK2", "encrypted_data_1")
        result = storage.get("A8sK2")
        assert result == "encrypted_data_1"

    def test_save_duplicate_index_raises(self, storage: Storage) -> None:
        storage.save("A8sK2", "data1")
        with pytest.raises(DuplicateIndexError) as exc_info:
            storage.save("A8sK2", "data2")
        assert "A8sK2" in str(exc_info.value)

    def test_get_nonexistent_index(self, storage: Storage) -> None:
        result = storage.get("nonexistent")
        assert result is None

    def test_list_indexes(self, storage: Storage) -> None:
        storage.save("index1", "data1")
        storage.save("index2", "data2")
        indexes = storage.list_indexes()
        assert len(indexes) == 2
        assert "index1" in indexes
        assert "index2" in indexes

    def test_delete_existing_index(self, storage: Storage) -> None:
        storage.save("A8sK2", "data")
        result = storage.delete("A8sK2")
        assert result is True
        assert storage.get("A8sK2") is None

    def test_delete_nonexistent_index_raises(self, storage: Storage) -> None:
        with pytest.raises(IndexNotFoundError) as exc_info:
            storage.delete("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_count_empty(self, storage: Storage) -> None:
        assert storage.count() == 0

    def test_count_after_save(self, storage: Storage) -> None:
        storage.save("index1", "data1")
        storage.save("index2", "data2")
        assert storage.count() == 2

    def test_count_after_delete(self, storage: Storage) -> None:
        storage.save("index1", "data1")
        storage.save("index2", "data2")
        storage.delete("index1")
        assert storage.count() == 1

    def test_persistence_across_instances(self, temp_cache_dir: str) -> None:
        storage1 = Storage(temp_cache_dir)
        storage1.save("persistent", "data")

        storage2 = Storage(temp_cache_dir)
        assert storage2.get("persistent") == "data"
        assert storage2.count() == 1
