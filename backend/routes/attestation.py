"""
Strategy Performance Attestation API — user-facing endpoints.
"""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api", tags=["attestation"])

db = None

def init_db(database):
    global db
    db = database


@router.get("/strategies/{strategy_id}/attestation")
async def get_strategy_attestation(strategy_id: str, demo: bool = Query(False)):
    """Get on-chain performance attestation for a strategy."""
    contract_addr = os.environ.get("CONTRACT_ADDRESS_SEPOLIA", "")

    if demo or not contract_addr:
        # Return latest attestation from DB
        record = await db.performance_attestations.find_one(
            {}, {"_id": 0}, sort=[("timestamp", -1)]
        )
        if record:
            for d in record.get("details", []):
                if str(d.get("strategy_id")) == str(strategy_id) or d.get("name", "").lower() in strategy_id.lower():
                    return {
                        "success": True,
                        "attestation": {
                            **d.get("metrics", {}),
                            "timestamp": record.get("timestamp"),
                            "on_chain": d.get("status") == "attested",
                            "tx_hash": d.get("tx_hash"),
                            "contract_address": contract_addr or None,
                            "explorer_url": f"https://sepolia.etherscan.io/address/{contract_addr}" if contract_addr else None,
                        },
                    }

        # Fallback: try reading from contract_manager
        try:
            from services.contract_manager import get_strategy_performance
            idx = int(strategy_id) if strategy_id.isdigit() else 0
            perf = await get_strategy_performance(idx)
            return {
                "success": True,
                "attestation": {
                    **perf,
                    "contract_address": contract_addr or None,
                    "explorer_url": f"https://sepolia.etherscan.io/address/{contract_addr}" if contract_addr else None,
                },
            }
        except Exception:
            pass

        return {
            "success": True,
            "attestation": None,
            "message": "No attestation data available. Run attestation cycle first.",
        }

    # Live on-chain read
    from services.contract_manager import get_strategy_performance
    idx = int(strategy_id) if strategy_id.isdigit() else 0
    perf = await get_strategy_performance(idx)
    return {
        "success": True,
        "attestation": {
            **perf,
            "contract_address": contract_addr,
            "explorer_url": f"https://sepolia.etherscan.io/address/{contract_addr}",
        },
    }
