"""
加密器模块

提供加密器的抽象基类、内置实现和注册中心，支持用户自定义加密算法。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence


@dataclass
class CipherInfo:
    """
    加密器元信息

    Attributes:
        name: 加密器名称
        description: 简要描述
        key_count: 所需密钥数量（-1 表示可变数量）
        key_meanings: 各密钥的含义说明
        author: 作者（可选）
    """

    name: str
    description: str
    key_count: int = 1
    key_meanings: list[str] | None = None
    author: str | None = None

    def format_info(self) -> str:
        """
        格式化显示加密器信息

        Returns:
            格式化的信息字符串
        """
        lines = [f"算法: {self.name}"]
        lines.append(f"简介: {self.description}")

        if self.key_count == -1:
            lines.append("密钥: 支持可变数量密钥")
        else:
            lines.append(f"密钥数量: {self.key_count}")

        if self.key_meanings:
            lines.append("密钥说明:")
            for i, meaning in enumerate(self.key_meanings, 1):
                lines.append(f"  [{i}] {meaning}")

        if self.author:
            lines.append(f"作者: {self.author}")

        return "\n".join(lines)


class Cipher(ABC):
    """
    加密器抽象基类

    用户可继承此类实现自定义加密算法。
    支持单密钥或多密钥模式，通过 keys: Sequence[str] 参数传递。

    子类应实现:
        - encrypt(): 加密方法
        - decrypt(): 解密方法
        - info: CipherInfo 元信息

    Example:
        class MyCipher(Cipher):
            info = CipherInfo(
                name="my_cipher",
                description="自定义加密算法",
                key_count=2,
                key_meanings=["主密钥", "盐值"]
            )

            def encrypt(self, plaintext: str, keys: Sequence[str]) -> str:
                return encrypted_text

            def decrypt(self, ciphertext: str, keys: Sequence[str]) -> str:
                return decrypted_text
    """

    info: CipherInfo

    @abstractmethod
    def encrypt(self, plaintext: str, keys: Sequence[str]) -> str:
        """
        加密明文

        Args:
            plaintext: 待加密的明文字符串
            keys: 密钥序列，支持单密钥或多密钥
                  单密钥: ["mykey"]
                  多密钥: ["key1", "key2", "key3"]

        Returns:
            加密后的密文字符串
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str, keys: Sequence[str]) -> str:
        """
        解密密文

        Args:
            ciphertext: 待解密的密文字符串
            keys: 密钥序列，必须与加密时使用的密钥一致

        Returns:
            解密后的明文字符串
        """
        pass


class CipherRegistry:
    """
    加密器注册中心

    管理所有加密器的注册和获取，支持动态切换加密算法。

    Example:
        # 注册加密器
        registry = CipherRegistry()
        registry.register("vigenere", VigenereCipher())
        registry.register("my_cipher", MyCipher())

        # 获取加密器
        cipher = registry.get("vigenere")

        # 设置默认加密器
        registry.set_default("my_cipher")
        cipher = registry.get_default()
    """

    def __init__(self) -> None:
        """初始化注册中心"""
        self._ciphers: dict[str, Cipher] = {}
        self._default_name: str | None = None

    def register(self, name: str, cipher: Cipher) -> None:
        """
        注册加密器

        Args:
            name: 加密器名称
            cipher: 加密器实例
        """
        self._ciphers[name] = cipher
        if self._default_name is None:
            self._default_name = name

    def get(self, name: str) -> Cipher:
        """
        根据名称获取加密器

        Args:
            name: 加密器名称

        Returns:
            加密器实例

        Raises:
            KeyError: 加密器名称不存在
        """
        if name not in self._ciphers:
            raise KeyError(f"加密器 '{name}' 未注册，可用: {list(self._ciphers.keys())}")
        return self._ciphers[name]

    def get_default(self) -> Cipher:
        """
        获取默认加密器

        Returns:
            默认加密器实例

        Raises:
            KeyError: 未设置默认加密器
        """
        if self._default_name is None:
            raise KeyError("未设置默认加密器，请先注册加密器")
        return self._ciphers[self._default_name]

    def set_default(self, name: str) -> None:
        """
        设置默认加密器

        Args:
            name: 加密器名称

        Raises:
            KeyError: 加密器名称不存在
        """
        if name not in self._ciphers:
            raise KeyError(f"加密器 '{name}' 未注册")
        self._default_name = name

    def list_ciphers(self) -> list[str]:
        """
        列出所有已注册的加密器名称

        Returns:
            加密器名称列表
        """
        return list(self._ciphers.keys())

    def get_info(self, name: str) -> CipherInfo:
        """
        获取加密器元信息

        Args:
            name: 加密器名称

        Returns:
            加密器元信息
        """
        return self._ciphers[name].info

    def get_default_info(self) -> CipherInfo:
        """
        获取默认加密器元信息

        Returns:
            默认加密器元信息
        """
        return self._ciphers[self._default_name].info

    def unregister(self, name: str) -> bool:
        """
        注销加密器

        Args:
            name: 加密器名称

        Returns:
            注销成功返回 True，不存在返回 False
        """
        if name in self._ciphers:
            del self._ciphers[name]
            if self._default_name == name:
                self._default_name = next(iter(self._ciphers), None)
            return True
        return False


class VigenereCipher(Cipher):
    """
    维吉尼亚加密器

    经典的多表替换加密算法，使用关键词对明文进行加密。
    加密时原文不论大小写，密文全部转为大写；非字母字符保持不变。

    特性:
        - 加密后密文全大写
        - 非字母字符（数字、空格、标点）保持不变
        - 多密钥模式下仅使用第一个密钥
    """

    info = CipherInfo(
        name="Vigenere",
        description="经典多表替换加密算法，密文全大写输出",
        key_count=1,
        key_meanings=["加密关键词（字母组成）"],
        author="Blaise de Vigenère"
    )

    def encrypt(self, plaintext: str, keys: Sequence[str]) -> str:
        """
        使用维吉尼亚密码加密明文

        加密公式: C = (P + K) mod 26
        其中 P 为明文字母位置，K 为密钥字母位置
        密文输出全大写，非字母字符保持不变

        Args:
            plaintext: 待加密的明文
            keys: 密钥序列，仅使用第一个密钥

        Returns:
            加密后的密文（全部大写），非字母字符保持不变
        """
        if not plaintext:
            return ""

        key = keys[0] if keys else ""
        if not key:
            return plaintext

        key_chars = [c.upper() for c in key if c.isalpha()]
        if not key_chars:
            return plaintext

        key_len = len(key_chars)
        result = []

        for i, char in enumerate(plaintext):
            if char.isalpha():
                base = ord('A')
                shift = ord(key_chars[i % key_len]) - ord('A')
                encrypted = chr((ord(char.upper()) - base + shift) % 26 + base)
                result.append(encrypted)
            else:
                result.append(char)

        return "".join(result)

    def decrypt(self, ciphertext: str, keys: Sequence[str]) -> str:
        """
        使用维吉尼亚密码解密密文

        解密公式: P = (C - K + 26) mod 26
        其中 C 为密文字母位置，K 为密钥字母位置
        密文中的大写字母解密后转为小写，其余字符保持不变

        Args:
            ciphertext: 待解密的密文
            keys: 密钥序列，必须与加密时使用的密钥一致

        Returns:
            解密后的明文（小写输出），非字母字符保持不变
        """
        if not ciphertext:
            return ""

        key = keys[0] if keys else ""
        if not key:
            return ciphertext

        key_chars = [c.upper() for c in key if c.isalpha()]
        if not key_chars:
            return ciphertext

        key_len = len(key_chars)
        result = []

        for i, char in enumerate(ciphertext):
            if char.isalpha():
                base = ord('A')
                shift = ord(key_chars[i % key_len]) - ord('A')
                decrypted = chr((ord(char.upper()) - base - shift + 26) % 26 + ord('a'))
                result.append(decrypted)
            else:
                result.append(char)

        return "".join(result)


registry = CipherRegistry()
registry.register("vigenere", VigenereCipher())
