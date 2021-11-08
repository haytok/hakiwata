$(eval USER_ID := $(shell id -u $(USER)))
$(eval GROUP_ID := $(shell id -g $(USER)))

# 開発環境
.PHONY: dev-build
dev-build:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

.PHONY: dev-up
dev-up:
	USER_ID=${USER_ID} GROUP_ID=${GROUP_ID} docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

.PHONY: dev-down
dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# GitHub Actions 内で走る処理
.PHONY: prod-build
prod-build:
	docker-compose build

.PHONY: prod-run
prod-run:
	docker-compose run --rm \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-u $(USER_ID):$(GROUP_ID) \
		ogp_creater

.PHONY: prod-run-on-github-actions
prod-run-on-github-actions:
	docker-compose run --rm \
		ogp_creater
