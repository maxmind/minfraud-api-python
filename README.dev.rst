Steps for doing a release:

1. Make a release branch
2. Review open issues and PRs to see if any can easily be fixed, closed, or
   merged.
3. Bump copyright year in ``README.rst``, ``docs/conf.py``, and
   ``docs/index.rst``, if necessary.
4. Review ``HISTORY.rst`` for completeness and correctness.
5. Add release date to ``HISTORY.rst``.
6. Install or update `gh <https://github.com/cli/cli>`_ as it used by the
   release script.
7. Run ``dev-bin/release.sh`` and follow the prompts.
8. Verify the release on `GitHub <https://github.com/maxmind/minfraud-api-python/releases>`_
   and `PyPI <https://pypi.python.org/pypi/minfraud>`_.
