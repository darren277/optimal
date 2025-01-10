# Optimal (WIP)

## About

## How to Use

### Chalice

1. `. venv/Scripts/activate`.
2. `chalice deploy`.

### Layers

1. Managed layer: `optimal-dev-managed-layer: arn:aws:lambda:us-east-1:<AWS_ACCOUNT_NUMBER>:layer:optimal-dev-managed-layer:15`.
2. Sympy layer: `optimal-sympy-layer: arn:aws:lambda:us-east-1:<AWS_ACCOUNT_NUMBER>:layer:optimal-sympy-layer:1`.


1. `pip3 install --target=C:\Users\Darren\PycharmProjects\Miniprojects\optimal\sympylayer\venv -r layer2-requirements.txt`. 
2. `pip3 install --target=C:\Users\Darren\PycharmProjects\Miniprojects\optimal\scipylayer\venv -r layer3-requirements.txt`.
