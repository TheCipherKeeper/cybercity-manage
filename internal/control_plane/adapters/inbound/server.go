package inbound

import (
	"log"
	"net/http"
	"os"
)

// Server сохраняет существующую временную HTTP-точку контрольной плоскости.
type Server struct {
	addr string
}

// NewServer читает адрес из существующего конфигурационного контракта.
func NewServer() *Server {
	addr := os.Getenv("MANAGE_HTTP_ADDR")
	if addr == "" {
		addr = ":8081"
	}
	return &Server{addr: addr}
}

// Start запускает прежнее поведение: любой маршрут отвечает 501.
func (server *Server) Start() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(writer http.ResponseWriter, _ *http.Request) {
		writer.Header().Set("Content-Type", "text/plain; charset=utf-8")
		writer.WriteHeader(http.StatusNotImplemented)
		_, _ = writer.Write([]byte("manage stub — not implemented\n"))
	})
	log.Printf("manage stub — not implemented; listening on %s (control API placeholder)", server.addr)
	if err := http.ListenAndServe(server.addr, mux); err != nil {
		log.Fatalf("manage stub: HTTP server error: %v", err)
	}
}
