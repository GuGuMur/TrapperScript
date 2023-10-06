import mwparserfromhell
from httpx import AsyncClient
from mwbot import utils
from mwbot.arktool_internet import arktool as att
from jinja2 import Environment
from pathlib import Path


async def read_static_file(name: str):
    domains = [
        "https://raw.githubusercontent.com",
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


def return_skill_name(skillId: str) -> str:
    return skill_table[skillId]["levels"][0]["name"]


def get_char_name(id: str) -> str:
    return character_table[id]["name"]


def cell_deal_token(data: dict) -> dict:
    charinfo = character_table[data["inst"]["characterKey"]]
    result = {}
    result["name"] = get_char_name(data["inst"]["characterKey"])

    # 能从json中直接获取的内容
    if data["inst"]["level"]:
        result["level"] = data["inst"]["level"]
    if data.get("initialCnt"):
        result["initialCnt"] = data["initialCnt"]
    if data.get("skillIndex") != None and data["skillIndex"] != -1:
        charskillid_local = charinfo["skills"][data["skillIndex"]]["skillId"]
        result["skill"] = return_skill_name(charskillid_local)
    if data.get("mainSkillLvl"):
        result["skillLevel"] = data["mainSkillLvl"]
    # 需要与static内容联动的内容
    # 处理一下装置到底用不用
    if result["name"] in unwritetraps:
        return {
            "type": "不需要写入页面的装置",
            "text": clean_text(TEMPLATES.render(T_NAME="trapper.jinja2", **result)),
        }
    else:
        if trapsformat.get(result["name"], False):
            trap_s_format = trapsformat[result["name"]]
            traptype = trap_s_format["type"]
            addition_text = [f"|{i['param']}={i['content']}" for i in trap_s_format["params"]]
            result["addition"] = "\n".join(addition_text)
        else:
            traptype = "未分类装置"
            result["addition"] = ""
        return {
            "type": traptype,
            "text": clean_text(TEMPLATES.render(T_NAME="trapper.jinja2", **result)),
        }


def deal_token(stageinfo: dict) -> str:
    traptext: [str, list[str]] = {}
    result_text: str = ""
    mainparams = ["predefines", "hardPredefines"]
    subparams = ["tokenInsts", "tokenCards"]

    for maintitle in mainparams:
        if subdict := stageinfo.get(maintitle, False):
            for subtitle in subparams:
                if nextdict := subdict.get(subtitle, False):
                    for t in nextdict:
                        cell_trap_info = cell_deal_token(data=t)
                        if traptext.get(cell_trap_info["type"], False):
                            traptext[cell_trap_info["type"]].append(cell_trap_info["text"])
                        else:
                            traptext[cell_trap_info["type"]] = [cell_trap_info["text"]]
            # for k,v in stageinfo[maintitle].items():
            #     #k=["characterInsts","tokenInsts","characterCards","tokenCards"]
            #     if v:
            #         for t in v:
    if traptext:
        for k, v in traptext.items():
            result_text += f"=={k}==\n" + "\n".join(list(set(v)))
            result_text += "\n"
        return clean_text(result_text)
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
                hint.append(f"没有获取到tile [{i['tileKey']}]的应用！")
                continue
    if text_list:
        tiletext = clean_list_and_return_str(text_list)
        return tiletext
    else:
        return ""


deal_key = lambda key: key.replace("[", "__").replace("]", "__").replace(".", "__")


async def return_text(pagetext: str):
    global unwritetiles, tilesformat, character_table, trapsformat, unwritetraps
    global skill_table, env, TEMPLATES, new_tiles_table, arktool, hint
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
    unwritetraps = await read_static_file("unwritetraps.json")
    tilesformat = await read_static_file("tilesformat.json")
    trapsformat = await read_static_file("trapsformat.json")
    hint = []
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
        hint = "\n".join(list(set(hint)))
        if pagetext != wikicode:
            print({"status": True, "text": wikicode, "hint": hint})
        else:
            return {"status": False, "text": wikicode, "hint": hint}
    except Exception as e:
        hint.append(f"关卡出现bug！{e}")
        hint = "\n".join(list(set(hint)))
        return {"status": False, "text": pagetext, "hint": hint}
