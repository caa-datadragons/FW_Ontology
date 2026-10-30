#!/usr/bin/env python3
"""Build the whole documentation of the FW ontology: ``python main.py``.

    python main.py                     all steps, in order
    python main.py --list              print the steps and exit
    python main.py --only guide        one step
    python main.py --from guide        this step and all after it
    python main.py --skip ontology     all but this step
    python main.py --dry-run           print the plan, run nothing
    python main.py --strict            warnings of the reference become errors (what CI could use)

Steps (each one is also a script that runs on its own):

    ontology   py/build_docs.py    pyLODE reference of the ontology           -> _site/
    guide      py/build_guide.py   figures + the pages in docs/               -> _site/guide/

The output folder ``_site/`` is generated and not committed. Nothing in it carries a date.
Needs Python 3.11 or newer (pyLODE); ``pip install -r requirements-docs.txt``.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = ROOT / "py"

STEPS: list[tuple[str, str, list[str]]] = [  # (name, description, command after the interpreter)
    ("ontology", "reference of the ontology", [str(PY / "build_docs.py")]),
    ("guide", "figures and guide pages", [str(PY / "build_guide.py")]),
]


def select(args: argparse.Namespace) -> list[tuple[str, str, list[str]]]:
    names = [s[0] for s in STEPS]
    for given in [args.only, args.from_, *args.skip]:
        if given and given not in names:
            raise SystemExit(f"unknown step {given!r}; known: {', '.join(names)}")
    chosen = STEPS
    if args.only:
        chosen = [s for s in chosen if s[0] == args.only]
    if args.from_:
        chosen = chosen[names.index(args.from_):]
    return [s for s in chosen if s[0] not in args.skip]


def run_step(name: str, cmd: list[str], strict: bool) -> tuple[int, float]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    command = [sys.executable, *cmd]
    if strict and name == "ontology":
        command.append("--strict")
    start = time.perf_counter()
    proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    assert proc.stdout is not None
    for line in proc.stdout:
        # pyLODE logs at INFO/DEBUG level; they say nothing about the result
        if not line.startswith(("INFO:", "DEBUG:")):
            print("   " + line.rstrip())
    return proc.wait(), time.perf_counter() - start


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="print the steps and exit")
    ap.add_argument("--only", metavar="STEP")
    ap.add_argument("--from", dest="from_", metavar="STEP")
    ap.add_argument("--skip", action="append", default=[], metavar="STEP")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for name, text, _ in STEPS:
            print(f"{name:<10} {text}")
        return 0

    plan = select(args)
    if args.dry_run:
        for name, text, cmd in plan:
            print(f"{name:<10} {text}\n           python {' '.join(Path(c).name if os.sep in c else c for c in cmd)}")
        return 0

    timings: list[tuple[str, float]] = []
    for name, text, cmd in plan:
        print(f"== {name}: {text}")
        code, seconds = run_step(name, cmd, args.strict)
        timings.append((name, seconds))
        if code != 0:
            print(f"ERROR  step {name} failed (exit code {code})")
            return code
    total = sum(t for _, t in timings) or 1.0
    print("\nstep        seconds   share")
    for name, seconds in timings:
        print(f"{name:<10} {seconds:8.1f}  {100 * seconds / total:4.0f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
