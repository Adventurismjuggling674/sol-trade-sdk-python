"""
Hot Path Trading Example

Demonstrates how to use the Hot Path architecture for minimal latency trading.
Key principle: NO RPC calls during trade execution - all data is prefetched.
"""

import asyncio
from typing import List, Optional
import base58

# Import hot path modules
from sol_trade_sdk.hotpath import (
    HotPathExecutor,
    HotPathConfig,
    TradingContext,
    ExecuteOptions,
    StaleBlockhashError,
    create_hot_path_executor,
)

# Import SWQoS clients
from sol_trade_sdk.swqos import (
    JitoClient,
    BloxrouteClient,
    HeliusClient,
    SwqosType,
)

# Import instruction builders
from sol_trade_sdk.instruction import (
    PumpFunInstructionBuilder,
    RaydiumInstructionBuilder,
    MeteoraInstructionBuilder,
)


class HotPathTrader:
    """
    Complete hot path trading implementation.
    
    Architecture:
    1. Prefetch: Load all required data before trading
    2. Build: Create transaction with cached blockhash
    3. Execute: Submit to SWQoS - NO RPC CALLS
    
    This ensures minimal latency during the critical trading path.
    """
    
    def __init__(
        self,
        rpc_url: str,
        jito_api_key: Optional[str] = None,
        bloxroute_api_key: Optional[str] = None,
        helius_api_key: Optional[str] = None,
    ):
        # Configure hot path with aggressive settings
        config = HotPathConfig(
            blockhash_refresh_interval=1.5,  # Refresh blockhash every 1.5s
            cache_ttl=4.0,                    # Data valid for 4s
            enable_prefetch=True,
        )
        
        # Create executor
        self.executor = create_hot_path_executor(rpc_url, config=config)
        
        # Add SWQoS clients for transaction submission
        if jito_api_key:
            self.executor.add_swqos_client(
                JitoClient(jito_api_key, rpc_url)
            )
        if bloxroute_api_key:
            self.executor.add_swqos_client(
                BloxrouteClient(bloxroute_api_key, rpc_url)
            )
        if helius_api_key:
            self.executor.add_swqos_client(
                HeliusClient(helius_api_key, rpc_url)
            )
        
        # Instruction builders
        self.pumpfun_builder = PumpFunInstructionBuilder()
        self.raydium_builder = RaydiumInstructionBuilder()
        self.meteora_builder = MeteoraInstructionBuilder()
    
    async def start(self) -> None:
        """Start background prefetching"""
        await self.executor.start()
        
        # Wait for initial data to be ready
        ready = await self.executor.wait_for_ready(timeout=10.0)
        if not ready:
            raise RuntimeError("Executor failed to become ready")
    
    async def stop(self) -> None:
        """Stop background prefetching"""
        await self.executor.stop()
    
    async def prefetch_for_trade(
        self,
        payer: str,
        token_accounts: List[str],
        pool_addresses: List[str],
    ) -> TradingContext:
        """
        Prefetch all data needed for a trade.
        
        This is called BEFORE the hot path execution.
        RPC calls happen here, not during trading.
        """
        # Create trading context with current blockhash
        context = self.executor.create_trading_context(payer)
        
        # Prefetch token accounts
        if token_accounts:
            await self.executor.prefetch_accounts(token_accounts)
            for addr in token_accounts:
                context.add_account(addr, self.executor.get_state())
        
        # Prefetch pool accounts if provided
        if pool_addresses:
            await self.executor.prefetch_accounts(pool_addresses)
        
        return context
    
    async def execute_pumpfun_buy(
        self,
        payer: str,
        mint: str,
        bonding_curve: str,
        amount: int,
        max_sol_cost: int,
        token_account: str,
        slippage_bps: int = 500,
    ) -> dict:
        """
        Execute a PumpFun buy with hot path optimization.
        
        Steps:
        1. Prefetch all required data (RPC calls here)
        2. Build transaction with cached blockhash (no RPC)
        3. Submit to SWQoS (no RPC)
        """
        # STEP 1: Prefetch data - RPC CALLS HAPPEN HERE
        context = await self.prefetch_for_trade(
            payer=payer,
            token_accounts=[token_account, bonding_curve],
            pool_addresses=[],
        )
        
        # Validate context is fresh
        if not context.is_valid():
            raise StaleBlockhashError("Trading context expired")
        
        # STEP 2: Build transaction - NO RPC CALLS
        blockhash, last_valid_height, _ = self.executor.get_blockhash()
        if not blockhash:
            raise StaleBlockhashError("No blockhash available")
        
        # Build instruction using prefetched data
        instruction = self.pumpfun_builder.build_buy_instruction(
            payer=payer,
            mint=mint,
            bonding_curve=bonding_curve,
            amount=amount,
            max_sol_cost=max_sol_cost,
        )
        
        # Build transaction (simplified - actual implementation would use solders)
        tx_bytes = self._build_transaction_bytes(
            payer=payer,
            instructions=[instruction],
            blockhash=blockhash,
        )
        
        # STEP 3: Execute - NO RPC CALLS
        opts = ExecuteOptions(
            parallel_submit=True,      # Submit to all SWQoS in parallel
            timeout=10.0,
            skip_blockhash_validation=False,
        )
        
        result = await self.executor.execute("buy", tx_bytes, opts)
        
        return {
            "signature": result.signature,
            "success": result.success,
            "error": result.error,
            "latency_ms": result.latency_ms,
            "swqos_type": result.swqos_type,
        }
    
    async def execute_raydium_swap(
        self,
        payer: str,
        amm_id: str,
        token_account_a: str,
        token_account_b: str,
        amount_in: int,
        min_amount_out: int,
    ) -> dict:
        """
        Execute a Raydium swap with hot path optimization.
        """
        # Prefetch accounts
        context = await self.prefetch_for_trade(
            payer=payer,
            token_accounts=[token_account_a, token_account_b],
            pool_addresses=[amm_id],
        )
        
        # Build instruction
        instruction = self.raydium_builder.build_swap_instruction(
            payer=payer,
            amm_id=amm_id,
            token_account_a=token_account_a,
            token_account_b=token_account_b,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
        )
        
        # Build transaction
        blockhash, _, _ = self.executor.get_blockhash()
        tx_bytes = self._build_transaction_bytes(
            payer=payer,
            instructions=[instruction],
            blockhash=blockhash,
        )
        
        # Execute
        result = await self.executor.execute("swap", tx_bytes)
        
        return {
            "signature": result.signature,
            "success": result.success,
            "error": result.error,
            "latency_ms": result.latency_ms,
        }
    
    async def execute_meteora_swap(
        self,
        payer: str,
        pool_address: str,
        input_token_account: str,
        output_token_account: str,
        amount_in: int,
        min_amount_out: int,
    ) -> dict:
        """
        Execute a Meteora DAMM v2 swap with hot path optimization.
        """
        # Prefetch
        context = await self.prefetch_for_trade(
            payer=payer,
            token_accounts=[input_token_account, output_token_account],
            pool_addresses=[pool_address],
        )
        
        # Build instruction
        instruction = self.meteora_builder.build_swap_instruction(
            payer=payer,
            pool_address=pool_address,
            input_token_account=input_token_account,
            output_token_account=output_token_account,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
        )
        
        # Build and execute
        blockhash, _, _ = self.executor.get_blockhash()
        tx_bytes = self._build_transaction_bytes(
            payer=payer,
            instructions=[instruction],
            blockhash=blockhash,
        )
        
        result = await self.executor.execute("swap", tx_bytes)
        
        return {
            "signature": result.signature,
            "success": result.success,
            "error": result.error,
            "latency_ms": result.latency_ms,
        }
    
    def _build_transaction_bytes(
        self,
        payer: str,
        instructions: list,
        blockhash: str,
    ) -> bytes:
        """
        Build transaction bytes - placeholder implementation.
        
        In production, this would use solders/solana-py to:
        1. Create transaction with instructions
        2. Set recent blockhash (from cache)
        3. Sign with keypair
        4. Serialize to bytes
        
        Key point: blockhash comes from cache, NOT RPC call
        """
        # Placeholder - actual implementation uses solders
        return b""


async def main():
    """
    Example usage of Hot Path trading.
    """
    # Configuration
    RPC_URL = "https://api.mainnet-beta.solana.com"
    JITO_API_KEY = "your-jito-api-key"
    BLOXROUTE_API_KEY = "your-bloxroute-api-key"
    
    # Create trader
    trader = HotPathTrader(
        rpc_url=RPC_URL,
        jito_api_key=JITO_API_KEY,
        bloxroute_api_key=BLOXROUTE_API_KEY,
    )
    
    # Start background prefetching
    await trader.start()
    
    try:
        # Example: PumpFun buy
        result = await trader.execute_pumpfun_buy(
            payer="YourWalletPubkey",
            mint="TokenMintAddress",
            bonding_curve="BondingCurveAddress",
            amount=1000000,
            max_sol_cost=1000000000,  # 1 SOL
            token_account="YourTokenAccount",
        )
        print(f"Trade result: {result}")
        
        # Check metrics
        metrics = trader.executor.get_metrics()
        print(f"Metrics: {metrics}")
        
    finally:
        # Cleanup
        await trader.stop()


if __name__ == "__main__":
    asyncio.run(main())
