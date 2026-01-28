package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"go-open-llm-vtuber/internal/config"
	"go-open-llm-vtuber/internal/server"
)

func main() {
	// 加载配置
	cfg := config.LoadConfig()

	// 设置日志模式
	if cfg.Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建 Gin 引擎
	r := gin.Default()

	// 初始化服务器
	srv := server.NewServer(cfg)
	srv.SetupRoutes(r)

	// 启动服务器
	log.Printf("服务器启动在 %s:%d", cfg.Host, cfg.Port)
	log.Fatal(http.ListenAndServe(cfg.Host+":"+cfg.Port, r))
}