#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/18 11:10
# @Author  : likai
# @Site    : 
# @File    : ProxyPool.py
# @Software: PyCharm
# @contact: likai5.@thewesthill.net
import logging

import requests
from queue import PriorityQueue
import time
from threading import Lock

"""
1、到达阈值自动提取
2、过期时间验证
"""
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProxyPool:
    def __init__(self, proxy_url: str, interval: int = 2, threshold: int = 0, time_out: int = 60 * 5, hp: int = 1):
        """
        初始化代理池
        :param proxy_url: 代理请求api
        :param interval: 请求时间间隔(秒)
        :param threshold: 提取阈值(达到阈值会触发提取)
        :param time_out: 超时时间(秒)
        :param hp: 代理使用次数(生命值)
        """
        self._proxy_url = proxy_url
        self._interval = interval
        self._threshold = threshold
        self._time_out = time_out
        self._hp = hp
        self._queue = PriorityQueue(maxsize=0)

        # 上次提取时间
        self._last_ex_time = 0
        # 测试需要
        self._token = "minami373"

        self._lock = Lock()

    def __extract(self):
        """
        从API请求代理
        这个过程需要阻塞队列
        :return:
        """
        # 这里可以让其他线程不必等待锁，直接等待获取ip即可(能发挥阈值的作用)
        if not self._lock.acquire(blocking=False):
            logger.debug("已经有线程开始提取")
            return

        logger.debug("进入请求锁")

        # 检查是否已经提取过了
        if self._queue.qsize() > self._threshold:
            logger.debug("提前释放请求锁")
            self._lock.release()
            return

        # 判断是否需要等待请求间隔
        if self._last_ex_time != 0:
            sleep_time = time.time() - self._last_ex_time
            if sleep_time < 2:
                time.sleep(2 - sleep_time)

        # 开始请求代理
        data_ = {
            # 携带服务器返回的token
            "token": self._token,
            # 获取IP的个数
            "num": 10
        }
        data = requests.post(self._proxy_url, json=data_).json()
        if data['code'] != 200:
            # 请求失败,交由其他线程提取
            logger.debug("请求失败,提前释放请求锁")
            self._lock.release()
            return

        logger.debug("开始置入ip")

        # 代理入队列
        for i in data['data']:
            self._queue.put((time.time(), self._hp, i))

        logger.debug("置入ip完毕")

        # 记录请求时间
        self._last_ex_time = time.time()

        logger.debug("释放请求锁")

        self._lock.release()

    def pop(self):
        """
        获取一个代理
        """
        # 检查队列是否达到阈值
        if self._queue.qsize() <= self._threshold:
            logger.debug("触发提取阈值")
            # 锁一下请求ip的方法，防止重复请求(这里的锁最好放在方法内)
            # self._lock.acquire()
            self.__extract()
            # self._lock.release()

        # 从队列取出ip，并检查是否过期
        put_time, hp, ip = self._queue.get()
        if (time.time() - put_time) > self._time_out:
            logger.debug("ip超时")
            # 如果过期则递归调用
            ip = self.pop()

        # 检查ip使用次数是否超过设置次数
        if hp > 1:
            self._queue.put((put_time, hp - 1, ip))

        return ip
