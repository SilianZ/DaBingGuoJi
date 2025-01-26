from logger import logger
from aiohttp import FormData
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import re
import random

async def main() -> None:
    try:
        cellphone = input("请输入你的手机号码，完成后按下 <Enter>：")
        password = input("请输入你的密码，完成后按下 <Enter>：")
        data = FormData()
        data.add_field("cellphone", cellphone)
        data.add_field("password", password)
        data.add_field("method", "doLogin")
        data.add_field("controller", "dbgj.UserController")
        cookie = ""
        async with aiohttp.ClientSession("https://dabingguoji.com/") as session:
            response = await session.post("/dbgj/*.do", data=data)
            data = json.loads(await response.text())
            if "data" not in data:
                logger.error("登陆失败。")
                raise asyncio.CancelledError
            cookie = response.headers.get("Set-Cookie", "").split("; ")[0]
        logger.success("登陆成功！")
        async def score() -> None:
            unit = ""
            while True:
                url = input("请输入打卡页面的完整链接（URL），完成后按下 <Enter>：")
                match = re.match(r"^(https?://[^\s]+/unitInfo/(\d+)\.html)$", url)
                if match:
                    logger.success("成功解析 URL！")
                    unit = match.group(2)
                    break
                else:
                    logger.error("错误的 URL 格式，请重新输入！")
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
                    words: List[str] = []
                    for word in random_words:
                        words.append(word["Word"])
                    words.append(sentence["matchWord"])
                    question: Dict[str, Any] = {}
                    question["id"] = sentence["wordId"]
                    question["type"] = 4
                    question["tigan"] = sentence["sentence_kong"]
                    question["answer"] = sentence["matchWord"]
                    question["userAnswer"] = sentence["matchWord"]
                    question["options"] = words
                    question["isRight"] = True
                    question["isChange"] = -1
                    questions.append(question)
                data = FormData()
                data.add_field("controller", "dbgj.word.WordLearnController")
                data.add_field("method", "addTongguanRecord")
                data.add_field("detail", json.dumps(questions))
                data.add_field("unitId", unit)
                data.add_field("startTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                seconds = random.randint(120, 150)
                data.add_field("useTime", str(seconds))
                data.add_field("endTime", (datetime.now() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S"))
                data.add_field("typeFlag", "1")
                data.add_field("score", "200")
                data.add_field("wrongCount", "0")
                data.add_field("rightCount", "20")
                response = await session.post("/dbgj/*.do", data=data)
                data = json.loads(await response.text())
                if "data" in data:
                    logger.success("通过成功！按下 Ctrl + C 以终止程序。")
        while True:
            await score()

    except Exception:
        logger.info("正在退出程序……")
        

if __name__ == "__main__":
    logger.info("正在启动程序……")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass 
    


