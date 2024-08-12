"""Canonical hashing for off-chain agent traces.

The chain stores `keccak256(canonical(trace))`. To verify off-chain, the
verifier re-canonicalizes their copy of the trace and re-hashes it. Two
ways to canonicalize:

  1. JSON with sorted keys + no whitespace + UTF-8.
  2. RLP. Faster to verify on-chain but harder to debug; we use (1) for now.
"""
import json
from hashlib import sha3_256

from eth_utils import keccak


def canonicalize(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def trace_hash(trace) -> bytes:
    """Return keccak256(canonical(trace)) — matches the on-chain digest."""
    return keccak(canonicalize(trace))


def input_digest(snapshot) -> bytes:
    """Hash of the input snapshot (prices, position, etc.) at decision time."""
    return keccak(canonicalize(snapshot))
