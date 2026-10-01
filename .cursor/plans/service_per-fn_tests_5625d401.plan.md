---
name: Service per-fn tests
overview: Add per-function test directories for DictionaryDashboardService (integration) and dictionary_validation (unit), with new dashboard seed fixtures, migrate/remove the monolithic validation file, and extend the existing [1.4.0] changelog plus commit draft.
todos:
  - id: dashboard-seed-fixtures
    content: Add seed_dashboard_* and set_word_created_at fixtures to dictionary_data_fixtures.py
    status: completed
  - id: dashboard-service-tests
    content: Create tests/integration/services/dictionary_dashboard_service/ with one file per public method; remove service velocity test from repo suite
    status: completed
  - id: validation-unit-split
    content: Create tests/unit/services/dictionary_validation/ per function; relocate split_syllables; delete monolithic test_dictionary_validation.py
    status: completed
  - id: changelog-commit-draft
    content: Extend [1.4.0] changelog and update temporary commit-message draft (no commit)
    status: completed
  - id: run-pytest
    content: Run targeted .venv pytest for new/updated service test packages
    status: completed
isProject: false
---

# Per-function tests for dashboard + validation services (v1.4.0)

## Placement (matches existing suite)

- [`DictionaryDashboardService`](app/services/dictionary_dashboard_service.py) → [`tests/integration/services/dictionary_dashboard_service/`](tests/integration/services/) (DB-backed, like [`blog_service/`](tests/integration/services/blog_service/))
- [`dictionary_validation`](app/services/dictionary_validation.py) → [`tests/unit/services/dictionary_validation/`](tests/unit/services/) (pure helpers, like [`formatting_service/`](tests/unit/services/formatting_service/) / [`sanitization_service/`](tests/unit/services/sanitization_service/))

Validation stays under **unit**, not integration. Private `_fill_velocity_gaps` is covered via `get_word_velocity` only (no dedicated private-method file).

Conventions: module docstring listing tests; each test docstring starts with "Verifies that..."; `@pytest.mark.dictionary`; parametrize input matrices.

---

## A. New fixtures in [`tests/fixtures/dictionary_data_fixtures.py`](tests/fixtures/dictionary_data_fixtures.py)

Reuse `make_*` / `bind_*` / existing `seed_dictionary`. Add scenario seeds:

1. `seed_dashboard_general` — mixed coverage for General + Data Health (HV+type+example word; bare word; spaced compound without HV; cited source for top-sources).
2. `seed_dashboard_sources` — ≥3 sources across types with uneven citation counts for sort/filter/pagination.
3. `seed_dashboard_han_viet` — reused root + orphan root + distinct Chinese characters.
4. `set_word_created_at(word_id, when)` — UPDATE helper for velocity `created_at` control.

---

## B. Dashboard service tests (integration)

Create `tests/integration/services/dictionary_dashboard_service/`:

- `test_get_general_metrics.py` — empty zeros; seeded KPI math, etymology split, word_types, top_sources by citations, recent_activity
- `test_get_sources_catalog.py` — parametrized sorts; type/q filters; pagination; empty payload shape; echoed filter fields
- `test_get_han_viet_analytics.py` — totals; top reused first; orphans only unbound
- `test_get_data_health.py` — expected audit queues; `limit` truncation
- `test_get_word_velocity.py` — parametrize `30d`/`6m`/`12m` shape; seeded window counts; invalid → `ValueError`; gap-fill zeros

Instantiate with `DictionaryDashboardService(session)`.

Remove `test_dashboard_service_word_velocity_shape` from [`tests/integration/models/repositories/test_dictionary_dashboard_repositories.py`](tests/integration/models/repositories/test_dictionary_dashboard_repositories.py). Keep repo-only aggregate tests and HTTP smoke in [`test_admin_dictionary_dashboard.py`](tests/integration/routes/admin/test_admin_dictionary_dashboard.py).

---

## C. Validation tests (unit, per-function)

Create `tests/unit/services/dictionary_validation/`:

- `test_normalize_viet_word.py` — trim / empty parametrize
- `test_validate_viet_word.py` — accept/reject matrices; assert `field == "viet_word"`
- `test_validate_english_translation.py` — accept trimmed; reject blank; assert field
- `test_validate_word_types.py` — empty/None → `[]`; dedupe; case-normalize; reject unknown

Delete monolithic [`tests/unit/services/test_dictionary_validation.py`](tests/unit/services/test_dictionary_validation.py) after migration.

Move the misplaced `split_syllables` test into `tests/unit/services/han_viet_service/test_split_syllables.py` (create directory). No production code change.

---

## D. Changelog + commit draft (still [1.4.0])

Extend [`CHANGELOG.md`](CHANGELOG.md) `[1.4.0]` Added with a testing bullet for per-function dashboard integration tests and validation unit split.

Update [`temporary/commit-drafts/v1.4.0-ui-auth-dashboard.txt`](temporary/commit-drafts/v1.4.0-ui-auth-dashboard.txt) (or sibling draft) to mention the service test package split. Do not commit.

---

## E. Verification

Run via `.venv`:

```text
pytest tests/integration/services/dictionary_dashboard_service/
       tests/unit/services/dictionary_validation/
       tests/unit/services/han_viet_service/test_split_syllables.py
       tests/integration/models/repositories/test_dictionary_dashboard_repositories.py -q
```

---

## Ordered steps

1. Add dashboard seed / `set_word_created_at` fixtures
2. Write five dashboard service integration modules; drop service velocity case from repo tests
3. Split validation into four unit modules; relocate `split_syllables`; delete monolithic file
4. Update `[1.4.0]` changelog + commit-message draft
5. Run targeted pytest via `.venv`
