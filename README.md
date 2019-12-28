# Rhasspy Client

Basic client library for talking to a remote [Rhasspy](https://rhasspy.readthedocs.io) server. Uses [aiohttp](https://aiohttp.readthedocs.io/en/stable/).

## Example

```python
import asyncio

import aiohttp
from rhasspyclient import RhasspyClient

async def main():
    async with aiohttp.ClientSession() as session:
        client = RhasspyClient("http://localhost:12101/api", session)
        result = await client.text_to_intent("what time is it")
        print(result)
        
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## Module CLI

You can run the module too:

```bash
$ python3 -m rhasspyclient <COMMAND> [<ARG>, ...]
```

Use `--help` to see available commands.
