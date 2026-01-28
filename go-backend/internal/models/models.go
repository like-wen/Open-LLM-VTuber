package models

// Message represents a message sent through WebSocket
type Message struct {
	Type    string      `json:"type"`
	Action  string      `json:"action,omitempty"`
	Payload interface{} `json:"payload,omitempty"`
}

// AudioData represents audio data
type AudioData struct {
	Samples []float32 `json:"samples"`
	SampleRate int    `json:"sample_rate"`
	Channels int     `json:"channels"`
}

// Config represents system configuration
type Config struct {
	LLM    LLMConfig    `json:"llm"`
	ASR    ASRConfig    `json:"asr"`
	TTS    TTSConfig    `json:"tts"`
	System SystemConfig `json:"system"`
}

// LLMConfig represents LLM configuration
type LLMConfig struct {
	Provider string `json:"provider"`
	Model    string `json:"model"`
	BaseURL  string `json:"base_url"`
	APIKey   string `json:"api_key"`
}

// ASRConfig represents ASR configuration
type ASRConfig struct {
	Provider string `json:"provider"`
	Model    string `json:"model"`
}

// TTSConfig represents TTS configuration
type TTSConfig struct {
	Provider string `json:"provider"`
	Voice    string `json:"voice"`
}

// SystemConfig represents system-level configuration
type SystemConfig struct {
	MaxConnections int `json:"max_connections"`
	BufferSize     int `json:"buffer_size"`
}

// ChatMessage represents a chat message
type ChatMessage struct {
	ID       string `json:"id"`
	Role     string `json:"role"`     // "user", "assistant", "system"
	Content  string `json:"content"`
	Timestamp int64 `json:"timestamp"`
}

// Session represents a chat session
type Session struct {
	ID        string        `json:"id"`
	Name      string        `json:"name"`
	Messages  []ChatMessage `json:"messages"`
	CreatedAt int64         `json:"created_at"`
	UpdatedAt int64         `json:"updated_at"`
}