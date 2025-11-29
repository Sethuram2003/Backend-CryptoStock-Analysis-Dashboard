import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import sys

from app.core.prompt import SYSTEM_PROMPT

load_dotenv()

checkpointer = InMemorySaver()

config = {
    "configurable": {
        "thread_id": "1"  
    }
}

def find_python_path():
    """Find Python binary path with packages"""
    return sys.executable 

python_executable = find_python_path()
current_dir = os.path.dirname(os.path.abspath(__file__))


async def chat_agent():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    McpConfig={
        "crypto_data": {
            "command": python_executable, 
            "args": [
                os.path.join(current_dir, "CryptoMcpServer", "main.py") 
            ],
            "transport": "stdio",
            "env": {
                **os.environ,
                "PYTHONPATH": os.pathsep.join([
                    current_dir,
                    os.path.join(current_dir, "CryptoMcpServer"),
                    *sys.path
                ])
            }
        },
        "stock_data": {
            "command": python_executable, 
            "args": [
                os.path.join(current_dir, "StockMcpServer", "main.py") 
            ],
            "transport": "stdio",
            "env": {
                **os.environ,
                "PYTHONPATH": os.pathsep.join([
                    current_dir,
                    os.path.join(current_dir, "StockMcpServer"),
                    *sys.path
                ])
            }
        },
        "firecrawl-mcp": {
        "transport": "streamable_http",
        "url": f"https://mcp.firecrawl.dev/{os.getenv("FIRECRAWL_API_KEY")}/v2/mcp",  
        }

    }

    client = MultiServerMCPClient(McpConfig)
    tools = await client.get_tools()

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

    return agent


async def main():
    agent = await chat_agent()

    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "tell me how did the agent perform in the conversation?"}
        ]
    }, config)

    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
