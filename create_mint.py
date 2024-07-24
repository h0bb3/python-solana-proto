import asyncio

import util

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT

from solders.pubkey import Pubkey


async def main():

    owner_kp = util.keypair_from_env()

    async with AsyncClient(ENDPOINT.https.devnet) as client:
        await client.is_connected()

        token = await AsyncToken.create_mint(client, owner_kp, owner_kp.pubkey(), 6, TOKEN_PROGRAM_ID, freeze_authority=owner_kp.pubkey())
        print(f'mint address: {token.pubkey()}')
        # J6NkhbGhXVzvrPNEpErBUmZXjePhNkYUqbyLtZ7wps6q

        to_address = util.keypair_from_env('SECRET_2').pubkey()

        token_account = await token.create_account(owner_kp.pubkey())
        print(token_account)

        # create an associated token account for the to adress account to store tokens
        #ata = await token.create_associated_token_account(to_address)
        #print(ata)

        # CCb9q5wPB3RbNNWZhYJwPFT8VzbcviD6YXwiZECmK2NF

        #transaction = await token.mint_to(ata, owner_kp.pubkey(), 1000) # mint 1000 tokens to the associated token account
        #print(transaction)


asyncio.run(main())