# checks if a given account has a token and returns the balance of the token.
import asyncio

import util

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID


from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT
from solana.rpc import commitment



from solders.pubkey import Pubkey
from solders.keypair import Keypair
#from solders.token.associated import get_associated_token_address
from solders.token.state import TokenAccount

from struct import unpack
from base58 import b58decode

import struct


# Constants
METAPLEX_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")

def get_metaplex_metadata_pda(mint_pubkey: Pubkey):
    """Calculates the PDA for the metadata account."""
    return Pubkey.find_program_address(
        [b"metadata", bytes(METAPLEX_PROGRAM_ID), bytes(mint_pubkey)],
        METAPLEX_PROGRAM_ID
    )

def decode_metaplex_metadata(data):
    # Offset definitions    https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/state/metadata.rs#L19
    NAME_MAX_LENGTH = 32
    SYMBOL_MAX_LENGTH = 10
    
    # Skip initial bytes up to the name field (schema: 1 byte, 32 bytes MINT, 32 bytes update auth, 4 bytes name length)
    NAME_START = 1 + 32 + 32 + 4
    name_bytes = data[NAME_START:NAME_START + NAME_MAX_LENGTH]
    name = name_bytes.split(b'\0', 1)[0].decode('utf-8')
    print(name)

    # Symbol field starts right after the fixed 100 bytes for the name
    SYMBOL_START = NAME_START + NAME_MAX_LENGTH + 4
    symbol_bytes = data[SYMBOL_START:SYMBOL_START + SYMBOL_MAX_LENGTH]
    symbol = symbol_bytes.split(b'\0', 1)[0].decode('utf-8')

    return name, symbol


def parse_tlv_header(byte_array):
    if len(byte_array) < 4:
        raise ValueError("Byte array is too short to contain a valid TLV header")

    # Unpack the type (2 bytes) and length (2 bytes) as unsigned short (big-endian)
    type_field, length_field = struct.unpack_from('<HH', byte_array, 0)
    
    return type_field, length_field

def read_next_string(byte_array, start):
    # Read the length of the string (4 bytes) as unsigned int (little-endian)
    length = struct.unpack_from('<I', byte_array, start)[0]
    start += 4

    # Read the string itself
    string = byte_array[start:start + length].decode('utf-8')
    start += length

    return string, start

async def get_token_name_symbol(client: AsyncClient, token: Pubkey):
    metadata_address, _ = get_metaplex_metadata_pda(token)
    metadata_account = await client.get_account_info(metadata_address, commitment.Finalized)
    if metadata_account.value is not None:
        return decode_metaplex_metadata(metadata_account.value.data)

    # the account may have meta data as an extension
    mint_account = await client.get_account_info(token, commitment.Finalized)
    assert mint_account.value.owner in {TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID}

    headerIx = 166
    while headerIx < len(mint_account.value.data):
        type, length = parse_tlv_header(mint_account.value.data[headerIx:])
        if type == 19:
            # https://github.com/solana-labs/solana-program-library/blob/c4d51f20b8722d23b03e94c7075702fca52460dd/token-metadata/interface/src/state.rs#L25
            # print(Pubkey.from_bytes(mint_account.value.data[headerIx + 4:headerIx + 4+32])) # update authority address
            # print(Pubkey.from_bytes(mint_account.value.data[headerIx + 4+32:headerIx + 4+32+32])) # mint address

            # basic strings start here each prepended with an u32 length
            string_start = headerIx + 4 + 64
            name, string_start = read_next_string(mint_account.value.data, string_start)
            symbol, string_start = read_next_string(mint_account.value.data, string_start)
            uri, string_start = read_next_string(mint_account.value.data, string_start)

            return name, symbol
            
        headerIx += length + 4

    return "unknown token", 'n/a'


def get_associated_token_address(account: Pubkey, token: Pubkey, owner:Pubkey) -> Pubkey:
    return Pubkey.find_program_address([bytes(account), bytes(owner), bytes(token)], ASSOCIATED_TOKEN_PROGRAM_ID)


async def get_associated_token_account(client: AsyncClient, account: Pubkey, token: Pubkey) -> TokenAccount:

    mint_account = await client.get_account_info(token, commitment.Finalized)
    assert mint_account.value.owner in {TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID}   
    
    associated_address, _ = get_associated_token_address(account, token, mint_account.value.owner)

    associated_account = await client.get_account_info(associated_address, commitment.Finalized)
    print("associated account address", associated_address)

    if associated_account.value is not None:
        return TokenAccount.from_bytes(associated_account.value.data[0:165])  # token 22 accounts are the same as the normal accounts up to 165 bytes
    raise ValueError(f'Associated token account not found for account: {account} and token: {token}')

async def main():
    async with AsyncClient(util.devnet_rpc()) as client:
        #await client.is_connected()

        token_pubkey = util.pubkey_from_env('TOKEN_PUB')
        holder_pubkey = util.keypair_from_env('SECRET_2').pubkey()
        #holder_pubkey = util.pubkey_from_env('h0bb3_PUB')

        name, symbol = await get_token_name_symbol(client, token_pubkey)

        try:
            account = await get_associated_token_account(client, holder_pubkey, token_pubkey)
            print(f'💰 The {name} balance of account {holder_pubkey} is {account.amount} {symbol}')
        except ValueError:

            print(f'💰 The account {holder_pubkey} does not have any {name} tokens')

asyncio.run(main())