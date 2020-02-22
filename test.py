import asyncio

import aiohttp
from rhasspyclient import RhasspyClient

def prob(msg):
    print(msg)

async def main():
    async with aiohttp.ClientSession() as session:
        client = RhasspyClient('localhost', '8000', session)
        result = await client.text_to_intent("what time is it")
        print(result)
        await client.listen_for_intent(prob)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
