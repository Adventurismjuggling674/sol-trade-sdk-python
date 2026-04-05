"""
SWQoS provider implementations.
Based on sol-trade-sdk Rust implementation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class SwqosType(Enum):
    """SWQOS service provider types"""
    JITO = "Jito"
    NEXT_BLOCK = "NextBlock"
    ZERO_SLOT = "ZeroSlot"
    TEMPORAL = "Temporal"
    BLOXROUTE = "Bloxroute"
    NODE1 = "Node1"
    FLASH_BLOCK = "FlashBlock"
    BLOCK_RAZOR = "BlockRazor"
    ASTRALANE = "Astralane"
    STELLIUM = "Stellium"
    LIGHTSPEED = "Lightspeed"
    SOYAS = "Soyas"
    SPEEDLANDING = "Speedlanding"
    HELIUS = "Helius"
    DEFAULT = "Default"


class SwqosRegion(Enum):
    """SWQOS service regions"""
    NEW_YORK = "NewYork"
    FRANKFURT = "Frankfurt"
    AMSTERDAM = "Amsterdam"
    SLC = "SLC"
    TOKYO = "Tokyo"
    LONDON = "London"
    LOS_ANGELES = "LosAngeles"
    DEFAULT = "Default"


@dataclass
class SwqosConfig:
    """SWQOS configuration"""
    swqos_type: SwqosType
    api_key: Optional[str] = None
    region: SwqosRegion = SwqosRegion.DEFAULT
    url: Optional[str] = None
    timeout_ms: int = 5000
    max_retries: int = 3
    enabled: bool = True

    def is_blacklisted(self) -> bool:
        """Check if this provider is blacklisted"""
        return not self.enabled

    def swqos_type_value(self) -> str:
        """Get SWQOS type value"""
        return self.swqos_type.value


class SwqosClient:
    """Base SWQOS client"""

    def __init__(self, config: SwqosConfig):
        self.config = config
        self._stats = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "avg_latency_ms": 0,
        }

    async def submit_transaction(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction to SWQOS provider"""
        raise NotImplementedError("Subclass must implement submit_transaction")

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return self._stats.copy()

    def update_stats(self, success: bool, latency_ms: int):
        """Update client statistics"""
        self._stats["requests"] += 1
        if success:
            self._stats["successes"] += 1
        else:
            self._stats["failures"] += 1

        # Update average latency
        n = self._stats["requests"]
        self._stats["avg_latency_ms"] = (
            (self._stats["avg_latency_ms"] * (n - 1) + latency_ms) // n
        )


class JitoClient(SwqosClient):
    """Jito SWQOS client"""

    def __init__(self, config: SwqosConfig):
        super().__init__(config)
        self.bundle_url = config.url or "https://mainnet.block-engine.jito.wtf"

    async def submit_transaction(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction via Jito"""
        # Placeholder implementation
        return {
            "success": True,
            "signature": "jito_signature_placeholder",
            "provider": "Jito",
        }


class BloxrouteClient(SwqosClient):
    """Bloxroute SWQOS client"""

    def __init__(self, config: SwqosConfig):
        super().__init__(config)
        self.gateway_url = config.url or "https://solana.dex.blxrbdn.com"

    async def submit_transaction(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction via Bloxroute"""
        return {
            "success": True,
            "signature": "bloxroute_signature_placeholder",
            "provider": "Bloxroute",
        }


class ZeroSlotClient(SwqosClient):
    """ZeroSlot SWQOS client"""

    def __init__(self, config: SwqosConfig):
        super().__init__(config)
        self.api_url = config.url or "https://api.zeroslot.io"

    async def submit_transaction(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction via ZeroSlot"""
        return {
            "success": True,
            "signature": "zeroslot_signature_placeholder",
            "provider": "ZeroSlot",
        }


class HeliusClient(SwqosClient):
    """Helius SWQOS client"""

    def __init__(self, config: SwqosConfig):
        super().__init__(config)
        self.api_url = config.url or "https://api.helius-rpc.com"

    async def submit_transaction(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction via Helius"""
        return {
            "success": True,
            "signature": "helius_signature_placeholder",
            "provider": "Helius",
        }


class SwqosClientFactory:
    """Factory for creating SWQOS clients"""

    @staticmethod
    def create_client(config: SwqosConfig) -> SwqosClient:
        """Create SWQOS client based on config type"""
        if config.swqos_type == SwqosType.JITO:
            return JitoClient(config)
        elif config.swqos_type == SwqosType.BLOXROUTE:
            return BloxrouteClient(config)
        elif config.swqos_type == SwqosType.ZERO_SLOT:
            return ZeroSlotClient(config)
        elif config.swqos_type == SwqosType.HELIUS:
            return HeliusClient(config)
        else:
            # Default generic client
            return SwqosClient(config)


class SwqosManager:
    """Manager for multiple SWQOS clients"""

    def __init__(self):
        self.clients: Dict[SwqosType, SwqosClient] = {}

    def add_client(self, client: SwqosClient) -> "SwqosManager":
        """Add a SWQOS client"""
        self.clients[client.config.swqos_type] = client
        return self

    def get_client(self, swqos_type: SwqosType) -> Optional[SwqosClient]:
        """Get SWQOS client by type"""
        return self.clients.get(swqos_type)

    def get_all_clients(self) -> list:
        """Get all enabled clients"""
        return [c for c in self.clients.values() if c.config.enabled]

    async def submit_to_all(
        self,
        transaction: bytes,
        tip: int = 0,
    ) -> Dict[str, Any]:
        """Submit transaction to all enabled providers"""
        import asyncio

        tasks = []
        for client in self.get_all_clients():
            tasks.append(client.submit_transaction(transaction, tip))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "results": results,
            "total": len(tasks),
            "successful": sum(1 for r in results if isinstance(r, dict) and r.get("success")),
        }

    def get_all_stats(self) -> Dict[SwqosType, Dict[str, Any]]:
        """Get stats for all clients"""
        return {t: c.get_stats() for t, c in self.clients.items()}
