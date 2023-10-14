def parse_soho_flow_id(raw_flow_id: str) -> tuple[int, int]:
    str_offer_ids, str_flow_ids = raw_flow_id.split(":")
    flow_id = next(map(int, str_flow_ids.split(",")))
    offer_id = next(map(int, str_offer_ids.split(",")))
    return offer_id, flow_id
