RPM_PATH = "iguazio_yum"
BINARY_NAME = "igz-fuse"
VERSION = $(IGUAZIO_VERSION)

.PHONY: build
build:
	docker build --tag flex-fuse:unstable .

.PHONY: download
download:
	@rm -rf hack/libs/${BINARY_NAME}*
	@cd hack/libs && wget --quiet $(MIRROR)/$(RPM_PATH)/$(IGUAZIO_VERSION)/$(BINARY_NAME).rpm
	@touch hack/libs/$(IGUAZIO_VERSION)

.PHONY: release
release: check-req download build
	docker tag flex-fuse:unstable flex-fuse:$(VERSION)

.PHONY: lint
lint: ensure-gopath
	@echo Installing linters...
	go get -u gopkg.in/alecthomas/gometalinter.v2
	@$(GOPATH)/bin/gometalinter.v2 --install

	@echo Linting...
	@$(GOPATH)/bin/gometalinter.v2 \
		--deadline=300s \
		--disable-all \
		--enable-gc \
		--enable=deadcode \
		--enable=goconst \
		--enable=gofmt \
		--enable=golint \
		--enable=gosimple \
		--enable=ineffassign \
		--enable=interfacer \
		--enable=misspell \
		--enable=staticcheck \
		--enable=unconvert \
		--enable=varcheck \
		--enable=vet \
		--enable=vetshadow \
		--enable=errcheck \
		--exclude="_test.go" \
		--exclude="comment on" \
		--exclude="error should be the last" \
		--exclude="should have comment" \
		./cmd/... ./pkg/...

	@echo Done.

.PHONY: vet
vet:
	go vet ./cmd/...
	go vet ./pkg/...

.PHONY: test
test:
	go test -v ./cmd/...
	go test -v ./pkg/...


check-req:
ifndef MIRROR
	$(error MIRROR must be set)
endif
ifndef IGUAZIO_VERSION
	$(error IGUAZIO_VERSION must be set)
endif

ensure-gopath:
ifndef GOPATH
	$(error GOPATH must be set)
endif
