# -*- coding: utf-8 -*-

import multiprocessing
import hashlib
import random
import string
import sys
import argparse
import os
from time import sleep
from urllib.parse import quote

CHARS = string.ascii_letters + string.digits

def cmp_md5(substr, stop_event, str_len, start=0, size=20, is_double=False, suffix=None, strong_collision_prefix=None):
    global CHARS
    while not stop_event.is_set():
        rnds = ''.join(random.choice(CHARS) for _ in range(size))
        
        if strong_collision_prefix:
            # 强碰撞模式
            if rnds.startswith(strong_collision_prefix):
                md5 = hashlib.md5(rnds.encode('utf-8'))
                value = md5.hexdigest()
                print(f"找到符合条件的字符串：{rnds} => {value}")
                stop_event.set()
        elif suffix:
            rnds1 = rnds + suffix
            md5 = hashlib.md5(rnds1.encode('utf-8'))
            value = md5.hexdigest()
            if value[start: start+str_len] == substr:
                print(f"找到符合条件的字符串：{rnds} (full)=> {rnds1} => {value}")
                stop_event.set()
        else:
            md5 = hashlib.md5(rnds.encode('utf-8'))
            value = md5.hexdigest()
            if value[start: start+str_len] == substr:
                if is_double:
                    md5_second = hashlib.md5(value.encode('utf-8'))
                    if md5_second.hexdigest()[start: start+str_len] == substr:
                        print(f"找到符合条件的字符串：{rnds} => {value} => {md5_second.hexdigest()}")
                        stop_event.set()
                else:
                    print(f"找到符合条件的字符串：{rnds} => {value}")
                    stop_event.set()

def strong_collision(prefix):
    # 使用fastcoll工具进行强碰撞
    test_file = "test.txt"
    with open(test_file, "w") as fw:
        fw.write(prefix)
    
    # 调用fastcoll工具
    fastcoll_path = "/mnt/d/aCTF/Tool_Web/fastcoll/fastcoll_v1.0.0.5.exe"
    if not os.path.exists(fastcoll_path):
        print("fastcoll工具未找到，请检查路径")
        return
    
    os.system(f"{fastcoll_path} {test_file}")
    
    # 读取生成的消息
    try:
        with open("test_msg1.txt", "rb") as fr1:
            msg1 = fr1.read()
        with open("test_msg2.txt", "rb") as fr2:
            msg2 = fr2.read()
        
        # 输出URL编码结果
        print("消息1 URL编码:", quote(msg1))
        print("消息2 URL编码:", quote(msg2))
        
        # 清理临时文件
        os.remove(test_file)
        os.remove("test_msg1.txt")
        os.remove("test_msg2.txt")
    except FileNotFoundError:
        print("fastcoll工具运行失败，未生成消息文件")

def md5_extension_attack():
    from struct import pack, unpack
    from math import floor, sin

    class MD5:
        def __init__(self):
            self.A, self.B, self.C, self.D = \
                (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)  # initial values
            self.r: list[int] = \
                [7, 12, 17, 22] * 4 + [5,  9, 14, 20] * 4 + \
                [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4  # shift values
            self.k: list[int] = \
                [floor(abs(sin(i + 1)) * pow(2, 32))
                 for i in range(64)]  # constants

        def _lrot(self, x: int, n: int) -> int:
            # left rotate
            return (x << n) | (x >> 32 - n)

        def update(self, chunk: bytes) -> None:
            # update the hash for a chunk of data (64 bytes)
            w = list(unpack('<'+'I'*16, chunk))
            a, b, c, d = self.A, self.B, self.C, self.D

            for i in range(64):
                if i < 16:
                    f = (b & c) | ((~b) & d)
                    flag = i
                elif i < 32:
                    f = (b & d) | (c & (~d))
                    flag = (5 * i + 1) % 16
                elif i < 48:
                    f = (b ^ c ^ d)
                    flag = (3 * i + 5) % 16
                else:
                    f = c ^ (b | (~d))
                    flag = (7 * i) % 16

                tmp = b + \
                    self._lrot((a + f + self.k[i] + w[flag])
                               & 0xffffffff, self.r[i])
                a, b, c, d = d, tmp & 0xffffffff, b, c

            self.A = (self.A + a) & 0xffffffff
            self.B = (self.B + b) & 0xffffffff
            self.C = (self.C + c) & 0xffffffff
            self.D = (self.D + d) & 0xffffffff

        def extend(self, msg: bytes) -> None:
            # extend the hash with a new message (padded)
            assert len(msg) % 64 == 0
            for i in range(0, len(msg), 64):
                self.update(msg[i:i + 64])

        def padding(self, msg: bytes) -> bytes:
            # pad the message
            length = pack('<Q', len(msg) * 8)

            msg += b'\x80'
            msg += b'\x00' * ((56 - len(msg)) % 64)
            msg += length

            return msg

        def digest(self) -> bytes:
            # return the hash
            return pack('<IIII', self.A, self.B, self.C, self.D)

    def attack(message_len: int, known_hash: str, append_str: bytes) -> tuple:
        # MD5 extension attack
        md5 = MD5()

        previous_text = md5.padding(b"*" * message_len)
        current_text = previous_text + append_str

        md5.A, md5.B, md5.C, md5.D = unpack("<IIII", bytes.fromhex(known_hash))
        md5.extend(md5.padding(current_text)[len(previous_text):])

        return current_text[message_len:], md5.digest().hex()

    message_len = int(input("[>] Input known text length: "))
    known_hash = input("[>] Input known hash: ").strip()
    append_text = input("[>] Input append text: ").strip().encode()

    print("[*] Attacking...")

    extend_str, final_hash = attack(message_len, known_hash, append_text)

    from urllib.parse import quote
    from base64 import b64encode

    print("[+] Extend text:", extend_str)
    print("[+] Extend text (URL encoded):", quote(extend_str))
    print("[+] Extend text (Base64):", b64encode(extend_str).decode())
    print("[+] Final hash:", final_hash)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MD5 碰撞查找工具")
    parser.add_argument("-m", "--mode", choices=["single", "double", "suffix", "strong", "extend"], required=True, help="模式：single 表示单次 MD5 碰撞，double 表示两次 MD5 碰撞，suffix 表示拼接后缀的 MD5 碰撞，strong 表示强碰撞，extend 表示 MD5 长度扩展攻击")
    parser.add_argument("-s", "--substr", help="目标 MD5 前缀（如 0e）")
    parser.add_argument("-p", "--start_pos", type=int, default=0, help="起始位置（默认为 0）")
    parser.add_argument("-l", "--length", type=int, default=20, help="生成随机字符串的长度（默认为 20）")
    parser.add_argument("-f", "--suffix", help="拼接的后缀字符串（仅在 suffix 模式下需要）")
    parser.add_argument("-c", "--prefix", help="强碰撞模式下字符串的前缀")
    
    args = parser.parse_args()
    
    if args.mode == "strong":
        if not args.prefix:
            print("在 strong 模式下，必须指定 -c 参数")
            sys.exit(1)
        strong_collision(args.prefix)
    elif args.mode == "extend":
        md5_extension_attack()
    else:
        substr = args.substr.strip() if args.substr else ""
        start_pos = args.start_pos
        str_len = len(substr) if args.substr else 0
        is_double = args.mode == "double"
        string_length = args.length
        suffix = args.suffix if args.mode == "suffix" else None
        strong_collision_prefix = args.prefix if args.mode == "strong" else None
        
        if args.mode == "suffix" and not suffix:
            print("在 suffix 模式下，必须指定 -f 参数")
            sys.exit(1)
        
        if not args.substr and args.mode != "strong":
            print("在 single、double 模式下，必须指定 -s 参数")
            sys.exit(1)
        
        cpus = multiprocessing.cpu_count()
        stop_event = multiprocessing.Event()
        processes = [multiprocessing.Process(target=cmp_md5, args=(substr, stop_event, str_len, start_pos, string_length, is_double, suffix, strong_collision_prefix))
                     for i in range(cpus)]
        
        print(f"正在使用 {cpus} 个进程查找 MD5 碰撞...")
        for p in processes:
            p.start()
        for p in processes:
            p.join()
