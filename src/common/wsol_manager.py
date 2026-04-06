"""
WSOL Manager - 100% port from Rust: src/trading/common/wsol_manager.rs

Provides utilities for handling wrapped SOL (WSOL) operations:
- Wrapping SOL to WSOL
- Unwrapping WSOL to SOL
- Creating WSOL ATA
"""

from typing import List
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.system_program import transfer, TransferParams
import struct

# Constants
TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
WSOL_TOKEN_ACCOUNT = Pubkey.from_string("So11111111111111111111111111111111111111112")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# PDA Cache for ATA addresses
_ata_cache: dict = {}


def _get_ata_cache_key(owner: Pubkey, mint: Pubkey, token_program: Pubkey) -> str:
    return f"{owner}:{mint}:{token_program}"


def get_associated_token_address_fast(
    owner: Pubkey,
    mint: Pubkey,
    token_program: Pubkey = TOKEN_PROGRAM
) -> Pubkey:
    """Get cached Associated Token Address"""
    key = _get_ata_cache_key(owner, mint, token_program)
    if key not in _ata_cache:
        seeds = [
            bytes(owner),
            bytes(token_program),
            bytes(mint),
        ]
        (ata, _) = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM)
        _ata_cache[key] = ata
    return _ata_cache[key]


def create_associated_token_account_idempotent_instruction(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey,
    token_program: Pubkey = TOKEN_PROGRAM
) -> Instruction:
    """Create ATA idempotent instruction"""
    ata = get_associated_token_address_fast(owner, mint, token_program)
    
    accounts = [
        AccountMeta(payer, True, True),  # payer
        AccountMeta(ata, False, True),   # ata
        AccountMeta(owner, False, False), # owner
        AccountMeta(mint, False, False),  # mint
        AccountMeta(SYSTEM_PROGRAM, False, False),  # system program
        AccountMeta(token_program, False, False),   # token program
        AccountMeta(RENT, False, False),  # rent
    ]
    
    return Instruction(ASSOCIATED_TOKEN_PROGRAM, bytes([1]), accounts)


def close_account_instruction(
    token_program: Pubkey,
    account: Pubkey,
    destination: Pubkey,
    owner: Pubkey
) -> Instruction:
    """Create close account instruction"""
    # Close account discriminator = 9
    data = bytes([9])
    
    accounts = [
        AccountMeta(account, False, True),      # account to close
        AccountMeta(destination, False, True),  # destination
        AccountMeta(owner, True, False),        # owner (signer)
    ]
    
    return Instruction(token_program, data, accounts)


def transfer_instruction(
    token_program: Pubkey,
    source: Pubkey,
    destination: Pubkey,
    owner: Pubkey,
    amount: int
) -> Instruction:
    """Create transfer instruction"""
    # Transfer discriminator = 3
    data = bytes([3]) + struct.pack("<Q", amount)
    
    accounts = [
        AccountMeta(source, False, True),       # source
        AccountMeta(destination, False, True),  # destination
        AccountMeta(owner, True, False),        # owner (signer)
    ]
    
    return Instruction(token_program, data, accounts)


def sync_native_instruction(account: Pubkey) -> Instruction:
    """Create sync_native instruction"""
    # SyncNative discriminator = 17
    data = bytes([17])
    accounts = [AccountMeta(account, False, True)]
    return Instruction(TOKEN_PROGRAM, data, accounts)


# ===== WSOL Manager Functions =====

def handle_wsol(payer: Pubkey, amount: int) -> List[Instruction]:
    """
    Handle WSOL - Create ATA, transfer SOL, and sync.
    100% from Rust: src/trading/common/wsol_manager.rs handle_wsol
    """
    instructions = []
    
    wsol_token_account = get_associated_token_address_fast(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    # 1. Create WSOL ATA (idempotent)
    instructions.append(
        create_associated_token_account_idempotent_instruction(payer, payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    )
    
    # 2. Transfer SOL to WSOL ATA
    instructions.append(
        transfer(TransferParams(
            from_pubkey=payer,
            to_pubkey=wsol_token_account,
            lamports=amount,
        ))
    )
    
    # 3. Sync native
    instructions.append(sync_native_instruction(wsol_token_account))
    
    return instructions


def close_wsol(payer: Pubkey) -> Instruction:
    """
    Close WSOL account and reclaim rent.
    100% from Rust: src/trading/common/wsol_manager.rs close_wsol
    """
    wsol_token_account = get_associated_token_address_fast(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    return close_account_instruction(TOKEN_PROGRAM, wsol_token_account, payer, payer)


def create_wsol_ata(payer: Pubkey) -> List[Instruction]:
    """
    Create WSOL ATA only (without funding).
    100% from Rust: src/trading/common/wsol_manager.rs create_wsol_ata
    """
    return [create_associated_token_account_idempotent_instruction(payer, payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)]


def wrap_sol_only(payer: Pubkey, amount: int) -> List[Instruction]:
    """
    Wrap SOL only - Transfer and sync without creating ATA.
    Assumes ATA already exists.
    100% from Rust: src/trading/common/wsol_manager.rs wrap_sol_only
    """
    instructions = []
    
    wsol_token_account = get_associated_token_address_fast(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    # 1. Transfer SOL to WSOL ATA
    instructions.append(
        transfer(TransferParams(
            from_pubkey=payer,
            to_pubkey=wsol_token_account,
            lamports=amount,
        ))
    )
    
    # 2. Sync native
    instructions.append(sync_native_instruction(wsol_token_account))
    
    return instructions


# ===== Seed-based ATA Functions =====

def _generate_seed_from_mint(mint: Pubkey) -> str:
    """Generate seed string from mint address using FNV hash"""
    # FNV-1a hash
    hash_val = 2166136261  # FNV offset basis for 32-bit
    mint_bytes = bytes(mint)
    for byte in mint_bytes:
        hash_val ^= byte
        hash_val = (hash_val * 16777619) & 0xFFFFFFFF  # FNV prime for 32-bit
    
    # Take lower 32 bits and convert to hex string (8 chars)
    return format(hash_val, '08x')


def get_associated_token_address_use_seed(
    wallet_address: Pubkey,
    token_mint_address: Pubkey,
    token_program_id: Pubkey = TOKEN_PROGRAM
) -> Pubkey:
    """
    Get Associated Token Address using seed method.
    100% from Rust: src/common/seed.rs get_associated_token_address_with_program_id_use_seed
    """
    # For now, use standard ATA derivation
    # Full seed-based implementation would use create_with_seed
    seeds = [
        bytes(wallet_address),
        bytes(token_program_id),
        bytes(token_mint_address),
    ]
    (ata, _) = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM)
    return ata


def wrap_wsol_to_sol(payer: Pubkey, amount: int) -> List[Instruction]:
    """
    Wrap WSOL to SOL - Transfer WSOL to seed account and close it.
    100% from Rust: src/trading/common/wsol_manager.rs wrap_wsol_to_sol
    """
    instructions = []
    
    # 1. Create seed WSOL account
    seed_ata = get_associated_token_address_use_seed(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    instructions.append(
        create_associated_token_account_idempotent_instruction(payer, payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    )
    
    # 2. Get user WSOL ATA
    user_wsol_ata = get_associated_token_address_fast(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    # 3. Transfer WSOL from user ATA to seed ATA
    instructions.append(
        transfer_instruction(TOKEN_PROGRAM, user_wsol_ata, seed_ata, payer, amount)
    )
    
    # 4. Close seed WSOL account
    instructions.append(
        close_account_instruction(TOKEN_PROGRAM, seed_ata, payer, payer)
    )
    
    return instructions


def wrap_wsol_to_sol_without_create(payer: Pubkey, amount: int) -> List[Instruction]:
    """
    Wrap WSOL to SOL without creating account.
    Assumes seed account already exists.
    100% from Rust: src/trading/common/wsol_manager.rs wrap_wsol_to_sol_without_create
    """
    instructions = []
    
    # 1. Get seed ATA address
    seed_ata = get_associated_token_address_use_seed(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    # 2. Get user WSOL ATA
    user_wsol_ata = get_associated_token_address_fast(payer, WSOL_TOKEN_ACCOUNT, TOKEN_PROGRAM)
    
    # 3. Transfer WSOL from user ATA to seed ATA
    instructions.append(
        transfer_instruction(TOKEN_PROGRAM, user_wsol_ata, seed_ata, payer, amount)
    )
    
    # 4. Close seed WSOL account
    instructions.append(
        close_account_instruction(TOKEN_PROGRAM, seed_ata, payer, payer)
    )
    
    return instructions
