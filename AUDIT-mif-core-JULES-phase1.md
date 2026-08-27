# Rapport d'Audit Indépendant — Phase 1 (`mif-core`)

**Auditeur :** JULES
**Dépôt audité :** `symbioticode/mif-core`
**Commit/Tag examiné :** Commit `dfb1ab9943d78f60101cb1f903def82b17edc36d` (Tag `v0.1.0`)
**Date d'audit :** 6 mars 2026

---

## 1. Périmètre exact examiné

L'audit de Phase 1 a porté exclusivement sur le dépôt `symbioticode/mif-core` à la racine et ses sous-dossiers :
- Fichiers de configuration et métadonnées : `pyproject.toml`, `LICENSE`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`.
- Documentation : `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/PROVENANCE.md`, `docs/PUBLISHING.md`, `docs/ROADMAP.md`.
- Code source Python (`core/`) : `core/__init__.py`, `core/cli.py`, `core/py.typed`, `core/certification/*`, `core/integrations/*`, `core/metric/*`, `core/strategy/*`, `core/testing/*`.
- Exemples exécutables (`examples/`) : `examples/certify_metric.py`, `examples/certify_strategy.py`.
- Suite de tests (`tests/`) : `tests/test_core_contracts.py`, `tests/test_dal_integration.py`.
- Workflows d'intégration continue (`.github/workflows/`) : `ci.yml`, `publish.yml`.

---

## 2. Constats par catégorie

### Catégorie 1 — Conformité au premier contact

#### Constat 1.1 : L'installation en mode éditable et l'utilisation des imports publics fonctionnent conformément à la documentation
- **Preuve directe (Commande & Sortie) :**
  ```bash
  $ pip install -e .
  Successfully built mif-foundation
  Successfully installed mif-dal-0.2.0 mif-dqf-1.3.0 mif-foundation-0.1.0 ...
  ```
  ```python
  from core import Certifier, StrategyAdapter, MetricAdapter, default_catalog
  ```
  *Résultat :* Importation réussie sans erreur.

#### Constat 1.2 : Toutes les commandes CLI documentées s'exécutent sans erreur et produisent le format attendu
- **Preuve directe (Commandes & Sorties brutes) :**
  - `mif-core --version`
    ```
    0.1.0
    ```
  - `mif-core catalog`
    ```
    T_HANDOFF_001	integration	DAL handoff readiness
    T_SIGNAL_SHAPE_001	strategy	Signal shape
    T_STABILITY_001	stability	Adaptive positive-return stability
    T_RETURN_INTEGRITY_001	data_quality	Backtest return integrity
    T_WALK_FORWARD_001	stability	Out-of-sample consistency
    T_LOOKAHEAD_001	indicator	Prefix causality
    ```
  - `mif-core demo` (Extrait sortie JSON) :
    ```json
    {
      "status": "PASS",
      "strategy_name": "demo",
      "tier": "S",
      "validity_domain": { ... }
    }
    ```
  - `mif-core demo --format text` (Extrait sortie texte) :
    ```
    Strategy: demo
    Status: PASS  Tier: S
    ...
    ```
  - `mif-core demo --tests T_HANDOFF_001,T_LOOKAHEAD_001` (Exécute uniquement les 2 tests spécifiés).

#### Constat 1.3 : Les scripts d'exemple s'exécutent sans erreur
- **Preuve directe (Commande & Sortie) :**
  - `python3 examples/certify_strategy.py`
    ```
    {'strategy_name': 'example-strategy', 'status': 'PASS', 'tests_run': {...}, 'tier': 'S'}
    ```
  - `python3 examples/certify_metric.py`
    ```
    {'schema_version': 1, 'metric_name': 'mean-return', 'metric_version': '0.1.0', 'status': 'PASS', ...}
    ```

---

### Catégorie 2 — Tenue des frontières avec les dépendances réelles

#### Constat 2.1 : L'intégration avec le paquet réel `mif-dal` est testée directement contre la classe canonique `DALHandoff`
- **Preuve directe (Code & Commande) :**
  - Fichier `tests/test_dal_integration.py` :
    ```python
    from dal.core.handoff import DALHandoff
    ...
    def test_canonical_handoff_passes_core_boundary(self):
        handoff = self.make_handoff()
        validate_dal_handoff(handoff)
        self.assertEqual(handoff.asset_id, "TEST-USD")
    ```
  - Exécution du test d'intégration avec `mif-dal` 0.2.0 réellement installé :
    ```bash
    $ python3 -m unittest tests/test_dal_integration.py
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.005s
    OK
    ```
  - Module `dal` installé sur l'environnement :
    `/home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages/dal/__init__.py` (version 0.2.0 de `mif-dal`, dépendant de `mif-dqf` 1.3.0).

#### Constat 2.2 : La validation de frontière `validate_dal_handoff` n'importe pas `mif-dal` à l'exécution mais applique un contrat strict par introspection de surface
- **Preuve directe (Code `core/integrations/dal.py`) :**
  Le fichier `core/integrations/dal.py` vérifie les attributs requis (`stream`, `asset_id`, `calendar`, `assembly_hash`, `handoff_timestamp`, `dal_version`, `source_manifest`, `coverage`, `dqf_status`, `dqf_mpi`, `dqf_version`, `dqf_report`, `aqi`), la présence de la méthode `__len__` sur `stream`, les valeurs permises pour `dqf_status` (`PASS`, `WARNING`), et la finitude numérique de `aqi` et `dqf_mpi` dans `[0.0, 100.0]`.

---

### Catégorie 3 — Cohérence entre ce qui est déclaré et ce qui est réel

#### Constat 3.1 : Cohérence des métadonnées de version interne
- **Preuve directe :**
  - `pyproject.toml` : `version = "0.1.0"`
  - Tag Git : `v0.1.0`
  - `mif-core --version` : `0.1.0`
  - `core.__version__` : `"0.1.0"`
  - `CHANGELOG.md` : Documente la version `0.1.0` et une section `Unreleased`.

#### Constat 3.2 : Incompatibilité déclarée avec Python 3.13 et restriction effective dans le projet
- **Preuve directe :**
  - `pyproject.toml` : `requires-python = ">=3.11,<3.13"`
  - Documentation (`README.md`, `docs/PUBLISHING.md`) : Déclare explicitement que Python 3.13 est différé en raison de la contrainte NumPy / `mif-dal`.

#### Constat 3.3 : Nom du paquet PyPI (`mif-foundation`) vs Nom du dépôt (`mif-core`)
- **Preuve directe :**
  - `pyproject.toml` : `name = "mif-foundation"`
  - `README.md` et `docs/PUBLISHING.md` affirment que le nom du projet PyPI est `mif-foundation`.
  - Vérification PyPI : Aucun paquet n'est encore publié sous le nom `mif-core` ni `mif-foundation` sur PyPI (`curl -s https://pypi.org/pypi/mif-core/json` et `curl -s https://pypi.org/pypi/mif-foundation/json` renvoient tous deux `{"message": "Not Found"}`).

---

### Catégorie 4 — Chemins d'échec silencieux

#### Constat 4.1 : Absence d'échec silencieux lors d'exceptions levées par les stratégies ou métriques
- **Preuve directe (Code `core/testing/builtin.py`, `core/certification/certifier.py`, `core/metric/certifier.py`) :**
  Toutes les fonctions de test et les certificateurs interceptent les exceptions levées par le code utilisateur (`strategy.calculate_signals`, `strategy.backtest`, `metric.calculate`) et renvoient un résultat explicite `passed: False` ou `status: FAIL` avec le détail de l'erreur dans `details["error"]`.
- **Test associé :** `test_test_exception_becomes_explicit_failure` et `test_metric_exception_preserves_validity_domain` dans `tests/test_core_contracts.py` confirment ce comportement.

#### Constat 4.2 : Rejet explicite des données non numériques, infinis ou NaNs dans les rendements et métriques
- **Preuve directe :**
  - `_return_integrity`, `_adaptive_stability`, et `_walk_forward_consistency` valident que chaque rendement est un nombre réel fini (`isinstance(v, Real)` et `math.isfinite(v)` et pas un `bool`).
  - `MetricCertifier` rejette les valeurs non finies ou non numériques dans les séries ou scalaires.

#### Constat 4.3 : Protection contre la sélection de tests vides ou en double
- **Preuve directe (`core/certification/certifier.py`) :**
  - `test_ids` vide -> `ValueError("at least one test must be selected")`
  - `test_ids` avec éléments vides -> `ValueError("test IDs must be non-empty")`
  - `test_ids` contenant des doublons -> `ValueError("test IDs must be unique")`

---

### Catégorie 5 — Fiabilité du pipeline de qualité lui-même

#### Constat 5.1 : La couverture de tests automatique (pytest-cov) dépasse le seuil exigé de 90%
- **Preuve directe (Commande & Sortie) :**
  ```bash
  $ python -m pytest --cov=core --cov-report=term-missing --cov-fail-under=90
  43 passed in 2.75s
  Required test coverage of 90% reached. Total coverage: 93.20%
  ```

#### Constat 5.2 : Le vérificateur de types `mypy` valide l'intégralité du code sans erreur
- **Preuve directe (Commande & Sortie) :**
  ```bash
  $ python -m mypy core tests
  Success: no issues found in 25 source files
  ```

#### Constat 5.3 : Écart entre les vérifications linter locales (`ruff check`) et les vérifications en CI (`.github/workflows/ci.yml`)
- **Preuve directe :**
  - Le fichier `.github/workflows/ci.yml` exécute la vérification de formatage :
    `python -m ruff format --check core tests examples`
    (qui passe avec la sortie `27 files already formatted`).
  - Cependant, `.github/workflows/ci.yml` N'EXÉCUTE PAS la vérification des règles de linting (`ruff check`).
  - Lorsque `ruff check .` est exécuté localement, **35 avertissements/erreurs de linting** sont identifiés (dont réorganisation des imports `I001`, dépréciations `typing.Dict` -> `UP006`/`UP035`, exceptions aveugles `BLE001`, alias de fuseau horaire `UP017`).

---

## 3. Ce qui n'a pas pu être vérifié et pourquoi

1. **Publication effective sur PyPI (`mif-foundation`) via GitHub Actions OIDC :**
   - *Raison :* Le dépôt sandbox n'a pas accès aux secrets OIDC GitHub ni aux autorisations de publication en production PyPI.
2. **Exécution native sous Python 3.11 :**
   - *Raison :* L'environnement de la sandbox dispose de Python 3.12.13. L'exécution sous Python 3.11 est vérifiée par la matrice CI GitHub Actions, mais n'a pas pu être exécutée localement dans cette session.

---

## 4. Critères de succès mesurables (États cibles sans préconisation d'implémentation)

- **Critère C-1 (Pipeline CI - Linting) :** La commande `python -m ruff check core tests examples` s'exécute avec une sortie brute de 0 erreur/avertissement et est intégrée comme étape obligatoire dans `.github/workflows/ci.yml`.
- **Critère C-2 (Publication PyPI) :** Une requête `curl -s https://pypi.org/pypi/mif-foundation/json` renvoie un objet JSON valide contenant la version `0.1.0`.
