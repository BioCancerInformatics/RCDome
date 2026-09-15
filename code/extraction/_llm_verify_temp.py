def llm_verify(gene, rcd_form):
    tokens_total = 0
    time.sleep(0.1)
    prompt_a = "Is gene " + gene + " mechanistically involved in the regulated cell death form " + rcd_form + "? Answer only CONFIRMED or UNCLEAR."
    resp_a, tok_a = call_llm(prompt_a)
    tokens_total += tok_a
    call_a_confirmed = resp_a and resp_a.startswith('CONFIRMED')
    pmids, abstract_text, total_count = fetch_pmids_and_abstracts(gene, rcd_form)
    if pmids and abstract_text not in ("PubMed search failed", "No PubMed hits"):
        chunks = [abstract_text[i:i+4000] for i in range(0, min(len(abstract_text), 20000), 4000)]
        batch_votes = []
        for chunk in chunks:
            time.sleep(0.1)
            prompt_b = "Based on these PubMed abstracts, is gene " + gene + " genuinely involved in " + rcd_form + "? Answer only CONFIRMED or UNCLEAR.

ABSTRACTS:
" + chunk
            resp_b, tok_b = call_llm(prompt_b, max_tokens=20)
            tokens_total += tok_b
            if resp_b:
                batch_votes.append(resp_b.startswith('CONFIRMED'))
        if batch_votes:
            confirm_count = sum(batch_votes)
            call_b_confirmed = confirm_count >= len(batch_votes) / 2
        else:
            call_b_confirmed = None
    else:
        call_b_confirmed = None
    if call_a_confirmed and call_b_confirmed:
        status = "CONFIRMED"; basis = "LLM knowledge + PubMed both confirm"
    elif call_a_confirmed and call_b_confirmed is False:
        status = "NEEDS_LITERATURE"; basis = "LLM confirms; PubMed does not"
    elif call_a_confirmed and call_b_confirmed is None:
        status = "CONFIRMED"; basis = "LLM confirms; no PubMed data"
    elif call_a_confirmed is False and call_b_confirmed:
        status = "NEEDS_CONTEXT"; basis = "PubMed confirms; LLM uncertain"
    elif call_a_confirmed is None and call_b_confirmed:
        status = "CONFIRMED"; basis = "PubMed confirms"
    elif call_a_confirmed is False and call_b_confirmed is False:
        status = "UNCLEAR"; basis = "Neither confirms"
    elif call_a_confirmed is False and call_b_confirmed is None:
        status = "UNCLEAR"; basis = "LLM uncertain; no PubMed"
    else:
        status = "UNVERIFIED"; basis = "Both calls failed"
    return {
        "llm_status": status, "llm_basis": basis,
        "llm_pmids": ";".join(pmids[:100]) if pmids else "",
        "llm_evidence_force": total_count,
        "llm_tokens": tokens_total,
    }
