import unittest
from types import SimpleNamespace

from asw.gui import grouped_activity


class GuiTests(unittest.TestCase):
    def test_activity_groups_by_application_and_sorts_newest_first(self) -> None:
        service = SimpleNamespace(signals=[
            {"application_id": "app.b", "created_at": "2026-08-01T12:00:00Z"},
            {"application_id": "app.a", "created_at": "2026-08-01T12:01:00Z"},
            {"application_id": "app.a", "created_at": "2026-08-01T11:00:00Z"},
        ])
        grouped = grouped_activity(service)
        self.assertEqual([item["created_at"] for item in grouped["app.a"]], ["2026-08-01T12:01:00Z", "2026-08-01T11:00:00Z"])


if __name__ == "__main__": unittest.main()
