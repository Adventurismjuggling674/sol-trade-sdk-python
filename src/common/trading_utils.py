"""
Trading Utilities - Async RPC utilities for trading operations.
100% port from Rust: src/trading/common/utils.rs
"""

from typing import Tuple, Optional
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams

from .wsol_manager import (
    get_associated_token_address_fast,
    get_associated_token_address_use_seed,
    close_account_instruction,
    TOKEN_PROGRAM,
)
from ..rpc.client import AsyncRPCClient, RPCClient


async def get_multi_token_balances(
    rpc: AsyncRPCClient,
    token0_vault: Pubkey,
    token1_vault: Pubkey,
) -> Tuple[int, int]:
    """
    Get the balances of two tokens in the pool.

    100% from Rust: src/trading/common/utils.rs get_multi_token_balances

    Args:
        rpc: Async RPC client
        token0_vault: First token vault address
        token1_vault: Second token vault address

    Returns:
        Tuple of (token0_balance, token1_balance)
    """
    result = await rpc._make_request(
        "getTokenAccountsBalance",
        [str(token0_vault), str(token1_vault)],
    )

    token0_amount = int(result[0]["amount"])
    token1_amount = int(result[1]["amount"])

    return (token0_amount, token1_amount)


async def get_token_balance(
    rpc: AsyncRPCClient,
    payer: Pubkey,
    mint: Pubkey,
) -> int:
    """
    Get token balance for a payer's ATA.

    100% from Rust: src/trading/common/utils.rs get_token_balance
    """
    return await get_token_balance_with_options(rpc, payer, mint, TOKEN_PROGRAM, False)


async def get_token_balance_with_options(
    rpc: AsyncRPCClient,
    payer: Pubkey,
    mint: Pubkey,
    token_program: Pubkey,
    use_seed: bool,
) -> int:
    """
    Get token balance using consistent ATA derivation (optional seed).
    Sell/balance queries should use the same ATA address as buy.

    100% from Rust: src/trading/common/utils.rs get_token_balance_with_options
    """
    if use_seed:
        ata = get_associated_token_address_use_seed(payer, mint, token_program)
    else:
        ata = get_associated_token_address_fast(payer, mint, token_program)

    result = await rpc._make_request(
        "getTokenAccountBalance",
        [str(ata)],
    )

    return int(result["value"]["amount"])


async def get_sol_balance(
    rpc: AsyncRPCClient,
    account: Pubkey,
) -> int:
    """
    Get SOL balance for an account.

    100% from Rust: src/trading/common/utils.rs get_sol_balance
    """
    result = await rpc._make_request(
        "getBalance",
        [str(account)],
    )
    return result["value"]


async def transfer_sol(
    rpc: AsyncRPCClient,
    payer: Keypair,
    receive_wallet: Pubkey,
    amount: int,
) -> str:
    """
    Transfer SOL from payer to receive_wallet.

    100% from Rust: src/trading/common/utils.rs transfer_sol

    Args:
        rpc: Async RPC client
        payer: Keypair of the sender
        receive_wallet: Recipient wallet address
        amount: Amount in lamports

    Returns:
        Transaction signature
    """
    if amount == 0:
        raise ValueError("transfer_sol: Amount cannot be zero")

    balance = await get_sol_balance(rpc, payer.pubkey())
    if balance < amount:
        raise ValueError("Insufficient balance")

    transfer_instruction = transfer(TransferParams(
        from_pubkey=payer.pubkey(),
        to_pubkey=receive_wallet,
        lamports=amount,
    ))

    blockhash = await rpc.get_latest_blockhash()

    transaction = Transaction.new_signed_with_payer(
        [transfer_instruction],
        payer.pubkey(),
        [payer],
        blockhash.blockhash,
    )

    return await rpc.send_transaction(bytes(transaction))


async def close_token_account(
    rpc: AsyncRPCClient,
    payer: Keypair,
    mint: Pubkey,
) -> Optional[str]:
    """
    Close token account.

    100% from Rust: src/trading/common/utils.rs close_token_account

    This function closes the associated token account for a specified token,
    transferring the token balance in the account to the account owner.

    Args:
        rpc: Async RPC client
        payer: Keypair of the account owner
        mint: Token mint address

    Returns:
        Transaction signature or None if account doesn't exist
    """
    # Get associated token account address
    ata = get_associated_token_address_fast(payer.pubkey(), mint, TOKEN_PROGRAM)

    # Check if account exists
    try:
        account_info = await rpc._make_request(
            "getAccountInfo",
            [str(ata), {"encoding": "base64"}],
        )
        if account_info.get("value") is None:
            return None  # Account doesn't exist, return success
    except Exception:
        return None

    # Build close account instruction
    close_account_ix = close_account_instruction(
        TOKEN_PROGRAM,
        ata,
        payer.pubkey(),
        payer.pubkey(),
    )

    # Build transaction
    blockhash = await rpc.get_latest_blockhash()
    transaction = Transaction.new_signed_with_payer(
        [close_account_ix],
        payer.pubkey(),
        [payer],
        blockhash.blockhash,
    )

    # Send transaction
    return await rpc.send_transaction(bytes(transaction))


# ===== Synchronous Versions =====

def get_token_balance_sync(
    rpc: RPCClient,
    payer: Pubkey,
    mint: Pubkey,
    token_program: Pubkey = TOKEN_PROGRAM,
    use_seed: bool = False,
) -> int:
    """Synchronous version of get_token_balance"""
    if use_seed:
        ata = get_associated_token_address_use_seed(payer, mint, token_program)
    else:
        ata = get_associated_token_address_fast(payer, mint, token_program)

    result = rpc._make_request(
        "getTokenAccountBalance",
        [str(ata)],
    )

    return int(result["value"]["amount"])


def get_sol_balance_sync(
    rpc: RPCClient,
    account: Pubkey,
) -> int:
    """Synchronous version of get_sol_balance"""
    result = rpc._make_request(
        "getBalance",
        [str(account)],
    )
    return result["value"]


def get_multi_token_balances_sync(
    rpc: RPCClient,
    token0_vault: Pubkey,
    token1_vault: Pubkey,
) -> Tuple[int, int]:
    """Synchronous version of get_multi_token_balances"""
    # Get each balance separately
    result0 = rpc._make_request(
        "getTokenAccountBalance",
        [str(token0_vault)],
    )
    result1 = rpc._make_request(
        "getTokenAccountBalance",
        [str(token1_vault)],
    )

    token0_amount = int(result0["value"]["amount"])
    token1_amount = int(result1["value"]["amount"])

    return (token0_amount, token1_amount)
