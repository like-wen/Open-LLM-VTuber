# config_manager/i18n.py
from typing import Dict, ClassVar
from pydantic import BaseModel, Field, ConfigDict


class MultiLingualString(BaseModel):
    """
    表示具有多种语言翻译的字符串。
    """

    en: str = Field(..., description="英语翻译")
    zh: str = Field(..., description="中文翻译")

    def get(self, lang_code: str) -> str:
        """
        检索指定语言代码的翻译。

        参数:
            lang_code: 语言代码（例如，"en"，"zh"）。

        返回:
            指定语言代码的翻译，如果未找到指定语言，则返回英语翻译。
        """
        return getattr(self, lang_code, self.en)


class Description(MultiLingualString):
    """
    表示具有多种语言翻译的描述。
    """

    notes: MultiLingualString | None = Field(
        default=None, description="附加说明"
    )

    def get_text(self, lang_code: str) -> str:
        """
        检索指定语言的主要描述文本。

        参数:
            lang_code: 语言代码（例如，"en"，"zh"）。

        返回:
            指定语言的主要描述文本。
        """
        return self.get(lang_code)

    def get_notes(self, lang_code: str) -> str | None:
        """
        检索指定语言的附加说明。

        参数:
            lang_code: 语言代码（例如，"en"，"zh"）。

        返回:
            指定语言的附加说明，如果没有可用的说明则返回None。
        """
        return self.notes.get(lang_code) if self.notes else None

    @classmethod
    def from_str(cls, text: str, notes: str | None = None) -> "Description":
        """
        从纯字符串创建Description实例，假设英语为默认语言。

        参数:
            text: 主要描述文本。
            notes: 附加说明（可选）。

        返回:
            一个Description实例，包含提供的英语文本和说明。
        """
        return cls(
            en=text,
            zh=text,
            notes=MultiLingualString(en=notes, zh=notes) if notes else None,
        )


class I18nMixin(BaseModel):
    """
    为 Pydantic 模型提供字段多语言描述的混合类。
    """

    model_config = ConfigDict(populate_by_name=True)

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {}

    @classmethod
    def get_field_description(
        cls, field_name: str, lang_code: str = "en"
    ) -> str | None:
        """
        检索指定语言中字段的描述。

        参数:
            field_name: 字段的名称。
            lang_code: 语言代码（例如，"en"，"zh"）。

        返回:
            指定语言中字段的描述，如果没有可用的描述则返回None。
        """
        description = cls.DESCRIPTIONS.get(field_name)
        if description:
            return description.get_text(lang_code)
        return None

    @classmethod
    def get_field_notes(cls, field_name: str, lang_code: str = "en") -> str | None:
        """
        检索指定语言中字段的附加说明。

        参数:
            field_name: 字段的名称。
            lang_code: 语言代码（例如，"en"，"zh"）。

        返回:
            指定语言中字段的附加说明，如果没有可用的说明则返回None。
        """
        description = cls.DESCRIPTIONS.get(field_name)
        if description:
            return description.get_notes(lang_code)
        return None

    @classmethod
    def get_field_options(cls, field_name: str) -> list | Dict | None:
        """
        检索字段的选项（如果已定义）。

        参数:
            field_name: 字段的名称。

        返回:
            字段的选项，可以是列表或字典，如果没有定义选项则返回None。
        """
        field = cls.model_fields.get(field_name)
        if field:
            if hasattr(field, "options"):
                return field.options
        return None
