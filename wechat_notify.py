#!/usr/bin/env python3
"""Server酱(方糖)微信推送 - 替换企业微信推送
通过环境变量 SENDKEY 读取 Server酱 SendKey，把签到结果推送到个人微信。
未配置该环境变量时，send_markdown 会直接返回 False，不影响主流程。
Server酱文档: https://sct.ftqq.com/
"""
import logging
import os
import requests

logger = logging.getLogger(__name__)

SEND_BASE = "https://sctapi.ftqq.com"


def get_sendkey() -> str:
    """从环境变量读取 Server酱 SendKey。"""
    return os.environ.get("SENDKEY", "").strip()


def send_markdown(content: str, key: str | None = None) -> bool:
    """发送 markdown 消息到个人微信。

    Args:
        content: markdown 文本。
        key: 可选的 SendKey；若不传则从环境变量读取。

    Returns:
        是否发送成功。未配置 Key 或网络异常时返回 False。
    """
    key = (key or "").strip() or get_sendkey()
    if not key:
        logger.info("未配置 SENDKEY，跳过微信推送")
        return False
    # 第一行去掉 # 后作为标题，其余作为正文
    lines = content.strip().split("\n", 1)
    title = (lines[0].replace("#", "").strip())[:64] or "贴吧签到结果"
    desp = lines[1].strip() if len(lines) > 1 else ""
    payload = {"title": title}
    if desp:
        payload["desp"] = desp
    url = f"{SEND_BASE}/{key}.send"
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code", -1) != 0:
            logger.error(f"Server酱推送失败: code={data.get('code')} message={data.get('message')}")
            return False
        logger.info("Server酱推送成功")
        return True
    except Exception as e:
        logger.error(f"Server酱推送异常: {e}")
        return False
