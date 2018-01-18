Steps for doing a release:

1. Review open issues and PRs to see if any can easily be fixed, closed, or
   merged.
2. Bump copyright year in ``README.rst``, ``docs/conf.py``, and
   ``docs/index.rst``, if necessary.
3. Review ``HISTORY.rst`` for completeness and correctness.
4. Add release date to ``HISTORY.rst``.
5. Install or update `hub <https://github.com/github/hub`_ as it used by the
   release script.
6. Run ``dev-bin/release.sh`` and follow the prompts.
7. Verify the release on `GitHub <https://github.com/maxmind/minfraud-api-python/releases>`_
   and `PyPI <https://pypi.python.org/pypi/minfraud>`_.
