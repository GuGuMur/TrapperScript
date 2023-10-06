import argparse
from mwbot import Bot
import asyncio
from pathlib import Path


async def main(password:str):
    bot = Bot(
        sitename="PRTS",
        api="https://prts.wiki/api.php",
        index="https://prts.wiki/index.php",
        username="GuBot",
        password=password,
    )
    await bot.login()
    jspath = str (Path(__file__).parent / "main.js" )
    js = Path(jspath).read_text()
    ori = await bot.get_page_text("User:GuBot/trapper.js")
    if js == ori:
        print("PASS")
    else:
        await bot.edit_page(title="User:GuBot/trapper.js",text=js,summary="//Edit by GithubActionBot.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='update js')
    parser.add_argument('password')
    args = parser.parse_args()
    asyncio.get_event_loop().run_until_complete(main(password=args.password))
