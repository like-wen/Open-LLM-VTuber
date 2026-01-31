package config

import (
	"fmt"

	"github.com/spf13/viper"
)

type Config struct {
	Host  string `mapstructure:"host"`
	Port  string `mapstructure:"port"`
	Debug bool   `mapstructure:"debug"`

	LLM    LLMConfig    `mapstructure:"llm"`
	ASR    ASRConfig    `mapstructure:"asr"`
	TTS    TTSConfig    `mapstructure:"tts"`
	VAD    VADConfig    `mapstructure:"vad"`
	System SystemConfig `mapstructure:"system"`
}

type LLMConfig struct {
	Provider string `mapstructure:"provider"`
	Model    string `mapstructure:"model"`
	BaseURL  string `mapstructure:"base_url"`
	APIKey   string `mapstructure:"api_key"`
}

type ASRConfig struct {
	Provider string `mapstructure:"provider"`
	Model    string `mapstructure:"model"`
}

type TTSConfig struct {
	Provider string `mapstructure:"provider"`
	Voice    string `mapstructure:"voice"`
}

type VADConfig struct {
	Provider string `mapstructure:"provider"`
}

type SystemConfig struct {
	MaxConnections int `mapstructure:"max_connections"`
	BufferSize     int `mapstructure:"buffer_size"`
}

func LoadConfig() *Config {
	// 设置配置文件
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./configs")
	viper.AddConfigPath("../configs") // 以防在子目录中运行

	// 设置默认值
	viper.SetDefault("host", "localhost")
	viper.SetDefault("port", "8080")
	viper.SetDefault("debug", false)
	viper.SetDefault("system.max_connections", 1000)
	viper.SetDefault("system.buffer_size", 1024)

	// 尝试读取配置文件（如果存在）
	if err := viper.ReadInConfig(); err != nil {
		fmt.Println("警告: 无法读取配置文件:", err)
		fmt.Println("使用默认配置...")
	}

	// 从环境变量加载（环境变量优先级更高）
	viper.AutomaticEnv()

	var config Config
	err := viper.Unmarshal(&config)
	if err != nil {
		panic(fmt.Errorf("无法解析配置: %w", err))
	}

	return &config
}