# Dockerfile сервиса cybercity-manage (Go). Мультистадийная сборка:
# stage build → тонкий runtime-образ, не от root. Детали —
# https://github.com/TheCipherKeeper/ai-project-template/docs/refs/DEPLOYMENT.md

# ---- stage: build ----
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod ./
# go.sum коммитится (lock-файл); копируем если есть
COPY go.sum* ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 go build -o /out/cybercity-manage ./cmd/cybercity_manage

# ---- stage: runtime ----
FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /app
COPY --from=build /out/cybercity-manage /app/cybercity-manage
USER nonroot:nonroot
EXPOSE 8081
CMD ["/app/cybercity-manage"]
