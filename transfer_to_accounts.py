import asyncio

import util
import token_util
import accounts

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT
from solana.rpc import commitment



from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.token.associated import get_associated_token_address
from solders.account import Account
from solders.token.state import TokenAccount



from solders.transaction import VersionedTransaction
from solders.system_program import CreateAccountParams, create_account as create_account_instr, ID as SYSTEM_PROGRAM_ID
from solders.message import MessageV0
from solders.signature import Signature




async def create_associated_token_account_if_required(client: AsyncClient, account_addres: Pubkey, token: AsyncToken) -> tuple[Pubkey, Account]:
    associated_address = get_associated_token_address(account_addres, token.pubkey)
    associated_account = await client.get_account_info(associated_address, commitment.Finalized)
    if associated_account.value is None:
        transaction = await token.create_associated_token_account(account_addres)
        associated_account = await client.get_account_info(associated_address, commitment.Finalized)

    return associated_address, TokenAccount.from_bytes(associated_account.value.data[0:165])

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

    

    async with AsyncClient(util.devnet_rpc()) as client:
        #await client.is_connected()

        token_pubkey = util.pubkey_from_env('SRC_DEV_TOKEN_PUB')

        token = AsyncToken(client, token_pubkey, TOKEN_PROGRAM_ID, owner_kp)
        mint_account = await client.get_account_info(token_pubkey)
        mint_account = mint_account.value
        print(f'mint address: {token_pubkey}')


        for address, desired_balance in accounts.srcful_devnet_to:
            account_pubkey = Pubkey.from_string(address)
            # account = await create_account_if_required(client, account_pubkey, owner_kp)
            # print(f'account: {account}')

            #account = await token_util.get_associated_token_account(client, account_pubkey, token_pubkey, mint_account)

            associated_address, ata = await create_associated_token_account_if_required(client, account_pubkey, token)
            current_balance = ata.amount / 1_000_000
            difference = desired_balance - current_balance
            print(f'current amount of tokens in associated account: {current_balance}')
            print(f'desired amount of tokens in associated account: {desired_balance}')
            print(f'difference: {difference}')
            if difference > 0:
                transaction = await token.mint_to(associated_address, owner_kp, int(1_000_000 * difference))
                print(transaction)
            else:
                print(f'account {account_pubkey} already has the desired amount of tokens')

            # sleep to prevent rate limiting
            await asyncio.sleep(1)
            
        #print(transaction)


asyncio.run(main())


