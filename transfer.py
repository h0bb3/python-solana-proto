import asyncio

import util

from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT

from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from solders.message import MessageV0

async def main():

    from_kp = util.keypair_from_env()

    async with AsyncClient(ENDPOINT.https.devnet) as client:
        await client.is_connected()
        from_address = from_kp.pubkey()
        await util.airdrop_if_required(client, from_address)

        to_address = util.keypair_from_env('SECRET_2').pubkey()

        balance = await client.get_balance(to_address, util.DEFAULT_COMMITMENT)
        print(f'💰 The balance of account {to_address} is {balance.value} lamports')
        
        lapmorts_to_send = 1000

        instruction = transfer(TransferParams(from_pubkey=from_address, to_pubkey=to_address, lamports=lapmorts_to_send))
        blockhash = await client.get_latest_blockhash()

        msg = MessageV0.try_compile(
            payer = from_address,
            instructions = [instruction],
            address_lookup_table_accounts = [],
            recent_blockhash = blockhash.value.blockhash
        )

        tx = VersionedTransaction(msg, [from_kp])

        tx_resp = await client.send_transaction(tx)

        print(f'💸 Finished! Sent ${lapmorts_to_send} to the address ${to_address}. ')
        print(f'Transaction signature: ${tx_resp}')

        balance = await client.get_balance(to_address, util.DEFAULT_COMMITMENT)
        print(f'💰 The balance of account {to_address} is {balance.value} lamports')
        

        

asyncio.run(main())