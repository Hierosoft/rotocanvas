#!/usr/bin/env python3

from diffimage import run as run_cli

diff = run_cli("test_diff_base.png", "test_diff_head.png", "tmp.png")
assert diff['same'] is False
print("All tests passed.")
