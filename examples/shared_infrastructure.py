"""
Shared Infrastructure Example

This example demonstrates how to share infrastructure across multiple wallets.
The infrastructure (RPC client, SWQOS clients) is created once and shared.
"""

import asyncio
import os
from sol_trade_sdk import (
    InfrastructureConfig,
    TradingInfrastructure,
    TradingClient,
    SwqosConfig,
    SwqosType,
    SwqosRegion,
)
from solders.keypair import Keypair


async def main():
    rpc_url = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")

    # Configure SWQoS services
    swqos_configs = [
        SwqosConfig(type=SwqosType.DEFAULT, url=rpc_url),
        SwqosConfig(type=SwqosType.JITO, uuid="your_uuid", region=SwqosRegion.FRANKFURT),
        SwqosConfig(type=SwqosType.BLOXROUTE, api_token="your_api_token", region=SwqosRegion.FRANKFURT),
    ]

    # Create infrastructure once (expensive operation)
    infra_config = InfrastructureConfig(
        rpc_url=rpc_url,
        swqos_configs=swqos_configs,
    )
    infrastructure = await TradingInfrastructure.new(infra_config)
    print("Infrastructure created successfully!")

    # Create multiple clients sharing the same infrastructure (fast)
    payer1 = Keypair()  # Use your first keypair
    payer2 = Keypair()  # Use your second keypair
    payer3 = Keypair()  # Use your third keypair

    client1 = TradingClient.from_infrastructure(payer1, infrastructure, use_seed_optimize=True)
    client2 = TradingClient.from_infrastructure(payer2, infrastructure, use_seed_optimize=True)
    client3 = TradingClient.from_infrastructure(payer3, infrastructure, use_seed_optimize=True)

    print(f"Client 1: {client1.payer_pubkey}")
    print(f"Client 2: {client2.payer_pubkey}")
    print(f"Client 3: {client3.payer_pubkey}")

    # All clients share the same RPC and SWQoS connections
    print("All clients share the same infrastructure!")


if __name__ == "__main__":
    asyncio.run(main())
