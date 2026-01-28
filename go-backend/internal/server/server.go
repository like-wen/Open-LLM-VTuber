package server

import (
	"go-open-llm-vtuber/internal/config"
	"go-open-llm-vtuber/internal/handlers"

	"github.com/gin-gonic/gin"
	"github.com/gin-contrib/cors"
)

type Server struct {
	config        *config.Config
	wsHandler     *handlers.WebSocketHandler
	audioHandler  *handlers.AudioHandler
}

func NewServer(config *config.Config) *Server {
	wsHandler := handlers.NewWebSocketHandler(config)
	audioHandler := handlers.NewAudioHandler(config)
	
	return &Server{
		config:       config,
		wsHandler:    wsHandler,
		audioHandler: audioHandler,
	}
}

func (s *Server) SetupRoutes(engine *gin.Engine) {
	// 配置CORS
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"*"}
	engine.Use(cors.New(config))

	// 静态文件服务
	engine.Static("/static", "./static")
	
	// API路由
	api := engine.Group("/api")
	{
		api.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{"status": "ok"})
		})
		
		// WebSocket路由
		ws := api.Group("/ws")
		{
			ws.GET("/client", s.wsHandler.HandleWebSocket)
		}
		
		// 音频处理路由
		audio := api.Group("/audio")
		{
			audio.POST("/process", s.audioHandler.ProcessAudio)
		}
	}
}