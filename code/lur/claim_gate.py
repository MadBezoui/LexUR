def summarize_claim(claim, gates):
    req_gates = claim.get("gates", [])
    
    if not req_gates:
        return "exploratory"
        
    has_check = False
    for g in req_gates:
        if g not in gates:
            return "exploratory"
            
        res = gates[g].get("result")
        
        if res == "FAIL":
            return "unsupported"
            
        if res == "CHECK" or not gates[g].get("pass", True):
            has_check = True
            
    if has_check:
        return "qualified"
        
    return "supported"
