"""Controllers for dictionary search and administrative dictionary workflows."""

from typing import Any, Dict, List, Optional, Tuple

from flask import Response as FlaskResponse
from flask import jsonify, render_template

from app import db
from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_source import DictionarySource
from app.domain.dictionary_word import DictionaryWord
from app.domain.domain_enums import SourceType, WordType
from app.domain.han_viet_root import HanVietRoot
from app.exceptions import (
    DictionaryValidationError,
    DictionaryWordDuplicateError,
    DictionaryWordNotFoundError,
    DictionarySourceNotFoundError,
    HanVietRootInUseError,
    HanVietRootNotFoundError,
)
from app.services.auth_service import is_admin_authenticated
from app.services.han_viet_service import HanVietService
from app.services.source_service import SourceService
from app.services.word_service import WordService


def _serialize_source(source: DictionarySource) -> Dict[str, Any]:
    source_type = source.source_type
    if hasattr(source_type, "value"):
        source_type = source_type.value
    return {
        "id": source.id,
        "source_type": source_type,
        "title": source.title,
        "url": source.url,
        "created_at": source.created_at.isoformat() if source.created_at else None,
    }


def _serialize_root(root: HanVietRoot) -> Dict[str, Any]:
    return {
        "id": root.id,
        "root": root.root,
        "chinese_character": root.chinese_character,
        "root_meaning": root.root_meaning,
    }


def _serialize_example(example: DictionaryExample) -> Dict[str, Any]:
    return {
        "id": example.id,
        "word_id": example.word_id,
        "source_id": example.source_id,
        "sentence": example.sentence,
        "english_translation": example.english_translation,
        "created_at": example.created_at.isoformat() if example.created_at else None,
        "source": _serialize_source(example.source) if example.source else None,
    }


def _serialize_word_summary(word: DictionaryWord) -> Dict[str, Any]:
    return {
        "id": word.id,
        "viet_word": word.viet_word,
        "english_translation": word.english_translation,
        "word_types": list(word.word_types or []),
    }


def _serialize_word_detail(word: DictionaryWord) -> Dict[str, Any]:
    payload = _serialize_word_summary(word)
    payload.update(
        {
            "examples": [_serialize_example(example) for example in (word.examples or [])],
            "han_viet_roots": [_serialize_root(root) for root in (word.han_viet_roots or [])],
            "level": word.level,
            "has_han_viet": word.has_han_viet,
            "created_at": word.created_at.isoformat() if word.created_at else None,
            "updated_at": word.updated_at.isoformat() if word.updated_at else None,
        }
    )
    return payload


def render_dictionary_page() -> Tuple[str, int]:
    """Render the public dictionary search page."""
    html = render_template(
        "dictionary/index.html",
        is_admin=is_admin_authenticated(),
    )
    return html, 200


def render_create_workspace() -> Tuple[str, int]:
    """Render the admin dictionary creation workspace."""
    source_service = SourceService(db.session)
    html = render_template(
        "admin/dictionary_create.html",
        word_types=[member.value for member in WordType],
        source_types=[member.value for member in SourceType],
        recent_sources=[_serialize_source(s) for s in source_service.list_recent()],
        is_admin=True,
    )
    return html, 200


def render_edit_workspace(word_id: int) -> Tuple[FlaskResponse | str, int]:
    """Render the admin dictionary modification workspace."""
    service = WordService(db.session)
    source_service = SourceService(db.session)
    try:
        word = service.get_entry(word_id)
    except DictionaryWordNotFoundError as exc:
        return jsonify({"success": False, "message": exc.message}), 404

    html = render_template(
        "admin/dictionary_edit.html",
        word=_serialize_word_detail(word),
        word_types=[member.value for member in WordType],
        source_types=[member.value for member in SourceType],
        recent_sources=[_serialize_source(s) for s in source_service.list_recent()],
        is_admin=True,
    )
    return html, 200


def search_dictionary(query: str, limit: int = 20) -> Tuple[FlaskResponse, int]:
    """Return autocomplete JSON matches for a Vietnamese prefix query."""
    service = WordService(db.session)
    results = service.search_prefix(query, limit=limit)
    return jsonify({
        "results": [_serialize_word_summary(word) for word in results],
        "is_admin": is_admin_authenticated(),
    }), 200


def check_duplicate(viet_word: str) -> Tuple[FlaskResponse, int]:
    """Return a JSON summary when a duplicate dictionary word exists."""
    service = WordService(db.session)
    existing = service.check_duplicate(viet_word)
    if existing is None:
        return jsonify({"exists": False}), 200
    return jsonify({
        "exists": True,
        "entry": {
            "id": existing.id,
            "viet_word": existing.viet_word,
            "english_translation": existing.english_translation,
        },
    }), 200


def create_word(
        viet_word: str,
        english_translation: str,
        word_types: Optional[List[str]] = None,
) -> Tuple[FlaskResponse, int]:
    """Create a new dictionary entry."""
    service = WordService(db.session)
    try:
        word = service.create_entry(viet_word, english_translation, word_types)
        db.session.commit()
    except DictionaryValidationError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message, "field": exc.field}), 400
    except DictionaryWordDuplicateError as exc:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": exc.message,
            "duplicate": {
                "id": None,
                "viet_word": exc.viet_word,
            },
        }), 409
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True, "entry": _serialize_word_detail(word)}), 201


def update_word(
        word_id: int,
        viet_word: Optional[str] = None,
        english_translation: Optional[str] = None,
        word_types: Optional[List[str]] = None,
) -> Tuple[FlaskResponse, int]:
    """Update an existing dictionary entry."""
    service = WordService(db.session)
    try:
        word = service.update_entry(
            word_id,
            viet_word=viet_word,
            english_translation=english_translation,
            word_types=word_types,
        )
        db.session.commit()
    except DictionaryValidationError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message, "field": exc.field}), 400
    except DictionaryWordNotFoundError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message}), 404
    except DictionaryWordDuplicateError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message}), 409
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True, "entry": _serialize_word_detail(word)}), 200


def delete_word(word_id: int) -> Tuple[FlaskResponse, int]:
    """Permanently delete a dictionary entry."""
    service = WordService(db.session)
    try:
        service.delete_entry(word_id)
        db.session.commit()
    except DictionaryWordNotFoundError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True}), 200


def get_word(word_id: int) -> Tuple[FlaskResponse, int]:
    """Return a full dictionary entry as JSON."""
    service = WordService(db.session)
    try:
        word = service.get_entry(word_id)
    except DictionaryWordNotFoundError as exc:
        return jsonify({"success": False, "message": exc.message}), 404
    return jsonify({"entry": _serialize_word_detail(word)}), 200


def add_example(
        word_id: int,
        source_id: int,
        sentence: str,
        english_translation: str,
) -> Tuple[FlaskResponse, int]:
    """Add a contextual example to a dictionary entry."""
    service = WordService(db.session)
    try:
        example = service.add_example(word_id, source_id, sentence, english_translation)
        db.session.commit()
    except DictionaryValidationError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message, "field": exc.field}), 400
    except (DictionaryWordNotFoundError, DictionarySourceNotFoundError) as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True, "example": _serialize_example(example)}), 201


def remove_example(example_id: int) -> Tuple[FlaskResponse, int]:
    """Remove a contextual example."""
    service = WordService(db.session)
    try:
        service.remove_example(example_id)
        db.session.commit()
    except RuntimeError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True}), 200


def list_sources(query: str = "") -> Tuple[FlaskResponse, int]:
    """List or search sources for the admin workspace."""
    service = SourceService(db.session)
    sources = service.search(query=query) if query else service.list_recent()
    return jsonify({"sources": [_serialize_source(source) for source in sources]}), 200


def create_source(
        source_type: str,
        title: str,
        url: Optional[str] = None,
) -> Tuple[FlaskResponse, int]:
    """Create a new dictionary source."""
    service = SourceService(db.session)
    try:
        source = service.create(source_type=source_type, title=title, url=url)
        db.session.commit()
    except DictionaryValidationError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message, "field": exc.field}), 400
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True, "source": _serialize_source(source)}), 201


def check_han_viet_roots(compound_word: str) -> Tuple[FlaskResponse, int]:
    """Return found and missing Hán Việt roots for a compound word."""
    service = HanVietService(db.session)
    result = service.check_existing_roots(compound_word)
    return jsonify(result), 200


def associate_han_viet_root(word_id: int, root_id: int) -> Tuple[FlaskResponse, int]:
    """Associate an existing Hán Việt root with a dictionary word."""
    service = HanVietService(db.session)
    try:
        service.associate_root(word_id, root_id)
        db.session.commit()
    except (DictionaryWordNotFoundError, HanVietRootNotFoundError) as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True}), 200


def create_han_viet_root(
        word_id: int,
        root: str,
        chinese_character: str,
        root_meaning: str,
) -> Tuple[FlaskResponse, int]:
    """Create a Hán Việt root and associate it with a dictionary word."""
    service = HanVietService(db.session)
    try:
        created = service.create_and_associate(
            word_id=word_id,
            root=root,
            chinese_character=chinese_character,
            root_meaning=root_meaning,
        )
        db.session.commit()
    except DictionaryValidationError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message, "field": exc.field}), 400
    except DictionaryWordNotFoundError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True, "root": _serialize_root(created)}), 201


def unlink_han_viet_root(word_id: int, root_id: int) -> Tuple[FlaskResponse, int]:
    """Unlink a Hán Việt root from a dictionary word without deleting the root."""
    service = HanVietService(db.session)
    try:
        service.unlink_root(word_id, root_id)
        db.session.commit()
    except (DictionaryWordNotFoundError, HanVietRootNotFoundError) as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True}), 200


def delete_han_viet_root(root_id: int) -> Tuple[FlaskResponse, int]:
    """Delete a Hán Việt root when it has no remaining associations."""
    service = HanVietService(db.session)
    try:
        service.delete_root(root_id)
        db.session.commit()
    except HanVietRootInUseError as exc:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": exc.message,
            "association_count": exc.association_count,
            "can_unlink": True,
        }), 409
    except HanVietRootNotFoundError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": exc.message}), 404
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"success": True}), 200
