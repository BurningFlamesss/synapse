from typing import Any

import click

from client.llm_client import LLMClient
import asyncio

class CLI:
    def __init__(self):
        pass
    def run_single(self):
        pass

async def run(messages: dict[str, Any]):
    client = LLMClient()
    async for event in client.chat_completion(messages, True):
        print(event)

@click.command()
@click.argument("prompt", required=False)
def main(
    prompt: str | None
):
    messages = [{
        "role": "user",
        "content": prompt
    }]
    asyncio.run(run(messages))
        
    print("Successful")
    
main()