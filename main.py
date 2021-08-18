from concurrent.futures import ThreadPoolExecutor
from ProxyPool import ProxyPool
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 工作线程
def work(i):
    # 提取IP
    ip = proxy_pool.pop()
    logger.info(f"{i}: {ip}")
    # 模拟工作
    time.sleep(3)


# 初始化线程池
thread_pool = ThreadPoolExecutor(max_workers=10)
# 初始化ip代理池
proxy_pool = ProxyPool(proxy_url="http://127.0.0.1/extract", threshold=20, hp=3)
for index in range(100):
    thread_pool.submit(work, index)

# 等待线程池结束
thread_pool.shutdown()
