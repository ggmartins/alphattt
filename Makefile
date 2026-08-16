IMAGE ?= my-app:v0
DEPLOYMENT ?= my-app

.PHONY: all build load-image rollout

all: build load-image rollout

build:
	docker build -t $(IMAGE) tttapi

load-image:
	@set -e; \
	for node in $$(docker ps --format '{{.Names}}' | grep '^desktop-'); do \
		echo "Loading image into $$node"; \
		docker save $(IMAGE) | docker exec -i "$$node" ctr -n k8s.io images import -; \
	done

rollout:
	kubectl rollout restart deployment/$(DEPLOYMENT)
	kubectl rollout status deployment/$(DEPLOYMENT)
