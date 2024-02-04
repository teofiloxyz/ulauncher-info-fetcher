from typing import Optional, Dict, List, Callable, Union

from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import (
    RenderResultListAction,
)
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from .info_list_manager import InfoList, InfoItemPicker, InfoItem
from .result_item_generator import ResultItemGenerator, CustomActionOption


class InfoFetcher(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.info_list = []
        self.new_info_title = ""
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def fetch_info(self, query: str) -> RenderResultListAction:
        if not query:
            return self._show_message(
                title="Search for info to fetch to the clipboard..."
            )
        return self._render_items_based_on_search(
            query, self._render_items_to_copy
        )

    def add_info_item_title(self, query: str) -> RenderResultListAction:
        """
        It starts by asking for the title, and it executes the CustomAction.
        Then it resets the query to run add_info_item_content.
        """
        if not query:
            return self._show_message("Add a new info item to the list...")
        elif query in [info_item.title for info_item in self.info_list]:
            return self._show_message(
                "There's already an item with this title..."
            )
        return self._render_item_title_to_add(query)

    def add_info_item_content(self, query: str) -> RenderResultListAction:
        if not query:
            return self._show_actionable_message(
                title=f'Now, add the content for "{self.new_info_title}"',
                description="Or just press Enter to reset the title",
            )
        elif query in [info_item.content for info_item in self.info_list]:
            return self._show_message(
                "There's already an item with this content..."
            )
        return self._render_item_content_to_add(query)

    def remove_info_item(self, query: str) -> RenderResultListAction:
        if not query:
            return self._show_message("Search for an info item to remove...")
        return self._render_items_based_on_search(
            query, self._render_items_to_remove
        )

    def hide(self) -> RenderResultListAction:
        item = ResultItemGenerator.generate_hide_item()
        return RenderResultListAction([item])

    def reset_add_info_item_query(self) -> SetUserQueryAction:
        keyword = self.preferences["add_info_item"]
        return SetUserQueryAction(keyword + " ")

    def refresh_info_list(self, force: bool = False) -> None:
        if not self.info_list or force:
            self.info_list = InfoList().get_info_list()

    def _show_message(
        self, title: str, description: str = ""
    ) -> RenderResultListAction:
        item = ResultItemGenerator.generate_message_item(title, description)
        return RenderResultListAction([item])

    def _show_actionable_message(
        self, title: str, description: str = ""
    ) -> RenderResultListAction:
        item = ResultItemGenerator.generate_actionable_message_item(
            title, description
        )
        return RenderResultListAction([item])

    def _search_info_items(self, query: str) -> Optional[List[InfoItem]]:
        return InfoItemPicker(self.preferences).fuzzy_search_info_title(
            query, self.info_list
        )

    def _render_items_based_on_search(
        self,
        query: str,
        render_method: Callable[[List], RenderResultListAction],
    ) -> RenderResultListAction:
        results = self._search_info_items(query)
        if not results:
            return self._show_message("No info items with that title found...")
        return render_method(results)

    def _render_items_to_copy(
        self, results: List[InfoItem]
    ) -> RenderResultListAction:
        items = [
            ResultItemGenerator().generate_item_to_copy(info_item)
            for info_item in results
        ]
        return RenderResultListAction(items)

    def _render_item_title_to_add(self, query: str) -> RenderResultListAction:
        item = ResultItemGenerator().generate_item_title_to_add(query)
        return RenderResultListAction([item])

    def _render_item_content_to_add(self, query: str) -> RenderResultListAction:
        item = ResultItemGenerator().generate_item_content_to_add(
            query, self.new_info_title
        )
        return RenderResultListAction([item])

    def _render_items_to_remove(
        self, results: List[InfoItem]
    ) -> RenderResultListAction:
        items = [
            ResultItemGenerator().generate_item_to_remove(info_item)
            for info_item in results
        ]
        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: InfoFetcher
    ) -> Optional[RenderResultListAction]:
        extension.refresh_info_list()
        keyword = event.get_keyword()
        keyword_id = self._find_keyword_id(keyword, extension.preferences)
        if keyword_id == "fetch_info":
            return extension.fetch_info(event.get_argument())
        elif keyword_id == "add_info_item":
            if not extension.new_info_title:
                return extension.add_info_item_title(event.get_argument())
            return extension.add_info_item_content(event.get_argument())
        elif keyword_id == "remove_info_item":
            return extension.remove_info_item(event.get_argument())
        return None

    @staticmethod
    def _find_keyword_id(keyword: str, preferences: Dict) -> Optional[str]:
        return next(
            (kw_id for kw_id, kw in preferences.items() if kw == keyword), None
        )


class ItemEnterEventListener(EventListener):
    """Only when enter is pressed, from an ExtensionCustomAction item"""

    def on_event(
        self, event: ItemEnterEvent, extension: InfoFetcher
    ) -> Union[RenderResultListAction, SetUserQueryAction]:
        option, data = event.get_data()
        if option == CustomActionOption.ADD_INFO_TITLE:
            extension.new_info_title = data
            return extension.reset_add_info_item_query()
        elif option == CustomActionOption.RESET_INFO_TITLE:
            extension.new_info_title = ""
            return extension.add_info_item_title(query="")
        elif option == CustomActionOption.ADD_INFO_CONTENT:
            InfoList().add_info_item(data)
            extension.new_info_title = ""
        elif option == CustomActionOption.REM_INFO:
            InfoList().remove_info_item(data)
        extension.refresh_info_list(force=True)
        return extension.hide()
