"""
Middleware System Example

This example demonstrates how to use the middleware system
to modify, add, or remove instructions before transaction execution.
"""

import asyncio
from sol_trade_sdk.middleware import (
    MiddlewareManager,
    LoggingMiddleware,
    ValidationMiddleware,
    TimerMiddleware,
    MetricsMiddleware,
)


async def main():
    # Create middleware manager
    manager = MiddlewareManager()

    # Add middlewares in order (executes in the order added)
    manager.add_middleware(ValidationMiddleware(max_instructions=100))
    manager.add_middleware(TimerMiddleware())
    manager.add_middleware(LoggingMiddleware())
    manager.add_middleware(MetricsMiddleware())

    print("Middleware manager created with 4 middlewares:")
    print("  1. ValidationMiddleware - validates instructions")
    print("  2. TimerMiddleware - times instruction processing")
    print("  3. LoggingMiddleware - logs instruction details")
    print("  4. MetricsMiddleware - collects metrics")

    # In a real scenario, you would apply middlewares to instructions:
    # processed = await manager.apply(instructions, "PumpFun", is_buy=True)


if __name__ == "__main__":
    asyncio.run(main())
