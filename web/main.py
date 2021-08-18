#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/10 16:39
# @Author  : likai
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @contact: likai5.@thewesthill.net
from flask import Flask, request
import time
import random

app = Flask(__name__)

# 存储用户帐号
USER = {"minami373": 0}


class TokenError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def _dict(self):
        return {"code": 500, "msg": self.msg}


class SpeedError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def _dict(self):
        return {"code": 500, "msg": self.msg}


# 改主意了，太麻烦直接用帐号好了
def decode_token(token: str):
    try:
        time_stamp = int(token[-13:])
    except Exception:
        raise TokenError("token解析错误")
    if time.time() * 1000 - time_stamp < 2 * 1000:
        raise SpeedError("速度过快")
    return token[:-13] + str(int(time.time() * 1000))


@app.post("/extract")
def extract():
    data = request.json
    token = data.get("token")
    # if token is None:
    #     return {"code": 500, "msg": "token不存在"}
    # try:
    #     token = decode_token(token)
    # except Exception as e:
    #     return e._dict()

    # 获取帐号对应的提取时间
    ex_time = USER[token]
    # 计算提取时间间隔
    if time.time() - ex_time < 2:
        return {"code": 500, "msg": "提取间隔过短"}
    # 重新为用户赋值提取时间
    ex_time = time.time()
    USER[token] = ex_time

    # 获取提取数量
    try:
        num = int(data.get("num"))
    except Exception:
        return {"code": 500, "msg": "num必须是数字"}
    if num <= 0 or num > 50:
        return {"code": 500, "msg": "num必须大于0小于50"}

    # 生成IP
    data = []
    for i in range(num):
        data.append(
            f"{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}")
    return {"code": 200, "token": token, "data": data}


# 太麻烦了，直接用帐号提取
@app.post("/login")
def login():
    data = request.json
    name = data.get("name")
    if name is None:
        return {"code": 500, "msg": "name不能为空"}
    data = {"token": name + str(int(time.time() * 1000) - 2 * 1000)}
    return data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
