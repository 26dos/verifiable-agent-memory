"""onchain_memory — SDK for committing agent reasoning traces on-chain."""

__version__ = "0.4.0"

from .client import MemoryClient
from .batch_client import BatchClient
from .schema import Trace, InputSnapshot, ReasoningStep, Decision
from .hash import trace_hash, input_digest, canonicalize
from .merkle import merkle_root, merkle_proof


__all__ = [
    "MemoryClient",
    "BatchClient",
    "Trace",
    "InputSnapshot",
    "ReasoningStep",
    "Decision",
    "trace_hash",
    "input_digest",
    "canonicalize",
    "merkle_root",
    "merkle_proof",
]
