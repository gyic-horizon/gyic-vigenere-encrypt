"""
解密程序

提供密文解密功能的命令行交互程序。

功能:
    - get: 从数据库读取密文并解密
    - 直接输入密文进行解密
    - 支持切换加密算法
    - 支持多密钥输入

使用方式:
    python decrypt_cli.py
    > get A8sK2
    > 密钥> KEY
    > 解密结果: hello world
"""

from core.cipher import registry
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


def main() -> None:
    """
    解密程序主入口

    初始化加密器和存储实例，进入命令行交互循环。
    支持从数据库读取密文或手动输入密文进行解密。
    """
    storage = Storage()

    print("\n=== 解密程序 ===")
    show_cipher_info()
    print("\n命令: get <索引>, list, quit 退出, ciphers 查看算法, use <算法名> 切换, info 查看当前算法")
    print("提示: 多密钥用逗号分隔，如: key1,key2,key3")

    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
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

            if action == "get":
                if len(parts) < 2:
                    print("用法: get <索引>")
                    continue
                index = parts[1]
                ciphertext = storage.get(index)
                if ciphertext is None:
                    print(f"索引 '{index}' 不存在")
                    continue

                print(f"密文: {ciphertext}")
                key_input = input("密钥> ").strip()
                if not key_input:
                    print("密钥不能为空")
                    continue

                keys = parse_keys(key_input)
                cipher = registry.get_default()
                plaintext = cipher.decrypt(ciphertext, keys)
                print(f"解密结果: {plaintext}")
                print(f"(使用 {len(keys)} 个密钥)")
                continue

            if action == "list":
                indexes = storage.list_indexes()
                if not indexes:
                    print("暂无存储数据")
                else:
                    print(f"已存储 {storage.count()} 条数据:")
                    for idx in indexes:
                        print(f"  {idx}")
                continue

            ciphertext = user_input
            key_input = input("密钥> ").strip()
            if not key_input:
                print("密钥不能为空")
                continue

            keys = parse_keys(key_input)
            cipher = registry.get_default()
            plaintext = cipher.decrypt(ciphertext, keys)
            print(f"解密结果: {plaintext}")
            print(f"(使用 {len(keys)} 个密钥)")

        except KeyboardInterrupt:
            print("\n退出程序")
            break


if __name__ == "__main__":
    main()
