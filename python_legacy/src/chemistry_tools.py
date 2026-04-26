"""Deterministic chemistry helper utilities for safer model responses."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Tuple


ATOMIC_MASS: Dict[str, float] = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078, "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996,
    "Mn": 54.938, "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Br": 79.904, "Ag": 107.8682, "I": 126.90447, "Ba": 137.327, "Au": 196.96657, "Hg": 200.592,
    "Pb": 207.2,
}


def _tokenize_formula(formula: str) -> List[str]:
    return re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)


def parse_formula(formula: str) -> Dict[str, int]:
    """Parse chemical formula into element counts. Supports simple parentheses."""
    tokens = _tokenize_formula(formula.replace(" ", ""))
    if not tokens:
        raise ValueError(f"Invalid formula: {formula}")

    stack: List[defaultdict[str, int]] = [defaultdict(int)]
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "(":
            stack.append(defaultdict(int))
        elif token == ")":
            if len(stack) == 1:
                raise ValueError(f"Unmatched ')' in formula: {formula}")
            group = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1
            for element, count in group.items():
                stack[-1][element] += count * mult
        elif re.match(r"[A-Z][a-z]?", token):
            element = token
            count = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                count = int(tokens[i + 1])
                i += 1
            stack[-1][element] += count
        else:
            raise ValueError(f"Unexpected token '{token}' in formula: {formula}")
        i += 1

    if len(stack) != 1:
        raise ValueError(f"Unmatched '(' in formula: {formula}")
    return dict(stack[0])


def molar_mass(formula: str) -> float:
    counts = parse_formula(formula)
    total = 0.0
    for element, count in counts.items():
        if element not in ATOMIC_MASS:
            raise ValueError(f"Unknown element '{element}' in formula: {formula}")
        total += ATOMIC_MASS[element] * count
    return round(total, 5)


def _parse_side(side: str) -> Dict[str, int]:
    out: Dict[str, int] = defaultdict(int)
    compounds = [c.strip() for c in side.split("+") if c.strip()]
    for part in compounds:
        match = re.match(r"^(\d+)?\s*([A-Za-z0-9()]+)$", part)
        if not match:
            continue
        coeff = int(match.group(1)) if match.group(1) else 1
        formula = match.group(2)
        counts = parse_formula(formula)
        for element, count in counts.items():
            out[element] += coeff * count
    return dict(out)


def check_equation_balance(equation: str) -> Tuple[bool, Dict[str, int], Dict[str, int]]:
    """Check if a simple reaction equation is balanced."""
    normalized = equation.replace("⇌", "->").replace("=", "->").replace("→", "->")
    if "->" not in normalized:
        raise ValueError("Equation must contain an arrow.")
    left, right = normalized.split("->", 1)
    left_counts = _parse_side(left)
    right_counts = _parse_side(right)
    return left_counts == right_counts, left_counts, right_counts


def detect_task_type(user_message: str) -> str:
    text = user_message.lower()
    if any(k in text for k in ["molar mass", "molecular mass", "khối lượng mol"]):
        return "molar_mass"
    if any(k in text for k in ["stoichiometry", "stoichiometric", "mol", "grams", "moles", "hiệu suất", "số mol"]):
        return "stoichiometry"
    if any(k in text for k in ["balance", "balanced", "cân bằng", "reaction", "phản ứng", "->", "→", "⇌"]):
        return "reaction_balance"
    if any(k in text for k in ["mechanism", "sn1", "sn2", "e1", "e2"]):
        return "organic_mechanism"
    if any(k in text for k in ["equilibrium", "acid", "base", "ph", "ka", "kb", "titration"]):
        return "equilibrium_acid_base"
    return "general_chemistry"


def extract_formulas(text: str) -> List[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9()]{0,15}\b", text)
    formulas: List[str] = []
    for token in candidates:
        if re.search(r"[A-Z]", token) and re.search(r"\d|\(|\)|[a-z]", token):
            try:
                parse_formula(token)
                formulas.append(token)
            except Exception:
                continue
    return list(dict.fromkeys(formulas))


def build_solver_hints(user_message: str) -> List[str]:
    """Generate deterministic hints for the model to reduce chemistry mistakes."""
    hints: List[str] = []
    task_type = detect_task_type(user_message)
    hints.append(f"Detected task type: {task_type}.")

    formulas = extract_formulas(user_message)
    if formulas:
        masses = []
        for f in formulas[:3]:
            try:
                masses.append(f"{f} = {molar_mass(f):.3f} g/mol")
            except Exception:
                continue
        if masses:
            hints.append("Reference molar masses: " + "; ".join(masses))

    if any(a in user_message for a in ["->", "→", "⇌", "="]):
        try:
            is_balanced, left_counts, right_counts = check_equation_balance(user_message)
            hints.append(f"Equation balance check: {'balanced' if is_balanced else 'not balanced'}.")
            if not is_balanced:
                hints.append(f"Left counts: {left_counts}; Right counts: {right_counts}")
        except Exception:
            pass

    if any(k in user_message.lower() for k in ["stoichiometry", "mol", "grams", "moles", "khối lượng", "số mol"]):
        hints.append("Stoichiometry reminder: convert all given values to moles first, use balanced coefficients, then convert back to requested units.")

    if any(k in user_message.lower() for k in ["answer", "giải", "solve", "tính"]):
        hints.append("Require units in every numerical step and enforce significant figures in final numeric result.")

    return hints
