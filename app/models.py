from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class SimpleListModel(QAbstractListModel):
    def __init__(self, roles: list[str], parent=None) -> None:
        super().__init__(parent)
        self._roles = roles
        self._items: list[dict[str, str]] = []

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return len(self._items)

    def data(self, index: QModelIndex, role: int):  # noqa: N802
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._items):
            return None
        item = self._items[row]
        role_name = self._role_name(role)
        if not role_name:
            return None
        return item.get(role_name, "")

    def roleNames(self) -> dict[int, bytes]:  # noqa: N802
        return {
            Qt.UserRole + idx: role.encode("utf-8")
            for idx, role in enumerate(self._roles, start=1)
        }

    def _role_name(self, role: int) -> str | None:
        if role < Qt.UserRole:
            return None
        idx = role - Qt.UserRole - 1
        if 0 <= idx < len(self._roles):
            return self._roles[idx]
        return None

    def set_items(self, items: list[dict[str, str]]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def clear(self) -> None:
        self.set_items([])


class PreviewModel(SimpleListModel):
    def __init__(self, parent=None) -> None:
        super().__init__(
            ["name", "ddi", "phone", "tags", "created"],
            parent,
        )


class SuspectModel(SimpleListModel):
    def __init__(self, parent=None) -> None:
        super().__init__(
            ["reason", "source", "raw_phone", "normalized_phone", "name", "suggested_fix", "line"],
            parent,
        )
