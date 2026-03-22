"""
RW-05 — Run all seed scripts in order.
Usage: python -m db.seeds.run_all_seeds
"""

import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.seeds import equipment_seed, pricing_seed


async def main():
    print("=" * 60)
    print("ScopeSnap Database Seed Runner")
    print("=" * 60)

    print("\n[1/2] Equipment Models")
    await equipment_seed.run()

    print("\n[2/2] Pricing Rules")
    await pricing_seed.run()

    print("\n" + "=" * 60)
    print("✅ All seeds complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
