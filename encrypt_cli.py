"""
加密存储程序

提供数据加密、存储、检索功能的命令行交互程序。

功能:
    - add: 添加数据（加密后存储）
    - get: 检索数据（返回密文）
    - list: 列出所有索引
    - delete: 删除数据
    - cipher: 切换加密算法
    - quit: 退出程序

使用方式:
    python encrypt_cli.py
    > add A8sK2 KEY HELLO WORLD
    > add A8sK3 KEY (然后输入多行，按 Ctrl+Z 结束)
    > get A8sK2
    > list
    > delete A8sK2
"""

import sys
from core.cipher import registry
from core.exceptions import DuplicateIndexError, IndexNotFoundError
from core.storage import Storage


def parse_keys(key_input: str) -> list[str]:
    """
    解析密钥输入，支持单密钥或多密钥

    多密钥用逗号分隔，例如: "key1,key2,key3"

    Args:
        key_input: 密钥输入字符串

    Returns:
        密钥列表
    """
    keys = [k.strip() for k in key_input.split(",")]
    return [k for k in keys if k]


def show_cipher_info() -> None:
    """显示当前加密算法信息"""
    info = registry.get_default_info()
    print("-" * 40)
    print(info.format_info())
    print("-" * 40)


def read_multiline_input() -> str:
    """
    读取多行输入，直到遇到 Ctrl+Z（Windows）

    Returns:
        多行输入的文本
    """
    print("（多行输入模式，按 Ctrl+Z 回车结束）")
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


def main() -> None:
    """
    加密存储程序主入口

    初始化加密器和存储实例，进入命令行交互循环。
    支持添加、检索、列出、删除加密数据，以及切换加密算法。
    """
    storage = Storage()

    print("\n=== 加密存储程序 ===")
    show_cipher_info()
    print("\n命令: add <索引> <密钥> [数据], get <索引>, list, delete <索引>, ciphers, use <算法名>, info, quit")
    print("提示: add 后若无数据则进入多行模式（Ctrl+Z 结束）")

    while True:
        try:
            cmd = input("\n> ").strip()
            if not cmd:
                continue

            parts = cmd.split(maxsplit=3)
            action = parts[0].lower()

            if action == "quit":
                print("退出程序")
                break

            if action == "info":
                show_cipher_info()
                continue

            if action == "ciphers":
                ciphers = registry.list_ciphers()
                print(f"可用加密算法: {', '.join(ciphers)}")
                continue

            if action == "use":
                if len(parts) < 2:
                    print("用法: use <算法名>")
                    continue
                name = parts[1]
                try:
                    registry.set_default(name)
                    print("已切换加密算法")
                    show_cipher_info()
                except KeyError as e:
                    print(f"错误: {e}")
                continue

            if action == "add":
                if len(parts) < 3:
                    print("用法: add <索引> <密钥> [数据]")
                    print("提示: add A8sK2 key1,key2 数据 或 add A8sK2 key (多行模式)")
                    continue

                index = parts[1]
                key_input = parts[2]
                keys = parse_keys(key_input)

                if len(parts) == 4:
                    data = parts[3]
                else:
                    data = read_multiline_input()

                cipher = registry.get_default()
                ciphertext = cipher.encrypt(data, keys)
                storage.save(index, ciphertext)
                print(f"已加密存储: 索引={index}, 密钥数量={len(keys)}")
                if "\n" in data:
                    print(f"（包含 {data.count(chr(10)) + 1} 行）")

            elif action == "get":
                if len(parts) < 2:
                    print("用法: get <索引>")
                    continue
                index = parts[1]
                ciphertext = storage.get(index)
                if ciphertext is None:
                    print(f"索引 '{index}' 不存在")
                else:
                    print(f"密文: {ciphertext}")

            elif action == "list":
                indexes = storage.list_indexes()
                if not indexes:
                    print("暂无存储数据")
                else:
                    print(f"已存储 {storage.count()} 条数据:")
                    for idx in indexes:
                        print(f"  {idx}")

            elif action == "delete":
                if len(parts) < 2:
                    print("用法: delete <索引>")
                    continue
                index = parts[1]
                storage.delete(index)
                print(f"已删除索引: {index}")

            else:
                print(f"未知命令: {action}")

        except DuplicateIndexError as e:
            print(f"错误: {e}")
        except IndexNotFoundError as e:
            print(f"错误: {e}")
        except KeyError as e:
            print(f"错误: {e}")
        except KeyboardInterrupt:
            print("\n退出程序")
            break


if __name__ == "__main__":
    main()
