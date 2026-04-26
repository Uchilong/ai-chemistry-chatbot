"""Small retrieval-ready chemistry knowledge snippets with citation metadata."""

from typing import Dict, List


KB_SNIPPETS: List[Dict[str, str]] = [
    {
        "id": "stoich_workflow",
        "title": "Stoichiometry Workflow",
        "source": "Internal Chemistry Notes",
        "content": "For stoichiometry: write balanced equation, convert given values to moles, apply mole ratio, then convert to requested unit. Track significant figures.",
    },
    {
        "id": "acid_base_core",
        "title": "Acid-Base Core",
        "source": "Internal Chemistry Notes",
        "content": "Strong acids and bases fully dissociate in water. Weak acids/bases require equilibrium expressions (Ka or Kb). pH = -log10[H+].",
    },
    {
        "id": "redox_method",
        "title": "Redox Balancing (Half-Reaction)",
        "source": "Internal Chemistry Notes",
        "content": "Split into oxidation and reduction half-reactions, balance atoms except H/O, balance O with H2O, H with H+, and charge with e-. Equalize electrons and combine.",
    },
    {
        "id": "thermo_signs",
        "title": "Thermo Sign Convention",
        "source": "Internal Chemistry Notes",
        "content": "Exothermic reactions have negative delta H. Endothermic reactions have positive delta H. Spontaneity depends on delta G = delta H - T delta S.",
    },
]


def retrieve_snippets(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    """Simple keyword scoring retrieval; can be swapped with vector DB later."""
    q = query.lower()
    scored = []
    for item in KB_SNIPPETS:
        score = 0
        for token in q.split():
            if token and token in item["content"].lower():
                score += 1
            if token and token in item["title"].lower():
                score += 2
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
