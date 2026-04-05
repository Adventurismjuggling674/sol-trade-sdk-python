"""
Gas Fee Strategy Example

This example demonstrates how to configure gas fee strategy
for optimal transaction landing.
"""

import asyncio
from sol_trade_sdk import GasFeeStrategy


async def main():
    # Create gas fee strategy
    gas_fee_strategy = GasFeeStrategy()

    # Set global fee strategy
    # Parameters:
    # - compute_unit_price: base compute unit price (micro-lamports)
    # - compute_unit_limit: maximum compute units
    # - priority_fee: priority fee in lamports
    # - rent_exempt_balance: rent-exempt balance for accounts
    # - slippage_bps: slippage in basis points
    # - tip_bps: tip percentage in basis points
    gas_fee_strategy.set_global_fee_strategy(
        compute_unit_price=150000,
        compute_unit_limit=150000,
        priority_fee=500000,
        rent_exempt_balance=500000,
        slippage_bps=0.001,
        tip_bps=0.001,
    )

    print("Gas fee strategy configured:")
    print(f"  Compute unit price: {gas_fee_strategy.compute_unit_price}")
    print(f"  Compute unit limit: {gas_fee_strategy.compute_unit_limit}")
    print(f"  Priority fee: {gas_fee_strategy.priority_fee}")

    # You can also set individual parameters
    gas_fee_strategy.set_compute_unit_price(200000)
    gas_fee_strategy.set_priority_fee(600000)

    print("\nUpdated gas fee strategy:")
    print(f"  Compute unit price: {gas_fee_strategy.compute_unit_price}")
    print(f"  Priority fee: {gas_fee_strategy.priority_fee}")


if __name__ == "__main__":
    asyncio.run(main())
