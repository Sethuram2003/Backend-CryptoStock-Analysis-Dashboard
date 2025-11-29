import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from app.core.prompt import SYSTEM_PROMPT

load_dotenv()

checkpointer = InMemorySaver()


async def chat_agent():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
    )

    client = MultiServerMCPClient()
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
    })

    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
