from solders.pubkey import Pubkey
import asyncio

from solana.rpc.async_api import AsyncClient
from solders.token.state import TokenAccount
from solders.account import Account

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID

from solders.keypair import Keypair
from solders.pubkey import Pubkey

import util



def get_associated_token_address(account: Pubkey, token: Pubkey, owner:Pubkey) -> Pubkey:
    return Pubkey.find_program_address([bytes(account), bytes(owner), bytes(token)], ASSOCIATED_TOKEN_PROGRAM_ID)


async def get_associated_token_account(client: AsyncClient, account: Pubkey, token: Pubkey, token_account:Account = None) -> TokenAccount:

    if token_account is None:
        mint_account = (await client.get_account_info(token, util.DEFAULT_COMMITMENT)).value
    else:
        mint_account = token_account
    
    assert mint_account.owner in {TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID}   
    
    associated_address, _ = get_associated_token_address(account, token, mint_account.owner)

    associated_account = await client.get_account_info(associated_address, util.DEFAULT_COMMITMENT)

    if associated_account.value is not None:
        return TokenAccount.from_bytes(associated_account.value.data[0:165])  # token 22 accounts are the same as the normal accounts up to 165 bytes
    raise ValueError(f'Associated token account not found for account: {account} and token: {token}')
