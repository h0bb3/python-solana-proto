from solders.keypair import Keypair
from solders.pubkey import Pubkey
from base58 import b58encode
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.constants import LAMPORTS_PER_SOL
import util

# second account
# 9kZPzNag4fdXyKiYUTCVTZrXUZBfJCDxLhptNjmbcmD6
# 3qh3NEW95zPvkW8XsaUdFcoRuUYaDWWnURqJnEsRPU69caDTZXQuiPc5ArdRxMGHvRGxc1musCYjhmfxb7Cq42Te


#keypair = Keypair()
keypair = util.keypair_from_env()
print(keypair)
print(keypair.pubkey())
print(b58encode(keypair.secret()))
print(b58encode(keypair.secret()).decode())
print(b58encode(bytes(keypair.to_bytes_array())).decode())



async def get_balance(connection: AsyncClient, address: Pubkey) -> int:
    balance = await connection.get_balance(address, util.DEFAULT_COMMITMENT)
    return balance.value


async def main():
    async with AsyncClient("https://api.devnet.solana.com") as client:
        await client.is_connected()
        address = keypair.pubkey()
        await util.airdrop_if_required(client, address)


        balance = await get_balance(client, address)
        print(f'💰 The balance of account {address} is {balance} lamports')

        

asyncio.run(main())

