"""The Turning Point Project: research software.

Modules are dataset-agnostic: dataset-specific variable identifiers live in YAML
mappings under ``config/`` and are filled in only after they are verified against
the official codebook (see ``docs/variable_dictionary.md``).

Nothing in this package fabricates research observations. Synthetic data are
generated only inside ``tests/`` for software testing and are labelled as such.
"""

__version__ = "0.1.0"
