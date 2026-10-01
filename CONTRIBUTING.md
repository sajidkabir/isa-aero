# Contributing

Contributions are welcome: bug reports, physics corrections, new models,
documentation, and examples. This project aims to stay small, readable, and
honest about its assumptions.

## Getting set up

```bash
git clone https://github.com/sajidkabir/isa-aero.git
cd isa-aero
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest -q
```

All 18 tests should pass before you change anything.

## Making a change

1. Fork the repository and create a branch from `main`
   (`git checkout -b feature/short-name`).
2. Keep the change focused. One model, one fix, or one feature per pull
   request.
3. Add or update tests. Physics changes need a sanity check against a
   published reference, such as the ISA tables, or a hand-computed value,
   and the test should say which.
4. Run `pytest -q` and make sure it is green.
5. Update the README, the docstrings, and `CHANGELOG.md` (Unreleased
   section) if behavior or numbers change.
6. Open a pull request against `main` describing what changed, why, and
   what it does to the validated table values.

## Ground rules

- No silent changes to validated numbers. If a fix moves a result, say so
  in the pull request and in the changelog.
- Prefer explicit physics over clever code. A reviewer should be able to
  check each formula against its source.
- Keep the core in SI units and free of dependencies. Convenience wrappers
  belong at the edges, not in the model.
- New assumptions go in the README limitations list until they are modeled.

## Reporting issues

Open an issue with the altitude or configuration, the command or code you
ran, the output you got, and the output you expected. A minimal reproducing
example is worth more than a long description.
