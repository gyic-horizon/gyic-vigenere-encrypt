"""
存储模块

提供基于 diskcache 的持久化存储功能，支持数据的增删改查。
"""

from diskcache import Cache

from core.exceptions import DuplicateIndexError, IndexNotFoundError


class Storage:
    """
    持久化存储类

    基于 diskcache 实现的键值存储，支持数据的持久化保存。
    程序关闭后数据不丢失，重新打开仍可读取。

    Attributes:
        cache: diskcache.Cache 实例，用于实际存储数据

    Example:
        storage = Storage()
        storage.save("A8sK2", "encrypted_data")  # 保存数据
        data = storage.get("A8sK2")               # 获取数据
        storage.delete("A8sK2")                   # 删除数据
    """

    def __init__(self, cache_dir: str = ".cache"):
        """
        初始化存储实例

        Args:
            cache_dir: 缓存目录路径，默认为 ".cache"
                      数据将持久化存储在此目录中
        """
        self.cache = Cache(cache_dir)

    def save(self, index: str, ciphertext: str) -> None:
        """
        保存加密数据

        将密文与索引关联存储，索引必须唯一。

        Args:
            index: 索引字符串，用于检索数据
                   支持数字、大小写字母自由组合（如：123、gyhsic、A8sK2）
            ciphertext: 加密后的数据字符串

        Raises:
            DuplicateIndexError: 当索引已存在时抛出
        """
        if index in self.cache:
            raise DuplicateIndexError(index)
        self.cache[index] = ciphertext

    def get(self, index: str) -> str | None:
        """
        根据索引获取密文

        Args:
            index: 索引字符串

        Returns:
            加密后的数据字符串，如果索引不存在则返回 None
        """
        return self.cache.get(index)

    def list_indexes(self) -> list[str]:
        """
        列出所有索引

        Returns:
            所有已存储索引的列表
        """
        return list(self.cache.iterkeys())

    def delete(self, index: str) -> bool:
        """
        删除指定索引的数据

        Args:
            index: 要删除的索引字符串

        Returns:
            删除成功返回 True

        Raises:
            IndexNotFoundError: 当索引不存在时抛出
        """
        if index not in self.cache:
            raise IndexNotFoundError(index)
        del self.cache[index]
        return True

    def count(self) -> int:
        """
        获取存储的数据数量

        Returns:
            当前存储的数据条数
        """
        return len(self.cache)
