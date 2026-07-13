"""Unit tests for the DictionarySource domain model.

These tests verify the correct initialization, attribute mapping, and structural
integrity of DictionarySource instances, ensuring that categorical enums, optional URLs,
and localization constraints function flawlessly at the domain boundary.

Scenarios included:
    - Ensure a DictionarySource instance initializes correctly for physical media (None URL).
    - Ensure a transient DictionarySource instance handles a None value for its identifier.
    - Ensure a digital media representation accurately maps valid web URL location identifiers.
    - Ensure various boundary payloads, multi-accented titles, and enums map via parametrization.
"""

import datetime
from typing import Optional

import pytest

from app.domain.dictionary_source import DictionarySource
from app.domain.domain_enums import SourceType


@pytest.mark.dictionary
def test_dictionary_source_physical_initialization_with_id() -> None:
    """Verifies that a DictionarySource initializes correctly for physical media without a footprint URL.

    This scenario ensures that persistence database anchors, domain enum types,
    and descriptive title strings are properly matched to operational parameters.
    """
    # Arrange & Act
    fixed_timestamp = datetime.datetime(2026, 7, 8, 5, 20, 0, tzinfo=datetime.timezone.utc)
    source_entry = DictionarySource(
        source_id=12,
        source_type=SourceType.BOOK,
        title="21 bài học cho thế kỷ 21",
        created_at=fixed_timestamp,
        url=None
    )

    # Assert
    assert source_entry.id == 12
    assert source_entry.source_type == SourceType.BOOK
    assert source_entry.title == "21 bài học cho thế kỷ 21"
    assert source_entry.created_at == fixed_timestamp
    assert source_entry.url is None


@pytest.mark.dictionary
def test_dictionary_source_transient_initialization_without_id() -> None:
    """Verifies that a transient DictionarySource instance initializes correctly with a None identifier.

    This scenario guarantees that dynamic curation forms and administrative inputs can safely
    construct origin references before committing rows to the backend database engine.
    """
    # Arrange & Act
    current_time = datetime.datetime.now(datetime.timezone.utc)
    transient_source = DictionarySource(
        source_id=None,
        source_type=SourceType.MANGA,
        title="Doraemon Tập 1",
        created_at=current_time,
        url=None
    )

    # Assert
    assert transient_source.id is None
    assert transient_source.source_type == SourceType.MANGA
    assert transient_source.title == "Doraemon Tập 1"
    assert transient_source.created_at == current_time
    assert transient_source.url is None


@pytest.mark.dictionary
def test_dictionary_source_digital_initialization_with_url() -> None:
    """Verifies that a digital DictionarySource properly preserves tracking web URL paths.

    This scenario validates that network string addresses are safely retained alongside
    complex Unicode title blocks without clipping or alteration.
    """
    # Arrange & Act
    fixed_timestamp = datetime.datetime(2026, 7, 8, 5, 25, 0, tzinfo=datetime.timezone.utc)
    target_url = "https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html"

    digital_source = DictionarySource(
        source_id=14,
        source_type=SourceType.ARTICLE,
        title="VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?",
        created_at=fixed_timestamp,
        url=target_url
    )

    # Assert
    assert digital_source.id == 14
    assert digital_source.source_type == SourceType.ARTICLE
    assert digital_source.title == "VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?"
    assert digital_source.created_at == fixed_timestamp
    assert digital_source.url == target_url


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "source_id,source_type,title,url",
    [
        # Case 1: Zero boundary indices for local IDs
        (0, SourceType.BOOK, "Từ điển Tiếng Việt", None),

        # Case 2: Negative database identifier boundaries
        (-1, SourceType.ARTICLE, "Báo tuổi trẻ", "https://tuoitre.vn"),

        # Case 3: Advanced combining diacritics and complex tone typography sets
        (99, SourceType.ARTICLE, "Truyện Kiều - Nguyễn Du (Bản khảo dị tổng hợp)", None),

        # Case 4: Extreme string length boundary for long tracking parameters
        (
                450,
                SourceType.ARTICLE,
                "Học thuật điện tử",
                "https://example.org/" + ("a" * 2000)
        ),
    ],
    ids=[
        "zero_id",
        "negative_id",
        "complex_diacritics_and_tones",
        "extreme_url_length_boundary"
    ]
)
def test_dictionary_source_parameterized_edge_cases(
        source_id: Optional[int],
        source_type: SourceType,
        title: str,
        url: Optional[str]  # Removed the default '= None' parameter here
) -> None:
    """Verifies that parameterized boundary conditions map cleanly to structural instance variables.

    This scenario ensures multi-accented title components, extreme URL lengths, and system
    numerical tokens are processed down without configuration collapse.
    """
    # Arrange
    static_time = datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    # Act
    source_entry = DictionarySource(
        source_id=source_id,
        source_type=source_type,
        title=title,
        created_at=static_time,
        url=url
    )

    # Assert
    assert source_entry.id == source_id
    assert source_entry.source_type == source_type
    assert source_entry.title == title
    assert source_entry.created_at == static_time
    assert source_entry.url == url
