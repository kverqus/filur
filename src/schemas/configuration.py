from schema import Optional, Or, Use, Schema


config_schema = Schema(
    {
        "files": [
            {
                "file": Use(str, error="No file supplied"),
                "direction": Or("forward", "reverse"),
                Optional("order_by"): Or("none", "weight"),
                Optional("rows"): int,
                "patterns": [
                    {
                        "pattern": Use(str),
                        "type": Or("string", "regex"),
                        Optional("weight"): int,
                        Optional("operator"): Or("AND", "OR", "NOT"),
                    }
                ],
                "output": {
                    "path": Use(str, error="No output path specified"),
                    "type": Or("json", "html", "console", error="No output type specified")
                },
            }
        ]
    }
)