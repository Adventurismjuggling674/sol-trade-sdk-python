"""
Trading Example for Sol Trade SDK Python
"""

import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from sol_trade_sdk import (
    TradingClient,
    DexType,
    TradeTokenType,
    TradeConfig,
    SwqosConfig,
    SwqosType,
    SwqosRegion,
    PumpFunParams,
    BondingCurveAccount,
    create_gas_fee_strategy,
    create_trade_config,
)
from sol_trade_sdk.instruction import (
    get_bonding_curve_pda,
    get_creator_vault_pda,
    get_associated_token_address,
    TOKEN_PROGRAM,
)


async def main():
    # 1. Setup wallet
    private_key_base58 = "your_private_key_here"
    payer = Keypair.from_base58_string(private_key_base58)

    # 2. Configure SWQOS services
    swqos_configs = [
        SwqosConfig(type=SwqosType.DEFAULT, region=SwqosRegion.FRANKFURT, api_key=""),
        SwqosConfig(
            type=SwqosType.JITO,
            region=SwqosRegion.FRANKFURT,
            api_key="your_jito_uuid",
        ),
    ]

    # 3. Create trade configuration
    rpc_url = "https://mainnet.helius-rpc.com/?api-key=your_api_key"
    config = create_trade_config(rpc_url, swqos_configs)

    # 4. Create trading client
    async with TradingClient(payer, config) as client:
        print(f"Trading client created for wallet: {client.get_payer()}")

        # 5. Example: Build PumpFun parameters
        mint = Pubkey.from_string("your_token_mint_here")
        bonding_curve = get_bonding_curve_pda(mint)
        creator = Pubkey.from_string("creator_address")
        creator_vault = get_creator_vault_pda(creator)

        pump_fun_params = PumpFunParams(
            bonding_curve=BondingCurveAccount(
                discriminator=0,
                account=bonding_curve,
                virtual_token_reserves=1000000000,
                virtual_sol_reserves=30000000000,
                real_token_reserves=800000000,
                real_sol_reserves=24000000000,
                token_total_supply=1000000000,
                complete=False,
                creator=creator,
                is_mayhem_mode=False,
                is_cashback_coin=False,
            ),
            associated_bonding_curve=get_associated_token_address(
                bonding_curve, mint, TOKEN_PROGRAM
            ),
            creator_vault=creator_vault,
            token_program=TOKEN_PROGRAM,
        )

        # 6. Get recent blockhash
        blockhash = await client.get_latest_blockhash()

        # 7. Build buy parameters
        from sol_trade_sdk import TradeBuyParams

        buy_params = TradeBuyParams(
            dex_type=DexType.PUMPFUN,
            input_token_type=TradeTokenType.WSOL,
            mint=mint,
            input_token_amount=10000000,  # 0.01 SOL
            extension_params=pump_fun_params,
            slippage_basis_points=500,  # 5%
            recent_blockhash=str(blockhash.blockhash),
            wait_tx_confirmed=True,
            create_mint_ata=True,
            gas_fee_strategy=create_gas_fee_strategy(),
        )

        # 8. Execute buy
        result = await client.buy(buy_params)
        if result.success:
            print(f"Buy successful! Signatures: {result.signatures}")
        else:
            print(f"Buy failed: {result.error}")

        # 9. Example: Sell tokens
        from sol_trade_sdk import TradeSellParams

        sell_params = TradeSellParams(
            dex_type=DexType.PUMPFUN,
            output_token_type=TradeTokenType.WSOL,
            mint=mint,
            input_token_amount=1000000,  # Token amount to sell
            extension_params=pump_fun_params,
            slippage_basis_points=500,
            recent_blockhash=str(blockhash.blockhash),
            with_tip=True,
            wait_tx_confirmed=True,
            gas_fee_strategy=create_gas_fee_strategy(),
        )

        sell_result = await client.sell(sell_params)
        if sell_result.success:
            print(f"Sell successful! Signatures: {sell_result.signatures}")
        else:
            print(f"Sell failed: {sell_result.error}")


if __name__ == "__main__":
    asyncio.run(main())
