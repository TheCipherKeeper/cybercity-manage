// Command cybercity-manage — STUB / PLACEHOLDER точки входа контрольной
// плоскости.
//
// TODO: реальная контрольная плоскость (provisioning/reset/изоляция/квоты,
// control API к engine, публикация infra/control-событий в Redpanda,
// generic consumption overlays-артефакта) — по docs/BACKLOG.md и
// docs/specs/control-plane.md. Сейчас main.go существует лишь для
// собираемости Dockerfile: поднимает HTTP-точку на MANAGE_HTTP_ADDR, логирует
// "manage stub — not implemented" и возвращает 501 на все маршруты.
//
// Не выдавать эту заглушку за реализацию.
package main

import (
	"log"
	"net/http"
	"os"
)

func main() {
	addr := os.Getenv("MANAGE_HTTP_ADDR")
	if addr == "" {
		addr = ":8081"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.WriteHeader(http.StatusNotImplemented)
		_, _ = w.Write([]byte("manage stub — not implemented\n"))
	})

	log.Printf("manage stub — not implemented; listening on %s (control API placeholder)", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("manage stub: HTTP server error: %v", err)
	}
}