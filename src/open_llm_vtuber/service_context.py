import os
import json
from typing import Callable
from loguru import logger
from fastapi import WebSocket

from prompts import prompt_loader
from .live2d_model import Live2dModel
from .asr.asr_interface import ASRInterface
from .tts.tts_interface import TTSInterface
from .vad.vad_interface import VADInterface
from .agent.agents.agent_interface import AgentInterface
from .translate.translate_interface import TranslateInterface

from .mcpp.server_registry import ServerRegistry
from .mcpp.tool_manager import ToolManager
from .mcpp.mcp_client import MCPClient
from .mcpp.tool_executor import ToolExecutor
from .mcpp.tool_adapter import ToolAdapter

from .asr.asr_factory import ASRFactory
from .tts.tts_factory import TTSFactory
from .vad.vad_factory import VADFactory
from .agent.agent_factory import AgentFactory
from .translate.translate_factory import TranslateFactory

from .config_manager import (
    Config,
    AgentConfig,
    CharacterConfig,
    SystemConfig,
    ASRConfig,
    TTSConfig,
    VADConfig,
    TranslatorConfig,
    read_yaml,
    validate_config,
)


class ServiceContext:
    """初始化、存储和更新 ASR、TTS 和 LLM 实例以及其他
    为连接客户端配置的参数。"""

    def __init__(self):
        self.config: Config = None
        self.system_config: SystemConfig = None
        self.character_config: CharacterConfig = None

        self.live2d_model: Live2dModel = None
        self.asr_engine: ASRInterface = None
        self.tts_engine: TTSInterface = None
        self.agent_engine: AgentInterface = None
        # 如果禁用翻译，translate_engine 可以为 None
        self.vad_engine: VADInterface | None = None
        self.translate_engine: TranslateInterface | None = None

        self.mcp_server_registery: ServerRegistry | None = None
        self.tool_adapter: ToolAdapter | None = None
        self.tool_manager: ToolManager | None = None
        self.mcp_client: MCPClient | None = None
        self.tool_executor: ToolExecutor | None = None

        # 系统提示是角色提示和 Live2D 表情提示的组合
        self.system_prompt: str = None

        # 存储生成的 MCP 提示字符串（如果启用了 MCP）
        self.mcp_prompt: str = ""

        self.history_uid: str = ""  # 添加 history_uid 字段

        self.send_text: Callable = None
        self.client_uid: str = None

    def __str__(self):
        return (
            f"ServiceContext:\n"
            f"  系统配置: {'已加载' if self.system_config else '未加载'}\n"
            f"    详情: {json.dumps(self.system_config.model_dump(), indent=6) if self.system_config else '无'}\n"
            f"  Live2D 模型: {self.live2d_model.model_info if self.live2d_model else '未加载'}\n"
            f"  ASR 引擎: {type(self.asr_engine).__name__ if self.asr_engine else '未加载'}\n"
            f"    配置: {json.dumps(self.character_config.asr_config.model_dump(), indent=6) if self.character_config.asr_config else '无'}\n"
            f"  TTS 引擎: {type(self.tts_engine).__name__ if self.tts_engine else '未加载'}\n"
            f"    配置: {json.dumps(self.character_config.tts_config.model_dump(), indent=6) if self.character_config.tts_config else '无'}\n"
            f"  LLM 引擎: {type(self.agent_engine).__name__ if self.agent_engine else '未加载'}\n"
            f"    代理配置: {json.dumps(self.character_config.agent_config.model_dump(), indent=6) if self.character_config.agent_config else '无'}\n"
            f"  VAD 引擎: {type(self.vad_engine).__name__ if self.vad_engine else '未加载'}\n"
            f"    代理配置: {json.dumps(self.character_config.vad_config.model_dump(), indent=6) if self.character_config.vad_config else '无'}\n"
            f"  系统提示: {self.system_prompt or '未设置'}\n"
            f"  MCP 已启用: {'是' if self.mcp_client else '否'}"
        )

    # ==== Initializers

    async def _init_mcp_components(self, use_mcpp, enabled_servers):
        """根据配置初始化 MCP 组件，动态获取工具信息。"""
        logger.debug(
            f"初始化 MCP 组件: use_mcpp={use_mcpp}, enabled_servers={enabled_servers}"
        )

        # 首先重置 MCP 组件
        self.mcp_server_registery = None
        self.tool_manager = None
        self.mcp_client = None
        self.tool_executor = None
        self.json_detector = None
        self.mcp_prompt = ""

        if use_mcpp and enabled_servers:
            # 1. 初始化 ServerRegistry
            self.mcp_server_registery = ServerRegistry()
            logger.info("ServerRegistry 已初始化或引用。")

            # 2. 使用 ToolAdapter 获取 MCP 提示和工具
            if not self.tool_adapter:
                logger.error(
                    "调用 _init_mcp_components 前未初始化 ToolAdapter。"
                )
                self.mcp_prompt = "[错误: ToolAdapter 未初始化]"
                return  # 如果 ToolAdapter 是必需的且未初始化，则退出

            try:
                (
                    mcp_prompt_string,
                    openai_tools,
                    claude_tools,
                ) = await self.tool_adapter.get_tools(enabled_servers)
                # 存储生成的提示字符串
                self.mcp_prompt = mcp_prompt_string
                logger.info(
                    f"动态生成的 MCP 提示字符串 (长度: {len(self.mcp_prompt)})。"
                )
                logger.info(
                    f"动态格式化的工具 - OpenAI: {len(openai_tools)}, Claude: {len(claude_tools)}。"
                )

                # 3. 使用获取的格式化工具初始化 ToolManager

                _, raw_tools_dict = await self.tool_adapter.get_server_and_tool_info(
                    enabled_servers
                )
                self.tool_manager = ToolManager(
                    formatted_tools_openai=openai_tools,
                    formatted_tools_claude=claude_tools,
                    initial_tools_dict=raw_tools_dict,
                )
                logger.info("ToolManager 已使用动态获取的工具初始化。")

            except Exception as e:
                logger.error(
                    f"动态 MCP 工具构建失败: {e}", exc_info=True
                )
                # 确保如果构建失败，不会创建依赖组件
                self.tool_manager = None
                self.mcp_prompt = "[构建 MCP 工具/提示时出错]"

            # 4. 初始化 MCPClient
            if self.mcp_server_registery:
                self.mcp_client = MCPClient(
                    self.mcp_server_registery, self.send_text, self.client_uid
                )
                logger.info("此会话的 MCPClient 已初始化。")
            else:
                logger.error(
                    "MCP 已启用但 ServerRegistry 不可用。未创建 MCPClient。"
                )
                self.mcp_client = None  # 确保为 None

            # 5. 初始化 ToolExecutor
            if self.mcp_client and self.tool_manager:
                self.tool_executor = ToolExecutor(self.mcp_client, self.tool_manager)
                logger.info("此会话的 ToolExecutor 已初始化。")
            else:
                logger.warning(
                    "MCPClient 或 ToolManager 不可用。未创建 ToolExecutor。"
                )
                self.tool_executor = None  # 确保为 None

            logger.info("此会话的 StreamJSONDetector 已初始化。")

        elif use_mcpp and not enabled_servers:
            logger.warning(
                "use_mcpp 为 True，但 mcp_enabled_servers 列表为空。未初始化 MCP 组件。"
            )
        else:
            logger.debug(
                "MCP 组件未初始化 (use_mcpp 为 False 或无启用的服务器)。"
            )

    async def close(self):
        """清理资源，尤其是 MCPClient。"""
        logger.info("关闭 ServiceContext 资源...")
        if self.mcp_client:
            logger.info(f"关闭上下文实例 {id(self)} 的 MCPClient...")
            await self.mcp_client.aclose()
            self.mcp_client = None
        if self.agent_engine and hasattr(self.agent_engine, "close"):
            await self.agent_engine.close()  # 确保代理资源也被关闭
        logger.info("ServiceContext 已关闭。")

    async def load_cache(
        self,
        config: Config,
        system_config: SystemConfig,
        character_config: CharacterConfig,
        live2d_model: Live2dModel,
        asr_engine: ASRInterface,
        tts_engine: TTSInterface,
        vad_engine: VADInterface,
        agent_engine: AgentInterface,
        translate_engine: TranslateInterface | None,
        mcp_server_registery: ServerRegistry | None = None,
        tool_adapter: ToolAdapter | None = None,
        send_text: Callable = None,
        client_uid: str = None,
    ) -> None:
        """
        使用提供实例的引用加载 ServiceContext。
        通过引用传递，因此不会重新初始化。
        """
        if not character_config:
            raise ValueError("character_config 不能为空")
        if not system_config:
            raise ValueError("system_config 不能为空")

        self.config = config
        self.system_config = system_config
        self.character_config = character_config
        self.live2d_model = live2d_model
        self.asr_engine = asr_engine
        self.tts_engine = tts_engine
        self.vad_engine = vad_engine
        self.agent_engine = agent_engine
        self.translate_engine = translate_engine
        # 通过引用加载可能共享的组件
        self.mcp_server_registery = mcp_server_registery
        self.tool_adapter = tool_adapter
        self.send_text = send_text
        self.client_uid = client_uid

        # 初始化会话特定的 MCP 组件
        await self._init_mcp_components(
            self.character_config.agent_config.agent_settings.basic_memory_agent.use_mcpp,
            self.character_config.agent_config.agent_settings.basic_memory_agent.mcp_enabled_servers,
        )

        logger.debug(f"已使用缓存加载服务上下文: {character_config}")

    async def load_from_config(self, config: Config) -> None:
        """
        使用配置加载 ServiceContext。
        如果配置不同，则重新初始化实例。

        参数:
        - config (Config): 配置对象。
        """
        if not self.config:
            self.config = config

        if not self.system_config:
            self.system_config = config.system_config

        if not self.character_config:
            self.character_config = config.character_config

        # 更新所有子配置

        # 从角色配置初始化 live2d
        self.init_live2d(config.character_config.live2d_model_name)

        # 从角色配置初始化 asr
        self.init_asr(config.character_config.asr_config)

        # 从角色配置初始化 tts
        self.init_tts(config.character_config.tts_config)

        # 从角色配置初始化 vad
        self.init_vad(config.character_config.vad_config)

        # 如果共享 ToolAdapter 尚未存在，则初始化
        if (
            not self.tool_adapter
            and config.character_config.agent_config.agent_settings.basic_memory_agent.use_mcpp
        ):
            if not self.mcp_server_registery:
                logger.info(
                    "在 load_from_config 中初始化共享 ServerRegistry。"
                )
                self.mcp_server_registery = ServerRegistry()
            logger.info("在 load_from_config 中初始化共享 ToolAdapter。")
            self.tool_adapter = ToolAdapter(server_registery=self.mcp_server_registery)

        # 在初始化 Agent 之前初始化 MCP 组件
        await self._init_mcp_components(
            config.character_config.agent_config.agent_settings.basic_memory_agent.use_mcpp,
            config.character_config.agent_config.agent_settings.basic_memory_agent.mcp_enabled_servers,
        )

        # 从角色配置初始化 agent
        await self.init_agent(
            config.character_config.agent_config,
            config.character_config.persona_prompt,
        )

        self.init_translate(
            config.character_config.tts_preprocessor_config.translator_config
        )

        # 存储类型化的配置引用
        self.config = config
        self.system_config = config.system_config or self.system_config
        self.character_config = config.character_config

    def init_live2d(self, live2d_model_name: str) -> None:
        logger.info(f"初始化 Live2D: {live2d_model_name}")
        try:
            self.live2d_model = Live2dModel(live2d_model_name)
            self.character_config.live2d_model_name = live2d_model_name
        except Exception as e:
            logger.critical(f"初始化 Live2D 时出错: {e}")
            logger.critical("尝试在没有 Live2D 的情况下继续...")

    def init_asr(self, asr_config: ASRConfig) -> None:
        if not self.asr_engine or (self.character_config.asr_config != asr_config):
            logger.info(f"初始化 ASR: {asr_config.asr_model}")
            self.asr_engine = ASRFactory.get_asr_system(
                asr_config.asr_model,
                **getattr(asr_config, asr_config.asr_model).model_dump(),
            )
            # 成功初始化后保存配置
            self.character_config.asr_config = asr_config
        else:
            logger.info("ASR 已使用相同配置初始化。")

    def init_tts(self, tts_config: TTSConfig) -> None:
        if not self.tts_engine or (self.character_config.tts_config != tts_config):
            logger.info(f"初始化 TTS: {tts_config.tts_model}")
            self.tts_engine = TTSFactory.get_tts_engine(
                tts_config.tts_model,
                **getattr(tts_config, tts_config.tts_model.lower()).model_dump(),
            )
            # 成功初始化后保存配置
            self.character_config.tts_config = tts_config
        else:
            logger.info("TTS 已使用相同配置初始化。")

    def init_vad(self, vad_config: VADConfig) -> None:
        if vad_config.vad_model is None:
            logger.info("VAD 已禁用。")
            self.vad_engine = None
            return

        if not self.vad_engine or (self.character_config.vad_config != vad_config):
            logger.info(f"初始化 VAD: {vad_config.vad_model}")
            self.vad_engine = VADFactory.get_vad_engine(
                vad_config.vad_model,
                **getattr(vad_config, vad_config.vad_model.lower()).model_dump(),
            )
            # 成功初始化后保存配置
            self.character_config.vad_config = vad_config
        else:
            logger.info("VAD 已使用相同配置初始化。")

    async def init_agent(self, agent_config: AgentConfig, persona_prompt: str) -> None:
        """根据代理配置初始化或更新 LLM 引擎。"""
        logger.info(f"初始化代理: {agent_config.conversation_agent_choice}")

        if (
            self.agent_engine is not None
            and agent_config == self.character_config.agent_config
            and persona_prompt == self.character_config.persona_prompt
        ):
            logger.debug("代理已使用相同配置初始化。")
            return

        system_prompt = await self.construct_system_prompt(persona_prompt)

        # 将头像传递给代理工厂
        avatar = self.character_config.avatar or ""  # 从配置中获取头像

        try:
            self.agent_engine = AgentFactory.create_agent(
                conversation_agent_choice=agent_config.conversation_agent_choice,
                agent_settings=agent_config.agent_settings.model_dump(),
                llm_configs=agent_config.llm_configs.model_dump(),
                system_prompt=system_prompt,
                live2d_model=self.live2d_model,
                tts_preprocessor_config=self.character_config.tts_preprocessor_config,
                character_avatar=avatar,
                system_config=self.system_config.model_dump(),
                tool_manager=self.tool_manager,
                tool_executor=self.tool_executor,
                mcp_prompt_string=self.mcp_prompt,
            )

            logger.debug(f"代理选择: {agent_config.conversation_agent_choice}")
            logger.debug(f"系统提示: {system_prompt}")

            # 保存当前配置
            self.character_config.agent_config = agent_config
            self.system_prompt = system_prompt

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    def init_translate(self, translator_config: TranslatorConfig) -> None:
        """根据配置初始化或更新翻译引擎。"""

        if not translator_config.translate_audio:
            logger.debug("翻译已禁用。")
            return

        if (
            not self.translate_engine
            or self.character_config.tts_preprocessor_config.translator_config
            != translator_config
        ):
            logger.info(
                f"初始化翻译器: {translator_config.translate_provider}"
            )
            self.translate_engine = TranslateFactory.get_translator(
                translator_config.translate_provider,
                getattr(
                    translator_config, translator_config.translate_provider
                ).model_dump(),
            )
            self.character_config.tts_preprocessor_config.translator_config = (
                translator_config
            )
        else:
            logger.info("翻译已使用相同配置初始化。")

    # ==== utils

    async def construct_system_prompt(self, persona_prompt: str) -> str:
        """
        将工具提示追加到角色提示中。

        参数:
        - persona_prompt (str): 角色提示。

        返回:
        - str: 包含所有工具提示的系统提示。
        """
        logger.debug(f"构建角色提示: '''{persona_prompt}'''")

        for prompt_name, prompt_file in self.system_config.tool_prompts.items():
            if (
                prompt_name == "group_conversation_prompt"
                or prompt_name == "proactive_speak_prompt"
            ):
                continue

            prompt_content = prompt_loader.load_util(prompt_file)

            if prompt_name == "live2d_expression_prompt":
                prompt_content = prompt_content.replace(
                    "[<insert_emomap_keys>]", self.live2d_model.emo_str
                )

            if prompt_name == "mcp_prompt":
                continue

            persona_prompt += prompt_content

        logger.debug("\n === 系统提示 ===")
        logger.debug(persona_prompt)

        return persona_prompt

    async def handle_config_switch(
        self,
        websocket: WebSocket,
        config_file_name: str,
    ) -> None:
        """
        处理配置切换请求。
        将配置更改为新配置并通知客户端。

        参数:
        - websocket (WebSocket): WebSocket 连接。
        - config_file_name (str): 配置文件的名称。
        """
        try:
            new_character_config_data = None

            if config_file_name == "conf.yaml":
                # 加载基础配置
                new_character_config_data = read_yaml("conf.yaml").get(
                    "character_config"
                )
            else:
                # 加载替代配置并与基础配置合并
                characters_dir = self.system_config.config_alts_dir
                file_path = os.path.normpath(
                    os.path.join(characters_dir, config_file_name)
                )
                if not file_path.startswith(characters_dir):
                    raise ValueError("Invalid configuration file path")

                alt_config_data = read_yaml(file_path).get("character_config")

                # Start with original config data and perform a deep merge
                new_character_config_data = deep_merge(
                    self.config.character_config.model_dump(), alt_config_data
                )

            if new_character_config_data:
                new_config = {
                    "system_config": self.system_config.model_dump(),
                    "character_config": new_character_config_data,
                }
                new_config = validate_config(new_config)
                await self.load_from_config(new_config)  # 等待异步加载
                logger.debug(f"新配置: {self}")
                logger.debug(
                    f"新角色配置: {self.character_config.model_dump()}"
                )

                # 向客户端发送响应
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "set-model-and-conf",
                            "model_info": self.live2d_model.model_info,
                            "conf_name": self.character_config.conf_name,
                            "conf_uid": self.character_config.conf_uid,
                        }
                    )
                )

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "config-switched",
                            "message": f"已切换到配置: {config_file_name}",
                        }
                    )
                )

                logger.info(f"配置已切换到 {config_file_name}")
            else:
                raise ValueError(
                    f"无法从 {config_file_name} 加载配置"
                )

        except Exception as e:
            logger.error(f"切换配置时出错: {e}")
            logger.debug(self)
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"切换配置时出错: {str(e)}",
                    }
                )
            )
            raise e


def deep_merge(dict1, dict2):
    """
    递归将 dict2 合并到 dict1 中，优先使用 dict2 的值。
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
