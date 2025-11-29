import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from app.core.prompt import SYSTEM_PROMPT

load_dotenv()


async def chat_agent():
    llm = ChatGroq(
        model="meta-llama/llama-guard-4-12b",
        temperature=0,
    )

    client = MultiServerMCPClient()
    tools = await client.get_tools()

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )
    return agent


async def main():
    agent = await chat_agent()

    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "tell me how did the agent perform in the conversation?"}
        ]
    })

    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
