import asyncio
from solana.rpc.websocket_api import connect

async def main():
    async with connect("wss://api.devnet.solana.com") as websocket:
        await websocket.logs_subscribe()
        first_resp = await websocket.recv()
        subscription_id = first_resp[0].result
        next_resp = await websocket.recv()
        print(next_resp)
        await websocket.logs_unsubscribe(subscription_id)

asyncio.run(main())