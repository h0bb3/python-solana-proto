import asyncio

import util
import token_util
import accounts

from solana.rpc.async_api import AsyncClient

from solders.pubkey import Pubkey





async def main():
    async with AsyncClient(util.mainnet_rpc()) as client:
        #await client.is_connected()

        token_pubkey = util.pubkey_from_env('SRC_TOKEN_PUB')
        mint_account = await client.get_account_info(token_pubkey)

        checked_accounts = []            

        for  address, amount in accounts.srcful_mainnet_from:
            print(f"{address} has {amount} tokens")
            holder_pubkey = Pubkey.from_string(address)

            try:
                account = await token_util.get_associated_token_account(client, holder_pubkey, token_pubkey, mint_account.value)
                print(f'💰 The balance of account {holder_pubkey} is {account.amount / 1_000_000_000} tokens')
                checked_accounts.append((address, amount, account.amount / 1_000_000_000))
            except ValueError:
                print(f'💰 The account {holder_pubkey} does not have any tokens')

        for address, amount, balance in checked_accounts:
            print(f"{address}\t{amount}\t{balance}")


asyncio.run(main())