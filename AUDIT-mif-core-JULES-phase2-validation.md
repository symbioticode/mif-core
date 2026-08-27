# Rapport de Comparaison et Validation Croisée — Phase 2 (`mif-core`)

**Auditeur :** JULES
**Dépôt audité :** `symbioticode/mif-core`
**Commit/Tag examiné :** Commit `dfb1ab9943d78f60101cb1f903def82b17edc36d` (Tag `v0.1.0`)
**Fichier de référence comparé :** `AUDIT_MIF_CORE_v0.1.0.md` (fourni en Phase 2)
**Date d'audit :** 6 mars 2026

---

## 1. Contexte de la Phase 2

Conformément au protocole d'audit croisé, le rapport d'audit antérieur `AUDIT_MIF_CORE_v0.1.0.md` a été fourni à l'auditeur JULES à l'issue du figeage complet de la Phase 1 (`AUDIT-mif-core-JULES-phase1.md`).

Le présent document réalise la comparaison factuelle entre les constatations de la Phase 1 indépendante à l'aveugle et celles contenues dans `AUDIT_MIF_CORE_v0.1.0.md`, puis recense les défauts additionnels identifiés lors de l'investigation complémentaire de Phase 2.

---

## 2. Tableau de convergence et de comparaison

| Constat / Sujet d'audit | Statut de convergence | Analyse comparative & Équivalence des preuves |
| :--- | :--- | :--- |
| **Constat 1.1 : Installation et imports publics** | **Confirmé indépendamment** | Présent dans les deux rapports. Les deux audits ont validé `pip install -e .` et l'import de `Certifier`, `StrategyAdapter`, `MetricAdapter`, `default_catalog`. |
| **Constat 1.2 : Commandes CLI documentées** | **Confirmé indépendamment** | Présent dans les deux rapports. Validation complète des commandes `mif-core --version`, `catalog`, `demo` (formats JSON et texte, option `--tests`). |
| **Constat 1.3 : Exécution des scripts d'exemple** | **Confirmé indépendamment** | Présent dans les deux rapports. Les scripts `certify_strategy.py` et `certify_metric.py` s'exécutent avec succès dans les deux cas. |
| **Constat 2.1 : Intégration réelle avec `mif-dal`** | **Confirmé indépendamment** | Présent dans les deux rapports. Exécution validée de `test_canonical_handoff_passes_core_boundary` avec le paquet réel `mif-dal` v0.2.0. |
| **Constat 2.2 : Validation de frontière DAL sans import lourd** | **Confirmé indépendamment** | Présent dans les deux rapports. Analyse de la fonction `validate_dal_handoff` (`core/integrations/dal.py`) contrôlant les 13 attributs obligatoires par introspection. |
| **Constat 3.1 : Cohérence de version `0.1.0`** | **Confirmé indépendamment** | Présent dans les deux rapports. Alignement vérifié entre `pyproject.toml`, tag `v0.1.0`, CLI `--version`, et `CHANGELOG.md`. |
| **Constat 3.2 : Restriction et exclusion de Python 3.13** | **Confirmé indépendamment** | Présent dans les deux rapports. Identifié dans `pyproject.toml` (`>=3.11,<3.13`) et documenté dans `README.md`. |
| **Constat 3.3 : Nom de distribution PyPI (`mif-foundation`) vs dépôt (`mif-core`)** | **Confirmé indépendamment** | Présent dans les deux rapports. Nom de paquet `mif-foundation` vérifié non encore publié sur PyPI. |
| **Constat 4.1 : Captures d'exceptions et non-échec silencieux** | **Confirmé indépendamment** | Présent dans les deux rapports. Les exceptions de calcul des stratégies/métriques sont capturées et renvoyées explicitement avec `status: FAIL` et détails. |
| **Constat 4.2 : Rejet des valeurs non numériques, infinis ou NaNs** | **Confirmé indépendamment** | Présent dans les deux rapports. Validation stricte par `isinstance(v, Real)` et `math.isfinite(v)` dans `builtin.py` et `MetricCertifier`. |
| **Constat 4.3 : Protection contre la sélection de tests vides ou doublons** | **Confirmé indépendamment** | Présent dans les deux rapports. Levée explicite de `ValueError` lors de listes vides ou de doublons dans `Certifier`. |
| **Constat 5.1 : Couverture de tests (> 90%)** | **Confirmé indépendamment** | Présent dans les deux rapports. pytest-cov confirme un taux de couverture de 93.20% (supérieur au seuil de 90%). |
| **Constat 5.2 : Validation des types avec mypy** | **Confirmé indépendamment** | Présent dans les deux rapports. `mypy core tests` valide les 25 fichiers sans erreur. |
| **Constat 5.3 : Absence de `ruff check` en CI (Linting non exécuté)** | **Confirmé indépendamment** | Présent dans les deux rapports. Le workflow CI `.github/workflows/ci.yml` n'exécute que `ruff format --check`, ignorant 35 erreurs de linting détectées par `ruff check .`. |

- **Synthèse de la convergence :** 100% des constats de Phase 1 sont **Confirmés indépendamment** par `AUDIT_MIF_CORE_v0.1.0.md`. Aucune divergence factuelle n'a été relevée entre les deux audits.

---

## 3. Défauts additionnels identifiés (non couverts ni par Phase 1 ni par `AUDIT_MIF_CORE_v0.1.0.md`)

Une analyse approfondie spécifique menée en Phase 2 a permis de mettre en évidence les défauts résiduels suivants :

### Catégorie 2 — Tenue des frontières avec les dépendances réelles
- **Défaut 2.A : Absence de vérification sur la taille non nulle du `stream` dans `validate_dal_handoff`**
  - *Preuve directe (`core/integrations/dal.py`) :*
    `validate_dal_handoff` vérifie que `handoff.stream` possède la méthode `__len__`, mais ne vérifie pas que `len(handoff.stream) > 0`. Un `DALHandoff` contenant un DataFrame ou flux vide (`len == 0`) passe la validation de frontière, mais provoque des divisions par zéro ou comportements indéfinis dans les tests downstream.

### Catégorie 4 — Chemins d'échec silencieux
- **Défaut 4.A : Évaluation trompeuse de la causalité (`T_LOOKAHEAD_001`) sur des séries à 1 seule observation**
  - *Preuve directe (`core/testing/builtin.py`, lignes 193–198) :*
    ```python
    stream = handoff.stream
    midpoint = max(1, len(stream) // 2)
    ```
    Si `len(stream) == 1`, `len(stream) // 2` vaut `0`, donc `midpoint` est forcé à `1`. Le sous-flux de préfixe `stream[:1]` est alors strictly identique au flux complet `stream[:1]`. Le test de causalité compare une série de longueur 1 à elle-même, déclarant le test `PASS` sans avoir réellement pu tester l'influence de données futures.
- **Défaut 4.B : Absence de distinction entre rendement nul (`0.0`) et rendement négatif dans `_adaptive_stability`**
  - *Preuve directe (`core/testing/builtin.py`, ligne 82) :*
    `positive_rate = sum(value > 0 for value in returns) / len(returns)`
    Un rendement de `0.0` (ex: absence de position ou période sans trade) est comptabilisé comme un échec de positivité au même titre qu'une perte, sans expliciter cette convention dans la structure `details` du rapport.

### Catégorie 5 — Fiabilité du pipeline de qualité
- **Défaut 5.A : Absence de l'outil `build` dans les dépendances de développement de `pyproject.toml`**
  - *Preuve directe (`pyproject.toml`) :*
    Section `[project.optional-dependencies] dev = ["pytest>=8.0.0", "pytest-cov>=5.0.0", "mypy>=1.9.0", "ruff>=0.4.0"]`.
    Le paquet `build` nécessaire pour exécuter la commande documentée dans `README.md` (`python -m build`) et dans `docs/PUBLISHING.md` n'est pas inclus dans les dépendances `dev`.
- **Défaut 5.B : Configuration mypy non stricte et absente sur les exemples en CI**
  - *Preuve directe (`pyproject.toml` & `.github/workflows/ci.yml`) :*
    Dans `pyproject.toml`, `strict = false` et `ignore_missing_imports = true`. Dans `ci.yml`, `mypy` est exécuté sur `core tests`, mais les fichiers du répertoire `examples/` ne sont pas vérifiés par le type checker.

---

## 4. Synthèse des critères de succès mesurables récapitulatifs

1. **Intégration du Linting CI :** `.github/workflows/ci.yml` exécute `python -m ruff check core tests examples` et `python -m ruff format --check core tests examples`.
2. **Robustesse au flux vide :** Une tentative de passer un `DALHandoff` avec `len(stream) == 0` à `validate_dal_handoff` lève une exception `HandoffContractError`.
3. **Causalité sur flux court :** Le test `T_LOOKAHEAD_001` renvoie `passed: False` ou signale une observation insuffisante dans `details` lorsque `len(stream) < 2`.
4. **Dépendances dev complètes :** `pip install -e '.[dev]'` installe l'outil `build`, rendant la commande `python -m build` utilisable immédiatement dans un environnement virtuel propre.
