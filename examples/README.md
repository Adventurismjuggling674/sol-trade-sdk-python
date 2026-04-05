# Sol Trade SDK Python Examples

This directory contains examples demonstrating how to use the Sol Trade SDK for Python.

## Examples Summary

| Description | File | Run Command |
|-------------|------|-------------|
| Create and configure TradingClient instance | [trading_client.py](trading_client.py) | `python examples/trading_client.py` |
| Share infrastructure across multiple wallets | [shared_infrastructure.py](shared_infrastructure.py) | `python examples/shared_infrastructure.py` |
| PumpFun token sniping trading | [pumpfun_sniper_trading.py](pumpfun_sniper_trading.py) | `python examples/pumpfun_sniper_trading.py` |
| PumpSwap trading operations | [pumpswap_trading.py](pumpswap_trading.py) | `python examples/pumpswap_trading.py` |
| Raydium CPMM trading operations | [raydium_cpmm_trading.py](raydium_cpmm_trading.py) | `python examples/raydium_cpmm_trading.py` |
| Meteora DAMM V2 trading operations | [meteora_damm_v2_trading.py](meteora_damm_v2_trading.py) | `python examples/meteora_damm_v2_trading.py` |
| Custom instruction middleware example | [middleware_system.py](middleware_system.py) | `python examples/middleware_system.py` |
| Address lookup table example | [address_lookup.py](address_lookup.py) | `python examples/address_lookup.py` |
| Gas fee strategy example | [gas_fee_strategy.py](gas_fee_strategy.py) | `python examples/gas_fee_strategy.py` |

## Environment Setup

Set the following environment variables before running examples:

```bash
export RPC_URL="https://api.mainnet-beta.solana.com"
# Or use Helius for better performance:
# export RPC_URL="https://mainnet.helius-rpc.com/?api-key=your_api_key"
```

## Quick Start

1. Install the SDK:
```bash
pip install sol-trade-sdk
```

2. Set up your keypair and configuration

3. Run an example:
```bash
python examples/trading_client.py
```

## Important Notes

- Replace placeholder keypairs with your actual keypairs
- Configure SWQoS services with your API tokens for better transaction landing
- Test thoroughly before using on mainnet
- Monitor balances and transaction fees
