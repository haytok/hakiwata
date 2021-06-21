VERSION=0.83.1

.PHONY: server
server:
	docker run --rm -it \
		-v $(PWD):/src \
		-p 1313:1313 \
		klakegg/hugo:$(VERSION) server

.PHONY: new
new:
	@echo "New file name is $(F)"

	$(eval USER_ID := $(shell id -u $(USER)))
	$(eval GROUP_ID := $(shell id -g $(USER)))

	docker run --rm -it \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-v $(PWD):/src \
		-u $(USER_ID):$(GROUP_ID) \
		klakegg/hugo:$(VERSION) new "content/post/$(F)"

.PHONY: build
build:
	docker run --rm -it \
		-v $(PWD):/src \
		klakegg/hugo:$(VERSION)
