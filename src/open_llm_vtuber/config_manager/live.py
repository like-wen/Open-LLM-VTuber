from pydantic import Field
from typing import Dict, ClassVar, List
from .i18n import I18nMixin, Description


class BiliBiliLiveConfig(I18nMixin):
    """B站直播平台配置。"""

    room_ids: List[int] = Field([], alias="room_ids")
    sessdata: str = Field("", alias="sessdata")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "room_ids": Description(
            en="List of BiliBili live room IDs to monitor", zh="要监控的B站直播间ID列表"
        ),
        "sessdata": Description(
            en="SESSDATA cookie value for authenticated requests (optional)",
            zh="用于认证请求的SESSDATA cookie值（可选）",
        ),
    }


class LiveConfig(I18nMixin):
    """直播平台集成配置。"""

    bilibili_live: BiliBiliLiveConfig = Field(
        BiliBiliLiveConfig(), alias="bilibili_live"
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "bilibili_live": Description(
            en="Configuration for BiliBili Live platform", zh="B站直播平台配置"
        ),
    }
