CANONICAL_ENTITY_MAP = {
    "ncr": ["ncr", "ncr_description", "contract_clause"],
    "contract_clause": ["contract", "contract_clause"],
    "dpr": ["dpr", "dpr_narrative"],
    "correspondence": ["correspondence"]
}

def resolve_entity_types(router_label: str):
    return CANONICAL_ENTITY_MAP.get(router_label, [router_label])

    