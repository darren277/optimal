include .env

#RESOURCE_ID=$(OPTIMIZE_SINGLE_VARIABLE_RESOURCE_ID)
RESOURCE_ID=$(OPTIMIZE_MULTIPLE_VARIABLES_RESOURCE_ID)
METHOD=GET


create-pulp-layer:
	aws lambda publish-layer-version --layer-name pulp_layer --zip-file fileb://pulp_layer.zip

create-pyomo-layer:
	aws lambda publish-layer-version --layer-name pyomo_layer --zip-file fileb://pyomo_layer.zip

create-sympy-layer:
	aws lambda publish-layer-version --layer-name sympy_layer --zip-file fileb://sympy_layer.zip

create-custom-scipy-layer:
	aws lambda publish-layer-version --layer-name custom_scipy_layer --zip-file fileb://custom_scipy_layer.zip


create-usage-plan:
	aws apigateway create-usage-plan --name "OptimalUsagePlan" --description "Usage plan for optimal Chalice app" \
	--api-stages 'apiId=$(REST_API_ID),stage=api' --throttle "burstLimit=100,rateLimit=50" --quota "limit=1000,period=DAY"

create-api-key:
	aws apigateway create-api-key --name "OptimalAPIKey" --description "API key for optimal Chalice app" --enabled

link-key-to-plan:
	aws apigateway create-usage-plan-key --usage-plan-id $(USAGE_PLAN_ID) --key-id $(API_KEY_ID) --key-type "API_KEY"

attach-key-to-endpoint:
	aws apigateway update-method --rest-api-id $(REST_API_ID) --resource-id $(RESOURCE_ID) --http-method $(METHOD) --patch-operations op=replace,path=/apiKeyRequired,value=true


# Then do chalice deploy...

deploy:
	chalice deploy

deploy-alt:
	aws apigateway create-deployment --rest-api-id $(REST_API_ID) --stage-name api


list-resources:
	aws apigateway get-resources --rest-api-id $(REST_API_ID)

