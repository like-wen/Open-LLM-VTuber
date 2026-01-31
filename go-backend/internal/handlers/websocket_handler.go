package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"go-open-llm-vtuber/internal/config"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // 允许所有来源，生产环境中应该更严格
	},
}

type WebSocketHandler struct {
	config      *config.Config
	clients     map[*websocket.Conn]bool
	broadcast   chan Message
	register    chan *websocket.Conn
	unregister  chan *websocket.Conn
	mutex       sync.RWMutex
}

type Message struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

func NewWebSocketHandler(config *config.Config) *WebSocketHandler {
	handler := &WebSocketHandler{
		config:    config,
		clients:   make(map[*websocket.Conn]bool),
		broadcast: make(chan Message),
		register:  make(chan *websocket.Conn),
		unregister: make(chan *websocket.Conn),
	}

	go handler.handleClients()

	return handler
}

func (h *WebSocketHandler) HandleWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket升级失败: %v", err)
		return
	}
	defer conn.Close()

	h.register <- conn
	defer func() { h.unregister <- conn }()

	for {
		var msg Message
		err := conn.ReadJSON(&msg)
		if err != nil {
			log.Printf("读取WebSocket消息失败: %v", err)
			break
		}

		// 处理不同类型的消息
		h.handleMessage(conn, msg)
	}
}

func (h *WebSocketHandler) handleMessage(conn *websocket.Conn, msg Message) {
	switch msg.Type {
	case "text-input":
		h.processTextInput(conn, msg.Data)
	case "mic-audio-data":
		h.processAudioData(msg.Data)
	case "fetch-configs":
		h.sendConfigs(conn)
	case "request-init-config":
		h.sendInitConfig(conn)
	default:
		log.Printf("未知消息类型: %s", msg.Type)
	}
}

func (h *WebSocketHandler) processTextInput(conn *websocket.Conn, data interface{}) {
	// 处理文本输入，调用LLM服务
	log.Printf("处理文本输入: %+v", data)
	
	// 这里将数据发送到LLM服务进行处理
	// 模拟响应
	response := Message{
		Type: "llm-response",
		Data: map[string]interface{}{
			"text": "这是模拟的LLM响应",
			"audioUrl": "",
		},
	}
	
	h.sendToClient(conn, response)
}

// 发送初始化配置
func (h *WebSocketHandler) sendInitConfig(conn *websocket.Conn) {
	// 模拟发送初始化配置，包括模型信息
	response := Message{
		Type: "set-model-and-conf",
		Data: map[string]interface{}{
			"model_info": map[string]interface{}{
				"name": "mao_pro",
				"url": "/live2d-models/mao_pro/runtime/mao_pro.model3.json",
				"kScale": 0.5,
				"initialXshift": 0,
				"initialYshift": 0,
				"kXOffset": 1150,
				"idleMotionGroupName": "Idle",
				"emotionMap": map[string]int{
					"neutral": 0,
					"anger": 2,
					"disgust": 2,
					"fear": 1,
					"joy": 3,
					"smirk": 3,
					"sadness": 1,
					"surprise": 3,
				},
				"tapMotions": map[string]interface{}{
					"HitAreaHead": map[string]int{
						"": 1,
					},
					"HitAreaBody": map[string]int{
						"": 1,
					},
				},
			},
			"conf_name": "default",
			"conf_uid": "default-uid",
			"client_uid": "client-uid-placeholder",
		},
	}
	
	h.sendToClient(conn, response)
}



func (h *WebSocketHandler) processAudioData(data interface{}) {
	// 处理音频数据，调用ASR服务
	log.Printf("处理音频数据")
	
	// 这里将音频数据发送到ASR服务进行识别
	// 识别结果再发送到LLM服务
}

func (h *WebSocketHandler) sendConfigs(conn *websocket.Conn) {
	configs := map[string]interface{}{
		"llm": h.config.LLM,
		"asr": h.config.ASR,
		"tts": h.config.TTS,
	}
	
	response := Message{
		Type: "configs",
		Data: configs,
	}
	
	h.sendToClient(conn, response)
}

func (h *WebSocketHandler) sendToClient(conn *websocket.Conn, msg Message) {
	h.mutex.RLock()
	defer h.mutex.RUnlock()
	
	err := conn.WriteJSON(msg)
	if err != nil {
		log.Printf("发送消息到客户端失败: %v", err)
		conn.Close()
	}
}

func (h *WebSocketHandler) handleClients() {
	for {
		select {
		case conn := <-h.register:
			h.mutex.Lock()
			h.clients[conn] = true
			h.mutex.Unlock()
			log.Printf("新客户端连接，当前连接数: %d", len(h.clients))
			
		case conn := <-h.unregister:
			h.mutex.Lock()
			if _, ok := h.clients[conn]; ok {
				delete(h.clients, conn)
				conn.Close()
			}
			h.mutex.Unlock()
			log.Printf("客户端断开连接，当前连接数: %d", len(h.clients))
			
		case message := <-h.broadcast:
			h.mutex.RLock()
			for conn := range h.clients {
				err := conn.WriteJSON(message)
				if err != nil {
					log.Printf("广播消息失败: %v", err)
					delete(h.clients, conn)
					conn.Close()
				}
			}
			h.mutex.RUnlock()
		}
	}
}