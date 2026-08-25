# Journal d'exécution — CORE-CORR-001

Branche : `fix/audit-core-corr-001`  
Point de départ : tag `v0.1.0`, commit `dfb1ab9943d78f60101cb1f903def82b17edc36d`

Ce journal consigne les commandes exécutées, les échecs observés avant correction et les résultats après correction. Il constitue une preuve d'exécution, pas une certification indépendante.

## Baseline

Commande initiale avec le Python système :

    python -m pytest --cov=core --cov-report=term-missing --cov-fail-under=90

Sortie brute :

    /run/current-system/sw/bin/python: No module named pytest

Le dépôt possédait déjà un environnement local. Commandes rejouées :

    .venv/bin/python --version
    .venv/bin/python -m pytest --cov=core --cov-report=term-missing --cov-fail-under=90
    .venv/bin/python -m ruff check core tests examples
    .venv/bin/python -m mypy core tests

Sorties brutes significatives :

    Python 3.13.5
    43 passed in 0.95s
    TOTAL 500 34 93%
    Required test coverage of 90% reached. Total coverage: 93.20%
    Found 35 errors.
    [*] 20 fixable with the `--fix` option.
    Success: no issues found in 25 source files

Note : cet environnement préexistant utilise Python 3.13.5, hors de la plage déclarée `>=3.11,<3.13`. C3 vérifiera donc également une installation propre avec un interpréteur pris en charge.

## A1 — Échantillon insuffisant pour le contrôle de look-ahead

Test ajouté : `CoreContractTests.test_lookahead_rejects_insufficient_sample`.

Commande avant correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_lookahead_rejects_insufficient_sample -q

Sortie brute :

    F                                                                        [100%]
    =================================== FAILURES ===================================
    _________ CoreContractTests.test_lookahead_rejects_insufficient_sample _________
    tests/test_core_contracts.py:510: in test_lookahead_rejects_insufficient_sample
        self.assertEqual(report.status, "FAIL")
    E   AssertionError: 'PASS' != 'FAIL'
    E   - PASS
    E   + FAIL
    =========================== short test summary info ============================
    FAILED tests/test_core_contracts.py::CoreContractTests::test_lookahead_rejects_insufficient_sample

Correction : `_no_lookahead` produit maintenant un échec explicite avec `reason=insufficient sample`, le nombre d'observations et le minimum requis.

Commandes après correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_lookahead_rejects_insufficient_sample -q
    .venv/bin/python -m pytest -q

Sorties brutes :

    .                                                                        [100%]
    ............................................                             [100%]

## A2 — Rejet d'un flux DAL vide

Test ajouté : `CoreContractTests.test_dal_boundary_rejects_empty_stream`.

Commande avant correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_dal_boundary_rejects_empty_stream -q

Sortie brute :

    F                                                                        [100%]
    =================================== FAILURES ===================================
    ___________ CoreContractTests.test_dal_boundary_rejects_empty_stream ___________
    tests/test_core_contracts.py:279: in test_dal_boundary_rejects_empty_stream
        with self.assertRaisesRegex(HandoffContractError, "stream must not be empty"):
    E   AssertionError: HandoffContractError not raised
    =========================== short test summary info ============================
    FAILED tests/test_core_contracts.py::CoreContractTests::test_dal_boundary_rejects_empty_stream

Correction : la frontière DAL lève désormais `HandoffContractError` lorsque `len(stream) == 0`.

Commandes après correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_dal_boundary_rejects_empty_stream -q
    .venv/bin/python -m pytest -q

Sorties brutes :

    .                                                                        [100%]
    .............................................                            [100%]
