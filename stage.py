import mwparserfromhell
from mwbot import utils
from mwbot.arktool_internet import arktool as att
from jinja2 import Environment
from pathlib import Path
from src.utils import *


def cell_deal_token(data: dict) -> dict:
    charinfo = character_table[data["inst"]["characterKey"]]
    result = {}
    result["装置名称"] = char.get_char_name(data["inst"]["characterKey"])

    # 能从json中直接获取的内容
    if data["inst"]["level"]:
        result["装置等级"] = data["inst"]["level"]
    if data.get("initialCnt"):
        result["装置可部署数量"] = data["initialCnt"]
    if data.get("skillIndex") != None and data["skillIndex"] != -1:
        charskillid_local = charinfo["skills"][data["skillIndex"]]["skillId"]
        result["装置技能"] = return_skill_name(charskillid_local)
    if data.get("mainSkillLvl"):
        result["技能等级"] = data["mainSkillLvl"]
    # 需要与static内容联动的内容
    # 处理一下装置到底用不用
    if result["name"] in unwritetraps:
        return {
            "type": "不需要写入页面的装置",
            "text": clean_text(TEMPLATES.render(T_NAME="trapper.jinja2", **result)),
        }
    else:
        if result["name"] in trapsformat.keys():
            trap_s_format = trapsformat[str(result["name"])]
            print(trap_s_format)
            traptype = trap_s_format["type"]
            addition_text = [f"|{k}={v}" for k,v in trap_s_format["params"].items()]
            result["附加文本"] = "\n".join(addition_text)
        else:
            traptype = "未分类装置"
            result["附加文本"] = ""
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
                hint.append(f"没有获取到tile [{i['tileKey']}]的应用！<br/>")
                continue
    if text_list:
        tiletext = clean_list_and_return_str(text_list)
        return tiletext
    else:
        return ""


async def return_text(pagetext: str):
    global unwritetiles, tilesformat, character_table, trapsformat, unwritetraps
    global skill_table, env, TEMPLATES, new_tiles_table, arktool, hint, char
    arktool = att()
    # 首先处理stage
    stage_id = arktool.get_stage_id(content=pagetext)
    if stage_id:
        ... # continue
    else:
        return {"status": False, "text": wikicode, "hint": ""}
    # 然后再开始获取数据
    character_table = await arktool.read_ark_file("excel/character_table.json")
    skill_table = await arktool.read_ark_file("excel/skill_table.json")
    env = Environment(variable_start_string="{$", variable_end_string="$}")
    TEMPLATES = utils.templates_env(
        DIR_PATH=str(Path(__file__).parent / "templates"),
        variable_start_string="{$",
        variable_end_string="$}",
    )
    new_tiles_table = {}
    unwritetiles = await read_prts_static_json("特殊地形/trapper/unwritetiles.json")
    tilesformat = await read_prts_static_json("特殊地形/trapper/tilesformat.json")
    unwritetraps = await read_prts_static_json("模板:关卡装置/trapper/unwritetraps.json")
    trapsformat = await read_prts_static_json("模板:关卡装置/trapper/trapsformat.json")
    hint = []
    wikicode = pagetext[:]
    try:
        stageinfo = await arktool.get_stage_info(content=pagetext)
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
            return {"status": True, "text": wikicode, "hint": hint}
        else:
            return {"status": False, "text": wikicode, "hint": hint}
    except Exception as e:
        import traceback
        traceback.print_exc()
        hint.append(f"关卡出现bug！<br/>{e}")
        hint = "\n".join(list(set(hint)))
        return {"status": False, "text": pagetext, "hint": hint}
