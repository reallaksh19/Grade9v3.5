"""TEST declares a contract but has no adapter behind it, on purpose.

TEST is a sandbox subject for stress runs (see TEST/README.md). It has no scenes and no validators, so it
deliberately has no `load()`: subject checks read that as CONTRACT_ONLY and report it, which is more
honest than an adapter that imports but cannot compute.
"""
