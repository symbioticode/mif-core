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

## C2 — Ruff comme barrière CI

État avant correction (commande baseline) :

    .venv/bin/python -m ruff check core tests examples

Sortie brute synthétique de Ruff :

    Found 35 errors.
    [*] 20 fixable with the `--fix` option.

La CI exécute désormais `ruff check`; les familles `E4`, `E7`, `E9`, `F`, `I`, `UP`, `RUF`, `BLE` et `TRY` sont sélectionnées explicitement.

Précision : seules les règles auditables utiles de ces deux dernières familles sont activées (`BLE001` et `TRY004`), afin de corriger les 35 constats sans imposer une refonte hors périmètre. Les captures `Exception` sont conservées aux frontières d'extension, commentées et annotées : leur contrat exige de convertir toute défaillance d'un adaptateur en preuve FAIL déterministe.

Commandes après correction :

    .venv/bin/python -m ruff check core tests examples
    .venv/bin/python -m ruff format --check core tests examples
    .venv/bin/python -m pytest -q
    .venv/bin/python -m mypy core tests

Sorties brutes :

    All checks passed!
    27 files already formatted
    ...............................................                          [100%]
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

## B1 — Résultat de test non dictionnaire

Test ajouté : `CoreContractTests.test_non_mapping_test_result_becomes_explicit_failure`.

Commande avant correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_non_mapping_test_result_becomes_explicit_failure -q

Sortie brute :

    F                                                                        [100%]
    =================================== FAILURES ===================================
    ___ CoreContractTests.test_non_mapping_test_result_becomes_explicit_failure ____
    tests/test_core_contracts.py:321: in test_non_mapping_test_result_becomes_explicit_failure
        report = Certifier(catalog).certify(
    core/certification/certifier.py:48: in certify
        passed=result.get("passed", False) is True,
               ^^^^^^^^^^
    E   AttributeError: 'int' object has no attribute 'get'
    =========================== short test summary info ============================
    FAILED tests/test_core_contracts.py::CoreContractTests::test_non_mapping_test_result_becomes_explicit_failure

Correction : tout retour non dictionnaire est normalisé en résultat FAIL et son type réel est conservé dans le diagnostic.

Commandes après correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_non_mapping_test_result_becomes_explicit_failure -q
    .venv/bin/python -m pytest -q

Sorties brutes :

    .                                                                        [100%]
    ..............................................                           [100%]

## B2 — Sérialisation robuste des détails arbitraires

Test ajouté : `CoreContractTests.test_certification_report_serializes_arbitrary_details_as_repr`.

Commande avant correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_certification_report_serializes_arbitrary_details_as_repr -q

Sortie brute :

    F                                                                        [100%]
    =================================== FAILURES ===================================
    _ CoreContractTests.test_certification_report_serializes_arbitrary_details_as_repr _
    tests/test_core_contracts.py:365: in test_certification_report_serializes_arbitrary_details_as_repr
        json.loads(report.to_json())["tests_run"]["T_OPAQUE"]["details"][
    core/certification/report.py:37: in to_json
        return json.dumps(self.to_dict(), sort_keys=True)
    E   TypeError: Object of type OpaqueDetail is not JSON serializable
    =========================== short test summary info ============================
    FAILED tests/test_core_contracts.py::CoreContractTests::test_certification_report_serializes_arbitrary_details_as_repr

Correction : les deux rendus utilisent le mécanisme standard `json.dumps(default=repr)` pour dégrader uniquement les objets non sérialisables en texte.

Commandes après correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_certification_report_serializes_arbitrary_details_as_repr -q
    .venv/bin/python -m pytest -q

Sorties brutes :

    .                                                                        [100%]
    ...............................................                          [100%]

## C1 — Types d'exception des métadonnées et politiques

Contrat testé : mauvais type → `TypeError`; valeur du bon type mais invalide → `ValueError`.

Commande avant correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_metadata_rejects_unknown_frequency tests/test_core_contracts.py::CoreContractTests::test_criteria_policy_is_validated_and_injectable -q

Sortie brute :

    FF                                                                       [100%]
    =================================== FAILURES ===================================
    __________ CoreContractTests.test_metadata_rejects_unknown_frequency ___________
    core/strategy/metadata.py:21: in __post_init__
        raise ValueError("strategy identity fields must be non-empty strings")
    E   ValueError: strategy identity fields must be non-empty strings
    ______ CoreContractTests.test_criteria_policy_is_validated_and_injectable ______
    core/testing/policy.py:26: in __post_init__
        raise ValueError(f"{name} must be numeric")
    E   ValueError: default_positive_rate must be numeric
    =========================== short test summary info ============================
    FAILED tests/test_core_contracts.py::CoreContractTests::test_metadata_rejects_unknown_frequency
    FAILED tests/test_core_contracts.py::CoreContractTests::test_criteria_policy_is_validated_and_injectable

Correction : les validations séparent désormais le type de la valeur dans les trois contrats publics; l'évolution est inscrite au changelog.

Commandes après correction :

    .venv/bin/python -m pytest tests/test_core_contracts.py::CoreContractTests::test_metadata_rejects_unknown_frequency tests/test_core_contracts.py::CoreContractTests::test_criteria_policy_is_validated_and_injectable -q
    .venv/bin/python -m pytest -q
    .venv/bin/python -m mypy core tests

Sorties brutes :

    ..                                                                       [100%]
    ...............................................                          [100%]
    Success: no issues found in 25 source files
