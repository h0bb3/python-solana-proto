from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class VerifySizedCollectionItemAccounts(typing.TypedDict):
    metadata: Pubkey
    collection_authority: Pubkey
    payer: Pubkey
    collection_mint: Pubkey
    collection: Pubkey
    collection_master_edition_account: Pubkey
    collection_authority_record: typing.Optional[Pubkey]


def verify_sized_collection_item(
    accounts: VerifySizedCollectionItemAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["collection_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["collection_mint"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["collection"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["collection_master_edition_account"],
            is_signer=False,
            is_writable=False,
        ),
        (
            AccountMeta(
                pubkey=accounts["collection_authority_record"],
                is_signer=False,
                is_writable=False,
            )
            if accounts["collection_authority_record"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"Vo\xdfD\x11c\xb4\x93"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
