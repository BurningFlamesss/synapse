from client.llm_client import LLMClient
import asyncio


async def main():
    client = LLMClient()
    messages = [{
        "role": "user",
        "content": "Hey! Whats up?"
    }]
    await client.chat_completion(messages, False)
    print("Successful")
    
asyncio.run(main())