# Sol Trade SDK for Python

<p align="center">
    <strong>A high-performance Python SDK for low-latency Solana DEX trading</strong>
</p>

<p align="center">
    <a href="https://pypi.org/project/sol-trade-sdk">
        <img src="https://img.shields.io/pypi/v/sol-trade-sdk.svg" alt="PyPI">
    </a>
    <a href="https://pypi.org/project/sol-trade-sdk">
        <img src="https://img.shields.io/pypi/pyversions/sol-trade-sdk.svg" alt="Python Versions">
    </a>
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
    </a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Solana-9945FF?style=for-the-badge&logo=solana&logoColor=white" alt="Solana">
    <img src="https://img.shields.io/badge/DEX-4B8BBE?style=for-the-badge&logo=bitcoin&logoColor=white" alt="DEX Trading">
</p>

<p align="center">
    <a href="README_CN.md">中文</a> |
    <a href="https://fnzero.dev/">Website</a> |
    <a href="https://t.me/fnzero_group">Telegram</a> |
    <a href="https://discord.gg/vuazbGkqQE">Discord</a>
</p>

---

A comprehensive, high-performance Python SDK for Solana DEX trading with support for multiple protocols and MEV providers.

## Features

- **Multiple DEX Support**: PumpFun, PumpSwap, Bonk, Raydium AMM V4, Raydium CPMM, Meteora DAMM V2
- **SWQoS Integration**: Jito, Bloxroute, ZeroSlot, Temporal, FlashBlock, Helius, and more
- **High Performance**: LRU/TTL/Sharded caching, connection pooling, parallel execution
- **Low Latency**: Optimized for sub-second trade execution
- **Security First**: Integer overflow protection, secure key storage, input validation
- **Modular Design**: Use only what you need

## Installation

```bash
pip install sol-trade-sdk
```

## Quick Start

```python
import asyncio
from sol_trade_sdk import (
    create_gas_fee_strategy,
    TradeExecutor,
    TradeConfig,
    SwqosType,
    TradeType,
)

async def main():
    # Create gas strategy
    gas_strategy = create_gas_fee_strategy()

    # Create trade executor
    config = TradeConfig(
        rpc_url="https://api.mainnet-beta.solana.com",
        swqos_configs=[{"type": SwqosType.JITO}],
        gas_fee_strategy=gas_strategy,
    )

    executor = TradeExecutor(config)

    # Execute trade
    result = await executor.execute(
        trade_type=TradeType.BUY,
        transaction=serialized_tx,
    )
    print(f"Transaction signature: {result.signature}")

asyncio.run(main())
```

## Security Features

```python
from sol_trade_sdk.security import SecureKeyStorage, validate_rpc_url

# Secure key storage with memory encryption
storage = SecureKeyStorage.from_keypair(keypair)
with storage.unlock() as kp:
    signature = kp.sign(message)

# Input validation
validate_rpc_url("https://api.mainnet-beta.solana.com")
```

## Architecture

| Module | Description |
|--------|-------------|
| `cache` | LRU, TTL, and sharded caches |
| `calc` | AMM calculations for all DEXes |
| `hotpath` | Zero-RPC hot path execution |
| `instruction` | Instruction builders |
| `pool` | Connection and worker pools |
| `rpc` | High-performance RPC clients |
| `security` | Secure key storage, validators |
| `swqos` | MEV provider clients |

## Supported Protocols

### PumpFun
- Bonding curve calculations
- Buy/Sell instruction building
- PDA derivation

### PumpSwap
- Pool calculations
- Fee breakdown (LP, protocol, curve)
- Instruction building

### Raydium
- AMM V4 calculations
- CPMM calculations
- Authority PDA derivation

### Meteora
- DAMM V2 support
- Pool PDA derivation

## SWQoS Providers

| Provider | Min Tip | Features |
|----------|---------|----------|
| Jito | 0.001 SOL | Bundle support, gRPC |
| Bloxroute | 0.0003 SOL | High reliability |
| ZeroSlot | 0.0001 SOL | Low latency |
| Temporal | 0.0001 SOL | Fast confirmation |
| FlashBlock | 0.0001 SOL | Competitive pricing |
| Helius | 0.000005 SOL | SWQoS-only mode |

## Requirements

- Python >= 3.9
- solders >= 0.18.0
- solana >= 0.30.0

## License

MIT License

## Contact

- Official Website: https://fnzero.dev/
- Project Repository: https://github.com/sol-trade-sdk/sol-trade-sdk-python
- Telegram Group: https://t.me/fnzero_group
- Discord: https://discord.gg/vuazbGkqQE
