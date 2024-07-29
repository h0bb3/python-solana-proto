import os
import asyncio

from solana.rpc.async_api import AsyncClient
from solana.constants import LAMPORTS_PER_SOL

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from solana.rpc import commitment


DEFAULT_COMMITMENT = commitment.Finalized

async def airdrop_if_required(connection: AsyncClient, address: Pubkey):
    balance = await connection.get_balance(address, DEFAULT_COMMITMENT)
    if balance.value <= 0:
        print(f'Airdropping {LAMPORTS_PER_SOL} lamports to {address}')
        resp = await connection.request_airdrop(address, LAMPORTS_PER_SOL, DEFAULT_COMMITMENT)
        print(f'Airdrop transaction signature: {resp}')


def mainnet_rpc():
    return os.getenv('MAINNET_RPC', 'https://api.mainnet-beta.solana.com')

def devnet_rpc():
    return os.getenv('DEVNET_RPC', 'https://api.devnet.solana.com')

def keypair_from_env(key='SECRET'):
    secret = os.getenv(key)
    return Keypair.from_base58_string(secret)

def pubkey_from_env(key):
    pubkey = os.getenv(key)
    return Pubkey.from_string(pubkey) if pubkey else None
