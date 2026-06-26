import json
from pathlib import Path

from backend.app.schemas import InterviewType, InterviewTypeInfo, Topic


class KnowledgeBase:
    def __init__(self, path: Path):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def interview_types(self) -> list[InterviewTypeInfo]:
        items = []
        for key, value in self._data["interview_types"].items():
            items.append(
                InterviewTypeInfo(
                    id=key,
                    label=value["label"],
                    description=value["description"],
                )
            )
        return items

    def opening(self, interview_type: InterviewType) -> str:
        return self._data["interview_types"][interview_type]["opening"]

    def topics(self, interview_type: InterviewType) -> list[Topic]:
        raw_topics = self._data["interview_types"][interview_type]["topics"]
        return [Topic(**topic) for topic in raw_topics]
