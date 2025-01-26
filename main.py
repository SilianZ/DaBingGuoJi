from loguru import logger
import sys
from aiohttp import FormData
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import re
import random

logger.remove()
logger.add(sys.stdout, level="DEBUG")
logger.opt(ansi=True)

async def login(cellphone: str, password: str) -> str:
    """登录并返回 Cookie"""
    data = FormData()
    data.add_field("cellphone", cellphone)
    data.add_field("password", password)
    data.add_field("method", "doLogin")
    data.add_field("controller", "dbgj.UserController")
    
    async with aiohttp.ClientSession("https://dabingguoji.com/") as session:
        response = await session.post("/dbgj/*.do", data=data)
        data = json.loads(await response.text())
        if "data" not in data:
            logger.error("登陆失败。")
            raise ValueError("Login failed")
        return response.headers.get("Set-Cookie", "").split("; ")[0]

async def parse_url() -> str:
    """解析 URL 并返回 Unit ID"""
    while True:
        url = input("请输入打卡页面的完整链接（URL），完成后按下 <Enter>：")
        match = re.match(r"^(https?://[^\s]+/unitInfo/(\d+)\.html)$", url)
        if match:
            logger.success("成功解析 URL！")
            return match.group(2)
        else:
            logger.error("错误的 URL 格式，请重新输入！")

async def generate_random_time() -> int:
    """生成随机时间"""
    return random.randint(120, 150)

async def score(unit: str, cookie: str) -> None:
    """提交答题数据并保存成绩"""
    async with aiohttp.ClientSession("https://dabingguoji.com/") as session:
        session.headers["Cookie"] = cookie
        response = await session.get(f"/dbgj/*.do?controller=dbgj.word.WordLearnController&method=getUnitInfo&unitId={unit}")
        data = json.loads(await response.text(encoding="utf-8"))
        
        sentence_list: List[Dict[str, str]] = data["data"]["sentenceList"]
        word_list: List[Dict[str, str]] = data["data"]["wordList"]
        questions: List[Dict[str, Any]] = []

        for sentence in sentence_list:
            filtered_list = list(filter(lambda x: x["Word"] != sentence["matchWord"], word_list))
            random_words = random.sample(filtered_list, 3)
            words = [word["Word"] for word in random_words] + [sentence["matchWord"]]
            
            question: Dict[str, Any] = {
                "id": sentence["wordId"],
                "type": 4,
                "tigan": sentence["sentence_kong"],
                "answer": sentence["matchWord"],
                "userAnswer": sentence["matchWord"],
                "options": words,
                "isRight": True,
                "isChange": -1
            }
            questions.append(question)

        data = FormData()
        data.add_field("controller", "dbgj.word.WordLearnController")
        data.add_field("method", "addTongguanRecord")
        data.add_field("detail", json.dumps(questions))
        data.add_field("unitId", unit)
        data.add_field("startTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        seconds = await generate_random_time()
        data.add_field("useTime", str(seconds))
        data.add_field("endTime", (datetime.now() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S"))
        data.add_field("typeFlag", "1")
        data.add_field("score", "200")
        data.add_field("wrongCount", "0")
        data.add_field("rightCount", "20")

        response = await session.post("/dbgj/*.do", data=data)
        data = json.loads(await response.text())
        if "data" in data:
            logger.success(f"单元 {unit} 通过成功！按下 Ctrl + C 以终止程序。")

async def main() -> None:
    try:
        # 用户输入
        cellphone = input("请输入你的手机号码，完成后按下 <Enter>：")
        password = input("请输入你的密码，完成后按下 <Enter>：")
        crazy_mode = input("是否开启疯狂模式？(yes/no)，完成后按下 <Enter>：").strip().lower()
        
        # 登录
        cookie = await login(cellphone, password)
        logger.success("登陆成功！")

        # 开启疯狂模式
        if crazy_mode == "yes":
            unit = await parse_url()
            unit = int(unit)
            count = int(input("请输入你希望完成的单元数（不能超过该单词模块的数量），完成后按下 <Enter>："))
            for i in range(unit, unit + count):
                await score(str(i), cookie)
        else:
            unit = await parse_url()
            await score(unit, cookie)

    except Exception:
        logger.info("正在退出程序……")

if __name__ == "__main__":
    logger.info("正在启动程序……")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
