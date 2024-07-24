import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

async def main():

    #url = 'https://api.mainnet-beta.solana.com'
    url = 'https://api.devnet.solana.com'

    async with AsyncClient(url) as client:
        await client.is_connected()
        address = Pubkey.from_string("CenYq6bDRB7p73EjsPEpiYN7uveyPUTdXkDkgUduboaN")
        balance = await client.get_balance(address)

    print(f'💰 The balance of account {address} is {balance.value} lamports')


asyncio.run(main())