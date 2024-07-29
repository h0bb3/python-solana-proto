import asyncio
from solana.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.utils.cluster import ENDPOINT

from solders.instruction import Instruction, AccountMeta



from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from solders.system_program import ID as SYS_PROGRAM_ID
import struct
import util



from borsh_construct import CStruct, String, U8, U16, U64, Vec, Option, Bool, Enum
from construct import Bytes

# structure of the instruction
instruction_structure = CStruct(
    "instructionDiscriminator" / U8,
    "createMetadataAccountArgsV3" / CStruct( # https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/instruction/metadata.rs#L32
        "data" / CStruct(                       # https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/state/data.rs#L22
            "name" / String,
            "symbol" / String,
            "uri" / String,
            "sellerFeeBasisPoints" / U16,
            "creators" / Option(Vec(CStruct(
                "address" / Bytes(32),
                "verified" / Bool,
                "share" / U8
            ))),
            "collection" / Option(CStruct(
                "verified" / Bool,
                "key" / String
            )),
            "uses" / Option(CStruct(
                "useMethod" / Enum(
                    "Burn",
                    "Multiple",
                    "Single",
                    enum_name="UseMethod"
                ),
                "remaining" / U64,
                "total" / U64
            ))
        ),
        "isMutable" / Bool,
        "collectionDetails" / Option(String) # fixme: string is not correct, insert correct type
    )
)

# data for the instruction
instruction_data = {
    "instructionDiscriminator": 33, # createMetadataAccountV3 count to that enum in https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/instruction/mod.rs#L49
    "createMetadataAccountArgsV3": {
        "data": {
            "name": "h0bb3Z Tezt Token",
            "symbol": "h0b",
            "uri": "https://google.com",
            "sellerFeeBasisPoints": 0,
            "creators": None,
            "collection": None,
            "uses": None
        },
        "isMutable": 1,
        "collectionDetails": None
    }
}

# Constants
METAPLEX_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")

def get_metadata_pda(mint_pubkey: Pubkey):
    """Calculates the PDA for the metadata account."""
    return Pubkey.find_program_address(
        [b"metadata", bytes(METAPLEX_PROGRAM_ID), bytes(mint_pubkey)],
        METAPLEX_PROGRAM_ID
    )

def create_metadata_instruction(metadata_account: Pubkey, mint_account: Pubkey, mint_authority: Pubkey, payer:Pubkey, name:str, symbol:str, uri:str, update_authority:Pubkey, is_mutable=True):
    pass
    

    

async def create_metadata(client: AsyncClient, mint_pubkey: Pubkey, payer: Keypair, name: str, symbol: str, uri: str):
    metadata_pubkey, _ = get_metadata_pda(mint_pubkey)
    update_authority = payer.pubkey()

    instruction = create_metadata_instruction(
        metadata_pubkey,
        mint_pubkey,
        payer.pubkey(),
        payer.pubkey(),
        name,
        symbol,
        uri,
        update_authority
    )

    



    # account list for instruction
    accounts = [
        AccountMeta(pubkey=metadata_pubkey, is_signer=False, is_writable=True), # metadata
        AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False), # mint
        AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=False), # mint authority
        AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True), # payer
        AccountMeta(pubkey=payer.pubkey(), is_signer=False, is_writable=False), # update authority
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False), # system program
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False) # rent
    ]

    instruction = Instruction(METAPLEX_PROGRAM_ID, instruction_structure.build(instruction_data), accounts)

    transaction = Transaction()
    transaction.add(instruction)
    
    transaction.recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
    transaction.fee_payer = payer.pubkey()

    transaction.sign(payer)
    result = await client.send_transaction(transaction, payer)
    return result.value

async def main():
    payer = util.keypair_from_env()
    async with AsyncClient(ENDPOINT.https.devnet) as client:
        await client.is_connected()

        mint_pubkey = util.pubkey_from_env('TOKEN_PUB')

        name = "h0bb3Z"
        symbol = "h0b"
        uri = "https://example.com/metadata.json"

        result = await create_metadata(client, mint_pubkey, payer, name, symbol, uri)
        print(f"Transaction result: {result}")


asyncio.run(main())
