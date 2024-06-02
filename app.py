from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from src.internet import return_text as rti
from src.local import return_text as rtl

app = FastAPI()

origins = [
    "https://prts.wiki"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": True, "message": "Hello!"}


@app.post("/main")
async def main(pagetext: str = Form()):
    return await rti(pagetext=pagetext)


@app.post("/mainlocal")
async def main(pagetext: str = Form()):
    return await rtl(pagetext=pagetext)


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
