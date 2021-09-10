VERSION=0.83.1
PORT=1313

OLD_VERSION=0.65.3

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
