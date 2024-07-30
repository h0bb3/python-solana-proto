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
    "updateMetadataAccountArgsV2" / CStruct( # https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/instruction/metadata.rs#L32
        "data" / Option(CStruct(                       # https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/state/data.rs#L22
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
        )),
        "updateAuthority" / Option(Bytes(32)),
        "primarySaleHappened" / Option(Bool),
        "isMutable" / Option(Bool),
    )
)

# data for the instruction
instruction_data = {
    "instructionDiscriminator": 15, # UpdateMetadataAccountV2 count to that enum in https://github.com/metaplex-foundation/mpl-token-metadata/blob/5c7672c7b7cd671c7afbdaeed52819e9a7a3259f/programs/token-metadata/program/src/instruction/mod.rs#L49
    "updateMetadataAccountArgsV2": {
        "data": {
            "name": "The Best Token",
            "symbol": "TBT",
            "uri": "https://google.com",
            "sellerFeeBasisPoints": 0,
            "creators": None,
            "collection": None,
            "uses": None
        },
        "updateAuthority": None,
        "primarySaleHappened": None,
        "isMutable": 1,
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



async def update_metadata(client: AsyncClient, mint_pubkey: Pubkey, payer: Keypair, name: str, symbol: str, uri: str):
    metadata_pubkey, _ = get_metadata_pda(mint_pubkey)


    # account list for instruction
    accounts = [
        AccountMeta(pubkey=metadata_pubkey, is_signer=False, is_writable=True), # metadata
        AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=False), # update authority
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
    async with AsyncClient(util.devnet_rpc()) as client:
        #await client.is_connected()

        mint_pubkey = util.pubkey_from_env('TOKEN_PUB')

        name = "h0bb3Z"
        symbol = "h0b"
        uri = "https://example.com/metadata.json"

        result = await update_metadata(client, mint_pubkey, payer, name, symbol, uri)
        print(f"Transaction result: {result}")


asyncio.run(main())
