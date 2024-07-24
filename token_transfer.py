import asyncio

import util

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT
from solana.rpc import commitment



from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.token.associated import get_associated_token_address
from solders.account import Account


from solders.transaction import VersionedTransaction
from solders.system_program import CreateAccountParams, create_account as create_account_instr, ID as SYSTEM_PROGRAM_ID
from solders.message import MessageV0
from solders.signature import Signature



async def create_associated_token_account_if_required(client: AsyncClient, account_addres: Pubkey, token: AsyncToken) -> Pubkey:
    associated_address = get_associated_token_address(account_addres, token.pubkey)
    associated_account = await client.get_account_info(associated_address, commitment.Finalized)
    if associated_account.value is None:
        transaction = await token.create_associated_token_account(account_addres)
        print(f'associated_account: {transaction}')

    return associated_address

async def create_account(client: AsyncClient, account_addres: Pubkey, fee_payer: Keypair) -> Signature:

    instruction = create_account_instr(
        CreateAccountParams(
            from_pubkey=fee_payer.pubkey(),
            to_pubkey=account_addres,
            lamports=100000000,
            space=0,
            owner=SYSTEM_PROGRAM_ID
        )
    )

    blockhash = await client.get_latest_blockhash()

    msg = MessageV0.try_compile(
        payer = fee_payer.pubkey(),
        instructions = [instruction],
        address_lookup_table_accounts = [],
        recent_blockhash = blockhash.value.blockhash
    )

    tx = VersionedTransaction(msg, [fee_payer, fee_payer])
    tx_resp = await client.send_transaction(tx)

    return tx_resp.value

async def create_account_if_required(client: AsyncClient, account_addres: Pubkey, fee_payer: Keypair) -> Account:
    account = (await client.get_account_info(account_addres, commitment.Finalized))
    if account.value is None:
        # transaction = await create_account(client, account_addres, fee_payer)
        await util.airdrop_if_required(client, account_addres)
        #print(f'account: {transaction}')
        account = await client.get_account_info(account_addres, commitment.Finalized)

    return account.value



async def main():

    owner_kp = util.keypair_from_env()


    async with AsyncClient(ENDPOINT.https.devnet) as client:
        await client.is_connected()

        token_pubkey = util.pubkey_from_env('TOKEN_PUBKEY')

        token = AsyncToken(client, token_pubkey, TOKEN_PROGRAM_ID, owner_kp)
        print(f'mint address: {token.pubkey}')

        #new_account = Keypair()
        #print(f'new account: {new_account}')
        #print(f'new account pubkey: {new_account.pubkey()}')


        to_kp = util.keypair_from_env('SECRET_2')

        to_address = to_kp.pubkey()
        account = await create_account_if_required(client, to_address, owner_kp)
        print(f'account: {account}')

        to_address_ata = await create_associated_token_account_if_required(client, to_address, token)
        print(f'associated token account: {to_address_ata}')


        transaction = await token.mint_to(to_address_ata, owner_kp, 1000000) # mint 1000 tokens to the associated token account
        #print(transaction)


asyncio.run(main())