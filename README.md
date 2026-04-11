# 维吉尼亚加密存储系统

一个基于维吉尼亚密码的持久化数据存储与检索系统，提供高度可扩展的加密接口和友好的命令行交互体验。

## 项目特点

- 🔐 **安全加密**：基于经典维吉尼亚密码，支持多密钥
- 💾 **持久存储**：使用 diskcache 存储，数据不丢失
- 🔧 **高度可扩展**：轻松接入自定义加密算法
- 🖥️ **友好交互**：支持单行/多行输入，操作便捷
- 🧪 **完整测试**：覆盖核心功能的单元测试

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动加密程序

```bash
python encrypt_cli.py
```

启动后会显示当前加密算法信息：

```
=== 加密存储程序 ===
----------------------------------------
算法: Vigenere
简介: 经典多表替换加密算法，密文全大写输出
密钥数量: 1
密钥说明:
  [1] 加密关键词（字母组成）
作者: Blaise de Vigenère
----------------------------------------

命令: add <索引> <密钥> [数据], get <索引>, list, delete <索引>, ciphers, use <算法名>, info, quit
提示: add 后若无数据则进入多行模式（Ctrl+Z 结束）
```

---

## 加密程序使用指南

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `add <索引> <密钥> [数据]` | 加密并存储数据 | `add A8sK2 KEY HELLO WORLD` |
| `get <索引>` | 获取加密后的密文 | `get A8sK2` |
| `list` | 列出所有存储的索引 | `list` |
| `delete <索引>` | 删除指定索引的数据 | `delete A8sK2` |
| `ciphers` | 查看可用加密算法 | `ciphers` |
| `use <算法名>` | 切换加密算法 | `use vigenere` |
| `info` | 查看当前算法信息 | `info` |
| `quit` | 退出程序 | `quit` |

### 单行模式（推荐）

直接在命令行输入完整数据：

```
> add test genshin This is a test message!
已加密存储: 索引=test, 密钥数量=1
```

**特点**：
- 空格会被保留作为数据的一部分
- 适合短文本快速加密

### 多行模式

适合加密长文本或代码：

```
> add longtext mykey
（多行输入模式，按 Ctrl+Z 回车结束）
这是第一行
这是第二行
第三行可以包含代码: print("hello")
^Z
已加密存储: 索引=longtext, 密钥数量=1
（包含 3 行）
```

**操作步骤**：
1. 输入 `add <索引> <密钥>`（不输入数据）
2. 按回车进入多行模式
3. 输入多行内容
4. 按 `Ctrl+Z` 然后回车结束输入

### 多密钥加密

使用逗号分隔多个密钥：

```
> add secure key1,key2,key3 Top Secret Data
已加密存储: 索引=secure, 密钥数量=3
```

---

## 解密程序使用指南

### 启动解密程序

```bash
python decrypt_cli.py
```

### 从数据库解密（推荐）

```
=== 解密程序 ===
----------------------------------------
算法: Vigenere
...
----------------------------------------

命令: get <索引>, list, quit 退出, ciphers 查看算法, use <算法名> 切换, info 查看当前算法

> get test
密文: RIJVS AZWMCZ
密钥> genshin
解密结果: this is a test message!
(使用 1 个密钥)
```

### 列出所有索引

```
> list
已存储 3 条数据:
  test
  longtext
  secure
```

### 直接解密密文

也可以直接输入密文进行解密：

```
> RIJVS GSPVH
密钥> KEY
解密结果: hello world
(使用 1 个密钥)
```

---

## 扩展开发

### 自定义加密算法

实现 `Cipher` 抽象基类，添加算法元信息：

```python
from core.cipher import Cipher, CipherInfo, registry
from typing import Sequence


class MyCipher(Cipher):
    """自定义加密算法示例"""
    
    # 定义算法元信息
    info = CipherInfo(
        name="MyCipher",
        description="我的自定义加密算法",
        key_count=2,  # 需要2个密钥
        key_meanings=["主密钥", "盐值"],
        author="Your Name"
    )

    def encrypt(self, plaintext: str, keys: Sequence[str]) -> str:
        """加密逻辑"""
        key1, key2 = keys[0], keys[1]
        # 你的加密逻辑...
        return encrypted_text

    def decrypt(self, ciphertext: str, keys: Sequence[str]) -> str:
        """解密逻辑"""
        key1, key2 = keys[0], keys[1]
        # 你的解密逻辑...
        return decrypted_text


# 注册到全局注册中心
registry.register("my_cipher", MyCipher())

# 设置为默认加密器
registry.set_default("my_cipher")
```

### 注册中心 API

```python
from core.cipher import registry

# 查看所有已注册的加密器
registry.list_ciphers()  # ['vigenere', 'my_cipher']

# 获取指定加密器
cipher = registry.get("vigenere")

# 获取默认加密器
cipher = registry.get_default()

# 获取算法元信息
info = registry.get_info("vigenere")
print(info.format_info())

# 设置默认加密器
registry.set_default("vigenere")

# 注销加密器
registry.unregister("my_cipher")
```

### 替换存储后端

`Storage` 类可替换为其他持久化方案（SQLite、Redis 等），只需实现相同接口：

```python
class MyStorage:
    def save(self, index: str, ciphertext: str) -> None: ...
    def get(self, index: str) -> str | None: ...
    def list_indexes(self) -> list[str]: ...
    def delete(self, index: str) -> bool: ...
    def count(self) -> int: ...
```

---

## 项目结构

```
gyic-vigenere-encrypt/
├── core/
│   ├── __init__.py
│   ├── cipher.py          # 加密器抽象接口 + 注册中心 + Vigenere实现
│   ├── storage.py         # diskcache 存储封装
│   └── exceptions.py      # 自定义异常
├── tests/
│   ├── test_cipher.py     # 加密器测试（46+ 测试用例）
│   └── test_storage.py    # 存储测试
├── encrypt_cli.py         # 加密存储程序
├── decrypt_cli.py         # 解密程序
├── requirements.txt       # 依赖列表
└── README.md              # 本文件
```

---

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行加密器测试
python -m pytest tests/test_cipher.py -v

# 运行存储测试
python -m pytest tests/test_storage.py -v
```

---

## 技术细节

### Vigenere 加密特性

- **密文输出**：全部转为大写字母
- **特殊字符**：数字、空格、标点符号保持不变
- **密钥处理**：自动忽略密钥中的非字母字符
- **解密输出**：全部转为小写字母

示例：
```
原文: Hello World! 123
密钥: KEY
密文: RIJVS GSPVH! 123
解密: hello world! 123
```

### 存储特性

- 使用 diskcache 进行本地文件存储
- 自动创建 `cache` 目录存放数据
- 支持至少 1000 条数据存储
- 索引唯一性校验（不允许重复索引）

---

## 功能清单

- [x] 数据加密存储（单/多行输入）
- [x] 索引快速检索
- [x] 持久化存储（程序关闭后数据不丢失）
- [x] 支持至少 1000 条数据
- [x] 索引唯一性校验
- [x] 极度可扩展的加密器接口
- [x] 加密器注册中心（动态切换算法）
- [x] 多密钥支持
- [x] 算法元信息显示
- [x] 完整的单元测试
- [x] 加密/解密双程序支持

---

## 许可证

MIT License
