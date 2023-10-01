import re, mwparserfromhell
from httpx import AsyncClient
from mwbot import utils
from mwbot.arktool_internet import arktool as att
from jinja2 import Environment
from loguru import logger
from pathlib import Path


async def read_static_file(name: str):
    domains = [
        "https://raw.kgithub.com/",
        "https://ghproxy.com/https://raw.githubusercontent.com/",
        "https://fastly.jsdelivr.net/gh/",
        "https://cdn.staticaly.com/gh/",
        "https://ghproxy.net/https://raw.githubusercontent.com/",
        "https://gcore.jsdelivr.net/gh/",
        "https://jsdelivr.b-cdn.net/gh/",
    ]

    async with AsyncClient() as client:
        for i in domains:
            try:
                res = await client.get(f"{i}GuGuMur/GuBot-PRTS-static/main/{name}")
                return res.json()
            except:
                pass


def clean_list_and_return_str(li: list) -> str:
    return "\n".join(map(str, list(set(li))))


def clean_text(text: str):
    lines = text.strip().split("\n")
    cleaned_lines = [line.strip() for line in lines if line]
    result = "\n".join(cleaned_lines)
    return result


def return_skill_name(skillId: str):
    return skill_table[skillId]["levels"][0]["name"]

def get_char_name(self, id: str) -> str:
    return character_table[id]["name"]

def cell_deal_token(data: dict):
    charinfo = character_table[data["inst"]["characterKey"]]
    result = {}
    result["name"] = get_char_name(data["inst"]["characterKey"])
    if data["inst"]["level"]:
        result["level"] = data["inst"]["level"]
    if data.get("initialCnt"):
        result["initialCnt"] = data["initialCnt"]
    if data.get("skillIndex") != None and data["skillIndex"] != -1:
        charskillid_local = charinfo["skills"][data["skillIndex"]]["skillId"]
        result["skill"] = return_skill_name(charskillid_local)
    if data.get("mainSkillLvl"):
        result["skillLevel"] = data["mainSkillLvl"]
    return TEMPLATES.render(T_NAME="trapper.jinja2", **result)


async def deal_token(stageinfo: dict) -> str:
    traptext = []
    mainparams = ["predefines", "hardPredefines"]
    subparams = ["tokenInsts", "tokenCards"]

    def return_dict_if_exist(key, dic):
        if key in dic:
            return dic[key]
        else:
            return False

    for maintitle in mainparams:
        if subdict := return_dict_if_exist(maintitle, stageinfo):
            for subtitle in subparams:
                if nextdict := return_dict_if_exist(subtitle, subdict):
                    for t in nextdict:
                        traptext.append(f"{await cell_deal_token(data=t)}")

            # for k,v in stageinfo[maintitle].items():
            #     #k=["characterInsts","tokenInsts","characterCards","tokenCards"]
            #     if v:
            #         for t in v:
    if traptext:
        traptext = "== 未分类装置 ==\n" + "\n".join(list(set(traptext)))
        return clean_text(traptext)
    else:
        return ""


def deal_tiles(stageinfo: dict):
    text_list = []
    for i in stageinfo["mapData"]["tiles"]:
        # 处理新tiles
        if i["tileKey"] not in unwritetiles:
            # 选择tile的处理方式
            if i["tileKey"] in tilesformat:
                template = env.from_string(tilesformat[i["tileKey"]])
                if i["blackboard"]:
                    data = {
                        deal_key(cell["key"]): cell["value"] for cell in i["blackboard"]
                    }
                else:
                    data = {}
                text = template.render(**data)
                text_list.append(text)
            # else:
            #     continue
            else:
                logger.warning(f"{i['tileKey']} NOT FOUND USAGE!")
                continue
    if text_list:
        tiletext = clean_list_and_return_str(text_list)
        return tiletext
    else:
        return ""


deal_key = lambda key: key.replace("[", "__").replace("]", "__").replace(".", "__")


async def return_text(pagetext: str):
    global unwritetiles, tilesformat, character_table
    global skill_table, env, TEMPLATES, new_tiles_table, arktool
    arktool = att(
        domains=[
            "https://raw.githubusercontent.com",
            "https://raw.kgithub.com/",
            "https://ghproxy.com/https://raw.githubusercontent.com/",
            "https://fastly.jsdelivr.net/gh/",
            "https://cdn.staticaly.com/gh/",
            "https://ghproxy.net/https://raw.githubusercontent.com/",
            "https://gcore.jsdelivr.net/gh/",
            "https://jsdelivr.b-cdn.net/gh/",
        ]
    )
    character_table = await arktool.read_ark_file("excel/character_table.json")
    skill_table = await arktool.read_ark_file("excel/skill_table.json")
    env = Environment(variable_start_string="{$", variable_end_string="$}")
    TEMPLATES = utils.templates_env(
        DIR_PATH=str(Path(__file__).parent / "templates"),
        variable_start_string="{$",
        variable_end_string="$}",
    )
    new_tiles_table = {}
    unwritetiles = await read_static_file("unwritetiles.json")
    tilesformat = await read_static_file("tilesformat.json")
    wikicode = pagetext[:]
    try:
        stageinfo = await arktool.get_stage_info(pagetext)
        tiletext = deal_tiles(stageinfo=stageinfo)
        tokentext = deal_token(stageinfo=stageinfo)

        if tokentext:
            if "==作战进度奖励==" in wikicode:
                wikicode = wikicode.replace("==作战进度奖励==", f"{tokentext}\n==作战进度奖励==")
            elif "==材料掉落==" in wikicode:
                wikicode = wikicode.replace("==材料掉落==", f"{tokentext}\n==材料掉落==")
            else:
                wikicode = wikicode.replace("==注释与链接==", f"{tokentext}\n==注释与链接==")
        else:
            pass
        # --------------------------------------------------
        if tiletext:
            wikicode = mwparserfromhell.parse(wikicode)
            for template in wikicode.filter_templates():
                if template.name.matches("普通关卡信息") or template.name.matches("剿灭关卡信息"):
                    template.add("特殊地形效果", f"{tiletext}")
                    continue
            wikicode = str(wikicode)
        else:
            pass
        # FINALLY!
        if pagetext != wikicode:
            return {"status": True, "text": wikicode}
        else:
            return {"status": True, "text": wikicode}
    except Exception as e:
        logger.warning(f"关卡出现bug！{e}")
        return {"status": False, "text": pagetext}
