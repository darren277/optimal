include .env

#RESOURCE_ID=$(OPTIMIZE_SINGLE_VARIABLE_RESOURCE_ID)
#RESOURCE_ID=$(OPTIMIZE_MULTIPLE_VARIABLES_RESOURCE_ID)
RESOURCE_ID=$(UNCONSTRAINED_OPTIMIZATION_RESOURCE_ID)
METHOD=GET


create-pulp-layer:
	aws lambda publish-layer-version --layer-name pulp_layer --zip-file fileb://pulp_layer.zip

create-pyomo-layer:
	aws lambda publish-layer-version --layer-name pyomo_layer --zip-file fileb://pyomo_layer.zip

create-sympy-layer:
	aws lambda publish-layer-version --layer-name sympy_layer --zip-file fileb://sympy_layer.zip

create-custom-scipy-layer:
	aws lambda publish-layer-version --layer-name custom_scipy_layer --zip-file fileb://custom_scipy_layer.zip

create-openai-layer:
	aws lambda publish-layer-version --layer-name openai_layer --zip-file fileb://openai_layer.zip


create-usage-plan:
	aws apigateway create-usage-plan --name "OptimalUsagePlan" --description "Usage plan for optimal Chalice app" \
	--api-stages 'apiId=$(REST_API_ID),stage=api' --throttle "burstLimit=100,rateLimit=50" --quota "limit=1000,period=DAY"

create-api-key:
	aws apigateway create-api-key --name "OptimalAPIKey" --description "API key for optimal Chalice app" --enabled

link-key-to-plan:
	aws apigateway create-usage-plan-key --usage-plan-id $(USAGE_PLAN_ID) --key-id $(API_KEY_ID) --key-type "API_KEY"

# Run this one for each endpoint (resource):
attach-key-to-endpoint:
	aws apigateway update-method --rest-api-id $(REST_API_ID) --resource-id $(RESOURCE_ID) --http-method $(METHOD) --patch-operations op=replace,path=/apiKeyRequired,value=true


# Then do chalice deploy...

deploy:
	chalice deploy

deploy-alt:
	aws apigateway create-deployment --rest-api-id $(REST_API_ID) --stage-name api


list-resources:
	aws apigateway get-resources --rest-api-id $(REST_API_ID)



SECRET_SUFFIX=5kW6yx
#SECRET_SUFFIX=*

SECRET_ARN=arn:aws:secretsmanager:$(AWS_REGION):$(AWS_ACCOUNT_ID):secret:OPTIMAL_OPENAI_API_KEY-$(SECRET_SUFFIX)

SECRETS_STATEMENT={"Effect": "Allow", "Action": "secretsmanager:GetSecretValue", "Resource": "$(SECRET_ARN)"}
LOG_STATEMENT={"Effect": "Allow", "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], "Resource": "arn:aws:logs:$(AWS_REGION):$(AWS_ACCOUNT_ID):*"}
POLICY='{"Version": "2012-10-17", "Statement": [$(SECRETS_STATEMENT), $(LOG_STATEMENT)]}'


update-llm-role:
	aws iam put-role-policy --role-name optimal-dev-llm_endpoint_func --policy-name optimal-dev-llm_endpoint_func --policy-document $(POLICY)

attach-role-to-func:
	aws lambda update-function-configuration --function-name optimal-dev-llm_endpoint_func --role arn:aws:iam::160751179089:role/optimal-dev-llm_endpoint_func


REPOSITORY_URI=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPOSITORY_NAME)
DWAVE_FUNC_NAME=optimal-dev-test_loading_dwave_func
PYOMO_FUNC_NAME=optimal-dev-test_loading_pyomo_func

# SWITCH BETWEEN THESE AS NEEDED:
#DOCKERIZED_FUNC_NAME=$(DWAVE_FUNC_NAME)
DOCKERIZED_FUNC_NAME=$(PYOMO_FUNC_NAME)

# SWITCH BETWEEN THESE AS NEEDED:
#DOCKER_IMAGE_NAME=dwave_funcs:test
DOCKER_IMAGE_NAME=pyomo_funcs:test

# SWITCH BETWEEN THESE AS NEEDED:
#DOCKERFILE=Dockerfile.dwave
DOCKERFILE=Dockerfile.pyomo

ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

ecr-create:
	aws ecr create-repository --repository-name $(ECR_REPOSITORY_NAME) --region $(AWS_REGION) --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

docker-build:
	docker build --platform linux/amd64 -t $(DOCKER_IMAGE_NAME) --file $(DOCKERFILE) .

docker-deploy:
	docker tag $(DOCKER_IMAGE_NAME) $(REPOSITORY_URI):latest
	docker push $(REPOSITORY_URI):latest


TRUST_POLICY='{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'

create-role:
	aws iam create-role --role-name lambda-ex --assume-role-policy-document $(TRUST_POLICY)

create-func:
	aws lambda create-function --function-name $(DOCKERIZED_FUNC_NAME) --package-type Image --code ImageUri=$(REPOSITORY_URI):latest --role arn:aws:iam::$(AWS_ACCOUNT_ID):role/lambda-ex

update-func:
	aws lambda update-function-code --function-name $(DOCKERIZED_FUNC_NAME) --image-uri $(REPOSITORY_URI):latest --publish

update-func-config:
	aws lambda update-function-configuration --function-name $(DOCKERIZED_FUNC_NAME) --timeout 120 --memory-size 512

