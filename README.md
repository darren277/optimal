# Optimal – Optimisation‑as‑a‑Service

Optimal lets you submit plain‑English or JSON‑defined optimisation problems and returns optimal solutions using open‑source solvers (SymPy, PuLP, Pyomo, SciPy) or quantum‑annealing back‑ends (D‑Wave).

## Quick demo

```bash
# Classify & structure a problem
curl -G "$(chalice url)/llm_endpoint" \
     --data-urlencode "problem_description=Minimise cost subject to demand ≥ 100"
# → { "description": "...", "classification": "Linear programming" }

# Solve a toy unconstrained revenue function
curl -G "$(chalice url)/unconstrained_optimization" -d a=150 -d b=3
# → { "p_star":25, "R_star":3750 }
```

## About

URL: https://iknaxd5pj9.execute-api.us-east-1.amazonaws.com/api/.

URL: http://optimal.apphosting.services.

### Problem Spec

```json
{
  "id": "uuid",
  "kind": "quadratic_programming",
  "objective": { "sense":"max", "expr": "3x + 4y - z^2" },
  "vars": { "x": {"type":"real"}, "y":{"type":"integer"}, "z":{"type":"real"} },
  "constraints": [ "x + y <= 10", "z >= 0" ]
}
```

## How to Use

### Immediate Usage

```shell
python -m venv .venv && source .venv/bin/activate
pip install chalice
export AWS_PROFILE=your‑profile
export QUEUE_NAME=optimal‑jobs‑dev
chalice deploy --stage dev
```

### Chalice

1. `. venv/Scripts/activate`.
2. `chalice deploy`.

Also: `chalice logs`.

### Layers

1. Managed layer: `optimal-dev-managed-layer: arn:aws:lambda:us-east-1:<AWS_ACCOUNT_NUMBER>:layer:optimal-dev-managed-layer:15`.
2. Sympy layer: `optimal-sympy-layer: arn:aws:lambda:us-east-1:<AWS_ACCOUNT_NUMBER>:layer:optimal-sympy-layer:1`.


1. `pip3 install --target=C:\Users\Darren\PycharmProjects\Miniprojects\optimal\sympylayer\venv -r layer2-requirements.txt`. 
2. `pip3 install --target=C:\Users\Darren\PycharmProjects\Miniprojects\optimal\scipylayer\venv -r layer3-requirements.txt`.


Add to `.chalice/config.json`:
```json
{
  "layers": [
    "arn:aws:lambda:us-east-1:160751179089:layer:pulp_layer:1",
    "arn:aws:lambda:us-east-1:160751179089:layer:pyomo_layer:1",
    "arn:aws:lambda:us-east-1:160751179089:layer:sympy_layer:1"
  ]
}
```

Remember to structure the inside of your zip files correctly:
* pyomo_layer.zip:python\lib\python3.12\site-packages
* sympy_layer.zip:python\lib\python3.12\site-packages
* pulp_layer.zip:python\lib\python3.12\site-packages

Current load times:
```shell
{'pyomo_version': '6.8.2', 'success': 'SUCCESSFULLY LOADED PYOMO', 'loading_time': 4.124641418457031e-05}
Test took 0.2777373790740967 seconds
{'pulp_version': '2.9.0', 'success': 'SUCCESSFULLY LOADED PULP', 'loading_time': 0.46628499031066895}
Test took 0.7224259376525879 seconds
{'sympy_version': '1.13.3', 'success': 'SUCCESSFULLY LOADED SYMPY', 'loading_time': 10.816535711288452}
Test took 11.0744309425354 seconds
{'scipy_version': '1.14.1', 'success': 'SUCCESSFULLY LOADED SCIPY', 'loading_time': 3.814697265625e-05}
Test took 0.46985483169555664 seconds
```

## POSTMAN

After importing the file `optimal.postman_collection.json`, be sure to swap every case of `___REPLACE_WITH_API_KEY___` with the API Gateway key (`API_KEY` in `.env`).
