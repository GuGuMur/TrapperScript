from mwbot import Bot, utils
import asyncio
from stage.local import return_text as rtl
from stage.internet import return_text as rti

# 把这个文件移到根目录下跑

async def main():
    bot = Bot(
        sitename="PRTS",
        api="https://prts.wiki/api.php",
        index="https://prts.wiki/index.php",
        username="GuBot",
        password="Trapper@n1h0kq5c7r3t4ounha3obpv8r9c7n12q",
    )
    # await bot.login()
    # pagelist_ori = utils.get_all_links(content=await bot.get_page_text(title="首页/新增关卡"))
    # pagelist = sorted(list(set(pagelist_ori)), key=pagelist_ori.index)
    pagelist = [
        "RS-1 注意事项",
        "RS-2 同车异图",
        "RS-3 临时停车",
        "RS-4 重回正轨",
        "RS-ST-2 登山铁道",
        "RS-5 逃票？",
        "RS-6 补票！",
        "RS-7 制动失灵",
        "RS-8 极限时速",
        "RS-ST-3 终点站",
    ]
    for i in pagelist:
        text = await bot.get_page_text(title=i)
        a = await rti(pagetext=text)
        # a = a["text"]
        print(a)
        # if a != text:
        #     await bot.edit_page(title=i, text=a, summary="//Edit by TrapperScript-Local")


if __name__ == "__main__":
    asyncio.run(main())
