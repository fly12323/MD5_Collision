# MD5_Collision
MD5碰撞
## 简介

MD5 Collision Toolkit 是一个用于进行 MD5 碰撞查找和攻击的工具。它支持多种模式，包括单次 MD5 碰撞、两次 MD5 碰撞、拼接后缀的 MD5 碰撞、强碰撞以及 MD5 长度扩展攻击。

## 功能特点

* **单次 MD5 碰撞**：查找以指定前缀开头的 MD5 哈希的随机字符串。
* **两次 MD5 碰撞**：查找以指定前缀开头的 MD5 哈希，并且该哈希的再次 MD5 哈希也以相同前缀开头。
* **拼接后缀的 MD5 碰撞**：查找以指定前缀开头的 MD5 哈希的随机字符串，并拼接指定的后缀。
* **强碰撞**：使用 fastcoll 工具生成两个具有相同 MD5 哈希的不同消息。
* **MD5 长度扩展攻击**：基于已知的哈希值和消息长度，扩展消息并计算新的哈希值。

## 使用方法

### 安装

确保你已经安装了 Python 3，并且系统上安装了必要的依赖项。对于强碰撞功能，需要确保 fastcoll 工具的路径正确。

### 运行

在命令行中运行以下命令：

```bash
python3 md5_collision.py -m [mode] [其他参数]
```

### 参数说明

| 参数                | 选项                                   | 描述                                                                                                                                      |
| --------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| -m, --mode          | single, double, suffix, strong, extend | 模式：single 表示单次 MD5 碰撞，double 表示两次 MD5 碰撞，suffix 表示拼接后缀的 MD5 碰撞，strong 表示强碰撞，extend 表示 MD5 长度扩展攻击 |
| -s, --substr        |                                        | 目标 MD5 前缀（如 0e）                                                                                                                    |
| -p, --start\_pos |                                        | 起始位置（默认为 0）                                                                                                                      |
| -l, --length        |                                        | 生成随机字符串的长度（默认为 20）                                                                                                         |
| -f, --suffix        |                                        | 拼接的后缀字符串（仅在 suffix 模式下需要）                                                                                                |
| -c, --prefix        |                                        | 强碰撞模式下字符串的前缀                                                                                                                  |

### 示例

#### 单次 MD5 碰撞

```bash
python3 md5_collision.py -m single -s 0e -p 0 -l 20
```

输出示例：

`找到符合条件的字符串：AbK5UgrvLMmn1AMLbdn2 => 0ed9a2e5cea0a208bf1d4efae3ca68e7`

#### 两次 MD5 碰撞

```bash
python3 md5_collision.py -m double -s 0e -p 0 -l 20
```

输出示例：

`找到符合条件的字符串：7XYVCSsa101eqTr6IxyX => 0e3dd66594d9e82f5aea82c83b789b49 => 0e5e5a57f3bee382c1f4488fdb09b4d9`

#### 拼接后缀的 MD5 碰撞

```bash
python3 md5_collision.py -m suffix -s 91e0c -p 0 -l 20 -f 12ba
```

输出示例：

`找到符合条件的字符串：B5Ke2Jx1PJ22RsWZxDv6 (full)=> B5Ke2Jx1PJ22RsWZxDv612ba => 91e0c15e6b4ff26e89323bf784e089cf`

#### 强碰撞

bash复制

```bash
python3 md5_collision.py -m strong -c "prefix"
```

输出示例：

```
消息1 URL编码: ...
消息2 URL编码: ...
```

#### MD5 长度扩展攻击

```bash
python3 md5_collision.py -m extend
```

交互示例：

```
[>] Input known text length: 10
[>] Input known hash: 0e3dd66594d9e82f5aea82c83b789b49
[>] Input append text: test
[*] Attacking...
[+] Extend text: b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00test'
[+] Extend text (URL encoded): %80%00%00%00%00%00%00%00%00%00test
[+] Extend text (Base64): gAAAAAAAAAAAdGVzdA==
[+] Final hash: 0e5e5a57f3bee382c1f4488fdb09b4d9
```
