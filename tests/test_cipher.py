import pytest
from core.cipher import Cipher, CipherInfo, CipherRegistry, VigenereCipher, registry


class TestCipherInfo:
    def test_format_info_basic(self) -> None:
        info = CipherInfo(
            name="Test",
            description="Test cipher"
        )
        result = info.format_info()
        assert "算法: Test" in result
        assert "简介: Test cipher" in result
        assert "密钥数量: 1" in result

    def test_format_info_with_keys(self) -> None:
        info = CipherInfo(
            name="MultiKey",
            description="Multi-key cipher",
            key_count=3,
            key_meanings=["主密钥", "盐值", "初始向量"]
        )
        result = info.format_info()
        assert "密钥数量: 3" in result
        assert "[1] 主密钥" in result
        assert "[2] 盐值" in result
        assert "[3] 初始向量" in result

    def test_format_info_variable_keys(self) -> None:
        info = CipherInfo(
            name="Variable",
            description="Variable key cipher",
            key_count=-1
        )
        result = info.format_info()
        assert "支持可变数量密钥" in result

    def test_format_info_with_author(self) -> None:
        info = CipherInfo(
            name="Test",
            description="Test",
            author="Test Author"
        )
        result = info.format_info()
        assert "作者: Test Author" in result


class TestVigenereCipher:
    @pytest.fixture
    def cipher(self) -> VigenereCipher:
        return VigenereCipher()

    def test_encrypt_returns_uppercase(self, cipher: VigenereCipher) -> None:
        result = cipher.encrypt("hello", ["KEY"])
        assert result.isupper() or not result  # 密文全大写

    def test_encrypt_preserves_non_alpha_chars(self, cipher: VigenereCipher) -> None:
        result = cipher.encrypt("hello world! 123", ["KEY"])
        assert result == "RIJVS GSPVH! 123"
        assert " " in result
        assert "!" in result
        assert "123" in result

    def test_encrypt_preserves_spaces_and_punctuation(self, cipher: VigenereCipher) -> None:
        plaintext = "HELLO WORLD 123!"
        key = ["KEY"]
        encrypted = cipher.encrypt(plaintext, key)
        assert " " in encrypted
        assert "123" in encrypted
        assert "!" in encrypted

    def test_decrypt_roundtrip(self, cipher: VigenereCipher) -> None:
        plaintext = "HELLO"
        key = ["KEY"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert decrypted == plaintext.lower()

    def test_decrypt_lowercase_output(self, cipher: VigenereCipher) -> None:
        ciphertext = "RIJVS"
        result = cipher.decrypt(ciphertext, ["KEY"])
        assert result.islower()

    def test_roundtrip_hello_world(self, cipher: VigenereCipher) -> None:
        plaintext = "HELLO WORLD"
        key = ["KEY"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert decrypted == "hello world"

    def test_roundtrip_lowercase(self, cipher: VigenereCipher) -> None:
        plaintext = "hello world"
        key = ["password"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert decrypted == plaintext

    def test_roundtrip_mixed_case(self, cipher: VigenereCipher) -> None:
        plaintext = "HeLLo WoRLd"
        key = ["Key"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert decrypted == plaintext.lower()

    def test_empty_plaintext(self, cipher: VigenereCipher) -> None:
        result = cipher.encrypt("", ["KEY"])
        assert result == ""

    def test_empty_key(self, cipher: VigenereCipher) -> None:
        result = cipher.encrypt("HELLO", [])
        assert result == "HELLO"

    def test_non_alpha_preserved(self, cipher: VigenereCipher) -> None:
        plaintext = "HELLO WORLD 123!"
        key = ["KEY"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert "hello world 123!" == decrypted

    def test_multiple_keys_uses_first(self, cipher: VigenereCipher) -> None:
        plaintext = "TEST"
        encrypted = cipher.encrypt(plaintext, ["KEY1", "KEY2"])
        decrypted = cipher.decrypt(encrypted, ["KEY1", "KEY2"])
        assert decrypted == plaintext.lower()

    def test_key_with_non_alpha_chars(self, cipher: VigenereCipher) -> None:
        plaintext = "HELLO"
        key = ["K3Y"]
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        assert decrypted == plaintext.lower()

    def test_cipher_info_exists(self, cipher: VigenereCipher) -> None:
        assert hasattr(cipher, "info")
        assert cipher.info.name == "Vigenere"
        assert cipher.info.key_count == 1

    def test_encrypt_special_chars_not_changed(self, cipher: VigenereCipher) -> None:
        plaintext = "ABC@#$%123"
        encrypted = cipher.encrypt(plaintext, ["KEY"])
        assert "@" in encrypted
        assert "#" in encrypted
        assert "$" in encrypted
        assert "%" in encrypted
        assert "123" in encrypted

    def test_decrypt_special_chars_not_changed(self, cipher: VigenereCipher) -> None:
        ciphertext = "ABCD@#$%"
        decrypted = cipher.decrypt(ciphertext, ["KEY"])
        assert "@" in decrypted
        assert "#" in decrypted
        assert "$" in decrypted
        assert "%" in decrypted


class TestCipherRegistry:
    @pytest.fixture
    def empty_registry(self) -> CipherRegistry:
        return CipherRegistry()

    def test_register_cipher(self, empty_registry: CipherRegistry) -> None:
        cipher = VigenereCipher()
        empty_registry.register("test", cipher)
        assert "test" in empty_registry.list_ciphers()

    def test_get_cipher(self, empty_registry: CipherRegistry) -> None:
        cipher = VigenereCipher()
        empty_registry.register("test", cipher)
        result = empty_registry.get("test")
        assert result is cipher

    def test_get_nonexistent_raises(self, empty_registry: CipherRegistry) -> None:
        with pytest.raises(KeyError) as exc_info:
            empty_registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_first_registered_becomes_default(self, empty_registry: CipherRegistry) -> None:
        cipher = VigenereCipher()
        empty_registry.register("first", cipher)
        assert empty_registry.get_default() is cipher

    def test_set_default(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("cipher1", VigenereCipher())
        empty_registry.register("cipher2", VigenereCipher())
        empty_registry.set_default("cipher2")
        assert empty_registry.get_default() is empty_registry.get("cipher2")

    def test_set_default_nonexistent_raises(self, empty_registry: CipherRegistry) -> None:
        with pytest.raises(KeyError):
            empty_registry.set_default("nonexistent")

    def test_get_default_empty_raises(self, empty_registry: CipherRegistry) -> None:
        with pytest.raises(KeyError):
            empty_registry.get_default()

    def test_list_ciphers(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("a", VigenereCipher())
        empty_registry.register("b", VigenereCipher())
        ciphers = empty_registry.list_ciphers()
        assert len(ciphers) == 2
        assert "a" in ciphers
        assert "b" in ciphers

    def test_unregister(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("test", VigenereCipher())
        result = empty_registry.unregister("test")
        assert result is True
        assert "test" not in empty_registry.list_ciphers()

    def test_unregister_nonexistent(self, empty_registry: CipherRegistry) -> None:
        result = empty_registry.unregister("nonexistent")
        assert result is False

    def test_unregister_default_updates_default(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("a", VigenereCipher())
        empty_registry.register("b", VigenereCipher())
        empty_registry.set_default("a")
        empty_registry.unregister("a")
        assert empty_registry.get_default() is empty_registry.get("b")

    def test_get_info(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("test", VigenereCipher())
        info = empty_registry.get_info("test")
        assert info.name == "Vigenere"

    def test_get_default_info(self, empty_registry: CipherRegistry) -> None:
        empty_registry.register("test", VigenereCipher())
        info = empty_registry.get_default_info()
        assert info.name == "Vigenere"


class TestGlobalRegistry:
    def test_vigenere_registered(self) -> None:
        ciphers = registry.list_ciphers()
        assert "vigenere" in ciphers

    def test_get_vigenere(self) -> None:
        cipher = registry.get("vigenere")
        assert isinstance(cipher, VigenereCipher)

    def test_default_is_vigenere(self) -> None:
        cipher = registry.get_default()
        assert isinstance(cipher, VigenereCipher)
