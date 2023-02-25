# OLD_VERSION=0.65.3
# OLD_VERSION=0.83.1
VERSION=0.101.0
# VERSION=0.110.0 # not released Docker image
PORT=1313

$(eval USER_ID := $(shell id -u $(USER)))
$(eval GROUP_ID := $(shell id -g $(USER)))

.PHONY: server
server:
	docker run --rm -it \
		-v $(PWD):/src \
		-p $(PORT):1313 \
		klakegg/hugo:$(VERSION) server

.PHONY: new
new:
	@echo "Directory name is $(D)"

	mkdir -p content/post/$(D)

	docker run --rm -it \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-v $(PWD):/src \
		-u $(USER_ID):$(GROUP_ID) \
		klakegg/hugo:$(VERSION) new "content/post/$(D)/index.md"

	code "content/post/$(D)/index.md";

.PHONY: scraps
scraps:
	@echo "Directory name is $(D)"

	mkdir -p content/scraps/$(D)

	docker run --rm -it \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-v $(PWD):/src \
		-u $(USER_ID):$(GROUP_ID) \
		klakegg/hugo:$(VERSION) new "content/scraps/$(D)/index.md"

	code "content/scraps/$(D)/index.md";

.PHONY: log
log:
	@echo "Directory name is $(D)"

	mkdir -p content/log/$(D)

	docker run --rm -it \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-v $(PWD):/src \
		-u $(USER_ID):$(GROUP_ID) \
		klakegg/hugo:$(VERSION) new "content/log/$(D)/index.md"

	code "content/log/$(D)/index.md";

.PHONY: build
build:
	docker run --rm -it \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-v $(PWD):/src \
		-u $(USER_ID):$(GROUP_ID) \
		klakegg/hugo:$(VERSION) build
