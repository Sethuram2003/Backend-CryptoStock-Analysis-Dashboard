from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from app.core.Agent import chat_agent

 
chat_router = APIRouter(tags=["Chat"])

app = FastAPI()

config = {
    "configurable": {
        "thread_id": "1"  
    }
}

@chat_router.post("/chat")
async def chat(query:str):


    agent = await chat_agent()

    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": query}
        ]
    }, config)


    return JSONResponse(content={"message": str(response["messages"][-1].content)})

