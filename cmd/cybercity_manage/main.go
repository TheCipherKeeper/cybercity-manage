package main

import controlplane "github.com/TheCipherKeeper/cybercity-manage/internal/control_plane/adapters/inbound"

func main() {
	controlplane.NewServer().Start()
}
