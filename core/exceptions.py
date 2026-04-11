"""
异常模块

定义加密程序中使用的自定义异常类。
"""


class CipherError(Exception):
    """
    加密程序基础异常类

    所有加密相关的异常都继承此类。
    """

    pass


class DuplicateIndexError(CipherError):
    """
    重复索引异常

    当尝试保存已存在的索引时抛出。

    Attributes:
        index: 重复的索引字符串
    """

    def __init__(self, index: str):
        """
        初始化重复索引异常

        Args:
            index: 重复的索引字符串
        """
        self.index = index
        super().__init__(f"索引 '{index}' 已存在，不允许重复")


class IndexNotFoundError(CipherError):
    """
    索引不存在异常

    当尝试获取或删除不存在的索引时抛出。

    Attributes:
        index: 不存在的索引字符串
    """

    def __init__(self, index: str):
        """
        初始化索引不存在异常

        Args:
            index: 不存在的索引字符串
        """
        self.index = index
        super().__init__(f"索引 '{index}' 不存在")


class DecryptionError(CipherError):
    """
    解密失败异常

    当解密过程中发生错误时抛出。
    """

    def __init__(self, reason: str = "解密失败"):
        """
        初始化解密失败异常

        Args:
            reason: 解密失败的原因描述
        """
        super().__init__(reason)
