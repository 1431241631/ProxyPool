#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/10 16:43
# @Author  : likai
# @Site    : 
# @File    : test.py
# @Software: PyCharm
# @contact: likai5.@thewesthill.net
"""
游戏规则：
1、登录帐号
2、使用服务器返回的token获取IP
3、每次获取间隔不得小于2秒(服务器已经实现了对应的控制，如果你使用的是服务器返回的token，那你频繁的获取会被阻止)
4、IP有效时间为5分钟(无法验证，请自觉实现这个时间监控)
需求：
1、自己实现一个IP池
2、IP池需要可以实现自己过滤过期的IP
3、IP池可以置入和提取IP
4、提取的IP可以重复使用，也就是说IP池设置了一个IP可以被使用几次，那它应该可以被提取几次
5、它应该是线程安全的
"""
import requests

data = {
    # 登录的帐号，随便输入
    "name": "test"
}
# 登录
ret = requests.post("http://10.11.144.238/login", json=data).json()
print(ret)
# 获取返回的token，相当于令牌
token = ret['token']

data = {
    # 携带服务器返回的token
    "token": token,
    # 获取IP的个数
    "num": 10
}
# 从服务器获取IP
ret = requests.post("http://10.11.144.238/extract", json=data).json()
print(ret)
# 下次请求要使用返回的token，请遵守游戏规则
token = ret['token']
