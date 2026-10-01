"""Service layer for dictionary admin dashboard analytics."""

from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.repositories.han_viet_repository import HanVietRepository
from app.models.repositories.source_repository import SourceRepository
from app.models.repositories.word_repository import WordRepository

VALID_VELOCITY_RANGES = frozenset({"30d", "6m", "12m"})
DEFAULT_SOURCES_PER_PAGE = 20


class DictionaryDashboardService:
    """Aggregate dictionary metrics for the admin dashboard tabs."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.words = WordRepository(session)
        self.sources = SourceRepository(session)
        self.han_viet = HanVietRepository(session)

    def get_general_metrics(self) -> Dict[str, Any]:
        """Build KPI cards and categorical summaries for the General tab."""
        total_words = self.words.count_words()
        total_sources = self.sources.count_sources()
        words_with_hv = self.words.count_words_with_han_viet()
        words_with_examples = self.words.count_words_with_examples()

        hv_coverage = (words_with_hv / total_words * 100.0) if total_words else 0.0
        citation_coverage = (
            (words_with_examples / total_words * 100.0) if total_words else 0.0
        )

        etymology = [
            {"label": "Hán Việt", "count": words_with_hv},
            {"label": "Native/Other", "count": max(total_words - words_with_hv, 0)},
        ]
        word_types = [
            {"label": label, "count": count}
            for label, count in self.words.word_type_counts().items()
        ]
        top_sources, _ = self.sources.list_sources_catalog(
            page=1,
            per_page=8,
            sort="citations_desc",
        )
        recent = self.words.list_recently_updated(limit=10)

        return {
            "kpis": {
                "total_words": total_words,
                "total_sources": total_sources,
                "han_viet_coverage": round(hv_coverage, 1),
                "citation_coverage": round(citation_coverage, 1),
            },
            "etymology": etymology,
            "word_types": word_types,
            "top_sources": top_sources,
            "recent_activity": recent,
        }

    def get_sources_catalog(
            self,
            page: int = 1,
            per_page: int = DEFAULT_SOURCES_PER_PAGE,
            sort: str = "created_at_desc",
            source_type: Optional[str] = None,
            title_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return paginated sources catalog data for the Sources tab."""
        items, total = self.sources.list_sources_catalog(
            page=page,
            per_page=per_page,
            sort=sort,
            source_type=source_type,
            title_query=title_query,
        )
        total_pages = max(1, ceil(total / per_page)) if total else 1
        return {
            "rows": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "sort": sort,
            "source_type": source_type or "",
            "title_query": title_query or "",
        }

    def get_han_viet_analytics(self) -> Dict[str, Any]:
        """Return Hán Việt analytics for the dedicated dashboard tab."""
        return {
            "total_roots": self.han_viet.count_roots(),
            "distinct_chinese_characters": self.han_viet.count_distinct_chinese_characters(),
            "top_reused_roots": self.han_viet.list_top_reused_roots(limit=15),
            "orphan_roots": self.han_viet.list_orphan_roots(),
        }

    def get_data_health(self, limit: int = 50) -> Dict[str, Any]:
        """Return audit queues for the Data Health tab."""
        return {
            "missing_examples": self.words.list_words_missing_examples(limit=limit),
            "missing_types": self.words.list_words_missing_types(limit=limit),
            "multi_syllable_without_han_viet": self.words.list_multi_syllable_without_han_viet(
                limit=limit
            ),
        }

    def get_word_velocity(self, range_key: str) -> Dict[str, List]:
        """Return gap-filled word-creation velocity series for Chart.js."""
        if range_key not in VALID_VELOCITY_RANGES:
            raise ValueError(f"Unsupported velocity range '{range_key}'")

        raw = dict(self.words.count_words_created_by_bucket(range_key))
        labels, counts = self._fill_velocity_gaps(range_key, raw)
        return {"labels": labels, "counts": counts}

    @staticmethod
    def _fill_velocity_gaps(
            range_key: str,
            raw: Dict[str, int],
    ) -> Tuple[List[str], List[int]]:
        now = datetime.now(timezone.utc)
        labels: List[str] = []

        if range_key == "30d":
            for offset in range(29, -1, -1):
                day = (now - timedelta(days=offset)).date()
                labels.append(day.isoformat())
        elif range_key == "6m":
            # Approximate ISO year-week keys matching MySQL YEARWEEK(date, 3).
            cursor = (now - timedelta(days=183)).date()
            end = now.date()
            seen = set()
            while cursor <= end:
                iso_year, iso_week, _ = cursor.isocalendar()
                key = f"{iso_year}{iso_week:02d}"
                if key not in seen:
                    seen.add(key)
                    labels.append(key)
                cursor += timedelta(days=1)
        else:
            year, month = now.year, now.month
            months: List[str] = []
            for _ in range(12):
                months.append(f"{year:04d}-{month:02d}")
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            labels = list(reversed(months))

        counts = [int(raw.get(label, 0)) for label in labels]
        return labels, counts
