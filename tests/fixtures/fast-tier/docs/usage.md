# Using stockroom

Add stock with `store.add_item(name, qty, price)`; it returns the new item.

`parse_money` handles prices written like `$1,200.50`.

Set cache_ttl in config/settings.toml to change how long stock levels are cached.
