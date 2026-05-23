""""""

def try_catch(func):
    """Decorator to catch exceptions and return a standardized error response."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            return {"error": str(e), "success": False}
    return wrapper

def solve_scipy_slsqp(payload):
    import ast
    import operator as op
    import numpy as np
    from scipy.optimize import minimize

    SAFE_FUNCS = {
        "sum": np.sum,
        "dot": np.dot,
    }

    SAFE_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul}

    def _eval_expr(expr: str, local_dict):
        """Safe eval: supports +, -, *, sum(), dot()."""

        def _eval(node):
            if isinstance(node, ast.Num):
                return node.n
            if isinstance(node, ast.Name):
                return local_dict[node.id]
            if isinstance(node, ast.BinOp):
                return SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.Call):
                func = SAFE_FUNCS[node.func.id]
                args = [_eval(a) for a in node.args]
                return func(*args)
            raise TypeError(node)

        return _eval(ast.parse(expr, mode="eval").body)

    p = payload
    params = {k: np.array(v) for k, v in p["parameters"].items()}
    n = len(p["variables"])
    # Decision vector symbol for DSL:
    params["x"] = None  # placeholder

    def f(x):
        params["x"] = x
        return _eval_expr(p["objective"]["expr"], params)

    cons = []
    for c in p["constraints"]:
        if c["type"] == "ineq":
            cons.append({"type": "ineq",
                         "fun": lambda x, expr=c["expr"]: _eval_expr(expr, {**params, "x": x})})
        else:
            cons.append({"type": "eq",
                         "fun": lambda x, expr=c["expr"]: _eval_expr(expr, {**params, "x": x})})

    bounds = [(v["lower"], v["upper"]) for v in p["variables"]]
    x0 = p.get("initial_guess", [1.0]*n)

    try:
        res = minimize(f, x0, method="SLSQP", bounds=bounds, constraints=cons)
        if not res.success:
            raise ValueError(f"Optimization failed: {res.message}")
    except Exception as e:
        print(f"Error during optimization: {e}")
        return {"error": str(e), "success": False}

    return res
