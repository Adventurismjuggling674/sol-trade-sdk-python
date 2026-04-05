# Sol Trade SDK for Python

<p align="center">
    <strong>高性能 Python SDK，用于低延迟 Solana DEX 交易</strong>
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
    <a href="README.md">English</a> |
    <a href="https://fnzero.dev/">官网</a> |
    <a href="https://t.me/fnzero_group">Telegram</a> |
    <a href="https://discord.gg/vuazbGkqQE">Discord</a>
</p>

---

一个全面的高性能 Python SDK，用于 Solana DEX 交易，支持多种协议和 MEV 提供商。

## 特性

- **多 DEX 支持**: PumpFun、PumpSwap、Bonk、Raydium AMM V4、Raydium CPMM、Meteora DAMM V2
- **SWQoS 集成**: Jito、Bloxroute、ZeroSlot、Temporal、FlashBlock、Helius 等
- **高性能**: LRU/TTL/分片缓存、连接池、并行执行
- **低延迟**: 针对亚秒级交易执行优化
- **安全优先**: 整数溢出保护、安全密钥存储、输入验证
- **模块化设计**: 按需使用

## 安装

```bash
pip install sol-trade-sdk
```

## 快速开始

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
    # 创建 Gas 策略
    gas_strategy = create_gas_fee_strategy()

    # 创建交易执行器
    config = TradeConfig(
        rpc_url="https://api.mainnet-beta.solana.com",
        swqos_configs=[{"type": SwqosType.JITO}],
        gas_fee_strategy=gas_strategy,
    )

    executor = TradeExecutor(config)

    # 执行交易
    result = await executor.execute(
        trade_type=TradeType.BUY,
        transaction=serialized_tx,
    )
    print(f"交易签名: {result.signature}")

asyncio.run(main())
```

## 安全特性

```python
from sol_trade_sdk.security import SecureKeyStorage, validate_rpc_url

# 带内存加密的安全密钥存储
storage = SecureKeyStorage.from_keypair(keypair)
with storage.unlock() as kp:
    signature = kp.sign(message)

# 输入验证
validate_rpc_url("https://api.mainnet-beta.solana.com")
```

## 架构

| 模块 | 描述 |
|------|------|
| `cache` | LRU、TTL 和分片缓存 |
| `calc` | 所有 DEX 的 AMM 计算 |
| `hotpath` | 零-RPC 热路径执行 |
| `instruction` | 指令构建器 |
| `pool` | 连接池和工作池 |
| `rpc` | 高性能 RPC 客户端 |
| `security` | 安全密钥存储、验证器 |
| `swqos` | MEV 提供商客户端 |

## 支持的协议

### PumpFun
- 联合曲线计算
- 买卖指令构建
- PDA 派生

### PumpSwap
- 池计算
- 费用分解 (LP、协议、曲线)
- 指令构建

### Raydium
- AMM V4 计算
- CPMM 计算
- 权限 PDA 派生

### Meteora
- DAMM V2 支持
- 池 PDA 派生

## SWQoS 提供商

| 提供商 | 最低小费 | 特性 |
|----------|---------|----------|
| Jito | 0.001 SOL | 捆绑支持、gRPC |
| Bloxroute | 0.0003 SOL | 高可靠性 |
| ZeroSlot | 0.0001 SOL | 低延迟 |
| Temporal | 0.0001 SOL | 快速确认 |
| FlashBlock | 0.0001 SOL | 有竞争力的价格 |
| Helius | 0.000005 SOL | 仅 SWQoS 模式 |

## 环境要求

- Python >= 3.9
- solders >= 0.18.0
- solana >= 0.30.0

## 许可证

MIT License

## 联系方式

- 官方网站: https://fnzero.dev/
- 项目仓库: https://github.com/sol-trade-sdk/sol-trade-sdk-python
- Telegram 群组: https://t.me/fnzero_group
- Discord: https://discord.gg/vuazbGkqQE
