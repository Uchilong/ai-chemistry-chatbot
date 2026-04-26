"""Safe calculator evaluator for in-chat math tools."""

from __future__ import annotations

import ast
import math


ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
}

ALLOWED_CONSTS = {
    "pi": math.pi,
    "e": math.e,
}


class _SafeEval(ast.NodeVisitor):
    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Unsupported operator.")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        value = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("Unsupported unary operator.")

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function call.")
        name = node.func.id
        if name not in ALLOWED_FUNCS:
            raise ValueError(f"Function '{name}' is not allowed.")
        args = [self.visit(arg) for arg in node.args]
        return ALLOWED_FUNCS[name](*args)

    def visit_Name(self, node: ast.Name):
        if node.id in ALLOWED_CONSTS:
            return ALLOWED_CONSTS[node.id]
        raise ValueError(f"Unknown symbol '{node.id}'.")

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric constants are allowed.")

    def generic_visit(self, node):
        raise ValueError("Unsupported expression.")


def evaluate_expression(expr: str) -> float:
    """Evaluate arithmetic expression safely."""
    cleaned = expr.strip().replace("^", "**")
    if not cleaned:
        raise ValueError("Expression is empty.")
    tree = ast.parse(cleaned, mode="eval")
    result = _SafeEval().visit(tree)
    if isinstance(result, complex):
        raise ValueError("Complex results are not supported.")
    return float(result)
