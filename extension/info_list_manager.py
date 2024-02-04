from dataclasses import dataclass
import json
import os
import subprocess
import sys
from typing import List, Dict, Optional

EXT_PATH = os.path.dirname(sys.argv[0])
INFO_PATH = os.path.join(EXT_PATH, "info_list.json")


@dataclass
class InfoItem:
    title: str
    content: str


class InfoList:
    def get_info_list(self) -> List[InfoItem]:
        return [
            InfoItem(item["title"], item["content"])
            for item in self._read_info_list()
        ]

    def add_info_item(self, info_item: InfoItem) -> None:
        info_items = self._read_info_list()
        info_items.append(
            {"title": info_item.title, "content": info_item.content}
        )
        self._write_info_list(info_items)

    def remove_info_item(self, info_item: InfoItem) -> None:
        info_items = self._read_info_list()
        new_info_items = [
            d for d in info_items if d["title"] != info_item.title
        ]
        self._write_info_list(new_info_items)

    def _read_info_list(self) -> List[Dict[str, str]]:
        try:
            with open(INFO_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _write_info_list(self, info_items: List[Dict[str, str]]) -> None:
        with open(INFO_PATH, "w") as f:
            json.dump(info_items, f, indent=4)


class InfoItemPicker:
    def __init__(self, preferences: Dict) -> None:
        self.max_search_results = preferences["max_search_results"]

    def fuzzy_search_info_title(
        self, query: str, info_items: List[InfoItem]
    ) -> Optional[List[InfoItem]]:
        titles_string = self._get_titles_string(info_items)
        search_results = self._execute_fuzzy_search_cmd(titles_string, query)
        if not search_results:
            return None
        return self._filter_info_items_by_search_results(
            info_items, search_results
        )

    def _get_titles_string(self, info_items: List[InfoItem]) -> str:
        return "\n".join(item.title for item in info_items)

    def _execute_fuzzy_search_cmd(
        self, titles: str, query: str
    ) -> Optional[List[str]]:
        cmd = f'echo -e "{titles}" | fzf --filter "{query}"'
        try:
            output = subprocess.check_output(cmd, text=True, shell=True)
        except subprocess.CalledProcessError:
            return None
        return output.splitlines()[: self.max_search_results]

    def _filter_info_items_by_search_results(
        self, info_items: List[InfoItem], titles_to_match: List[str]
    ) -> List[InfoItem]:
        """Must follow the order of titles_to_match"""
        matching_items = [
            item for item in info_items if item.title in titles_to_match
        ]
        return sorted(
            matching_items, key=lambda item: titles_to_match.index(item.title)
        )
