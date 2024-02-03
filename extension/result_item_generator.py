from enum import Enum, auto

from ulauncher.api.shared.action.CopyToClipboardAction import (
    CopyToClipboardAction,
)
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import (
    ExtensionCustomAction,
)
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from .info_list_manager import InfoItem


class Icon:
    default = "images/icon.png"
    email = "images/email.png"
    number = "images/number.png"


class CustomActionOption(Enum):
    ADD_INFO_TITLE = auto()
    RESET_INFO_TITLE = auto()
    ADD_INFO_CONTENT = auto()
    REM_INFO = auto()


class ResultItemGenerator:
    def generate_item_to_copy(self, info_item: InfoItem) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=info_item.title,
            icon=self._get_icon(info_item.content),
            description=info_item.content,
            on_enter=CopyToClipboardAction(info_item.content),
        )

    def generate_item_title_to_add(self, query: str) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=query,
            icon=Icon.default,
            description=f"Add new info item: {query}",
            on_enter=ExtensionCustomAction(
                (CustomActionOption.ADD_INFO_TITLE, query),
                keep_app_open=True,
            ),
        )

    def generate_item_content_to_add(
        self, query: str, new_item_title: str
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=query,
            icon=self._get_icon(query),
            description=f"Add this content to: {new_item_title}",
            on_enter=ExtensionCustomAction(
                (
                    CustomActionOption.ADD_INFO_CONTENT,
                    InfoItem(title=new_item_title, content=query),
                ),
                keep_app_open=False,
            ),
        )

    def generate_item_to_remove(
        self, info_item: InfoItem
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=info_item.title,
            icon=self._get_icon(info_item.content),
            description="Remove info item?",
            on_enter=ExtensionCustomAction(
                (CustomActionOption.REM_INFO, info_item), keep_app_open=False
            ),
        )

    @staticmethod
    def generate_message_item(
        title: str, description: str = ""
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=title,
            icon=Icon.default,
            description=description,
            on_enter=DoNothingAction(),
        )

    @staticmethod
    def generate_actionable_message_item(
        title: str, description: str = ""
    ) -> ExtensionResultItem:
        return ExtensionResultItem(
            name=title,
            icon=Icon.default,
            description=description,
            on_enter=ExtensionCustomAction(
                (CustomActionOption.RESET_INFO_TITLE, None), keep_app_open=True
            ),
        )

    @staticmethod
    def generate_hide_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            on_enter=HideWindowAction(),
        )

    @staticmethod
    def _get_icon(content: str) -> str:
        if "@" in content:
            return Icon.email
        if content.isnumeric():
            return Icon.number
        return Icon.default
