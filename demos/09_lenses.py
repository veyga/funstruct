"""Lenses: composable getters and setters for immutable data.

The problem: updating deeply nested immutable structures requires
rebuilding the entire path manually.

    # Without lenses:
    config.put("app", config["app"].put("db", config["app"]["db"].put("host", "new")))

    # With lenses:
    host_lens = at("app") >> at("db") >> at("host")
    host_lens.set(config, "new")

A Lens[S, A] focuses on a value of type A inside a structure S:
    get(s)        → A
    set(s, a)     → S  (returns new S with a at the focus)
    modify(s, f)  → S  (applies f to the focused value)

Compose with >> to focus deeper.
"""

from funstruct.collections.frozendict import frozendict
from funstruct.experimental.optics import Lens, at


def main():
    config = frozendict(
        {
            "app": {
                "name": "myservice",
                "db": {
                    "host": "localhost",
                    "port": 5432,
                    "pool_size": 10,
                },
                "cache": {
                    "ttl": 300,
                    "backend": "redis",
                },
            },
            "deploy": {
                "region": "us-east-1",
                "replicas": 3,
            },
        }
    )

    print("=== Lenses: composable getters/setters ===\n")

    # Single-level lens
    app_lens = at("app")
    print(f"  at('app').get(config)['name'] = {app_lens.get(config)['name']}")

    # Composed lens — focus through multiple levels
    host_lens = at("app") >> at("db") >> at("host")
    port_lens = at("app") >> at("db") >> at("port")
    pool_lens = at("app") >> at("db") >> at("pool_size")
    ttl_lens = at("app") >> at("cache") >> at("ttl")
    replicas_lens = at("deploy") >> at("replicas")

    print(f"\n  host_lens.get(config) = {host_lens.get(config)}")
    print(f"  port_lens.get(config) = {port_lens.get(config)}")

    # Set — returns new config with the change, original untouched
    new_config = host_lens.set(config, "prod-db.internal")
    print(f"\n  host_lens.set(config, 'prod-db.internal'):")
    print(f"    new host = {host_lens.get(new_config)}")
    print(f"    old host = {host_lens.get(config)}  (unchanged)")

    # Modify — apply a function to the focused value
    scaled = pool_lens.modify(config, lambda n: n * 2)
    print(f"\n  pool_lens.modify(config, lambda n: n * 2):")
    print(f"    pool_size = {pool_lens.get(scaled)}")

    # Multiple modifications — each returns a new config
    prod_config = config
    prod_config = host_lens.set(prod_config, "prod-db.internal")
    prod_config = port_lens.set(prod_config, 5433)
    prod_config = pool_lens.modify(prod_config, lambda n: n * 4)
    prod_config = ttl_lens.set(prod_config, 60)
    prod_config = replicas_lens.modify(prod_config, lambda n: n * 3)

    print(f"\n  Production config (5 lens operations):")
    print(f"    db.host      = {host_lens.get(prod_config)}")
    print(f"    db.port      = {port_lens.get(prod_config)}")
    print(f"    db.pool_size = {pool_lens.get(prod_config)}")
    print(f"    cache.ttl    = {ttl_lens.get(prod_config)}")
    print(f"    replicas     = {replicas_lens.get(prod_config)}")

    # Original is completely untouched
    print(f"\n  Original config still intact:")
    print(f"    db.host      = {host_lens.get(config)}")
    print(f"    replicas     = {replicas_lens.get(config)}")

    # JSON round-trip with lenses
    import json

    print(f"\n  JSON round-trip:")
    s = json.dumps(prod_config.to_dict(), indent=2)
    print(f"    {s[:60]}...")


if __name__ == "__main__":
    main()
