"""Client for reading/writing agent attestations on-chain."""
import os
from pathlib import Path

from web3 import Web3
from eth_account import Account
from eth_utils import keccak

from .hash import trace_hash, input_digest, canonicalize
from .schema import Trace


ATTESTOR_ABI = [
    {
        "inputs": [
            {"name": "agentId", "type": "bytes32"},
            {"name": "traceHash", "type": "bytes32"},
            {"name": "inputDigest", "type": "bytes32"},
            {"name": "modelVersion", "type": "uint32"},
            {"name": "reasonCode", "type": "bytes32"},
        ],
        "name": "attest",
        "outputs": [{"name": "index", "type": "uint64"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "agentId", "type": "bytes32"},
            {"name": "index", "type": "uint64"},
        ],
        "name": "attestations",
        "outputs": [
            {"name": "traceHash", "type": "bytes32"},
            {"name": "inputDigest", "type": "bytes32"},
            {"name": "timestamp", "type": "uint64"},
            {"name": "modelVersion", "type": "uint32"},
            {"name": "reasonCode", "type": "bytes32"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


def _to_bytes32(s) -> bytes:
    if isinstance(s, bytes):
        return s.rjust(32, b"\x00")
    return Web3.keccak(text=s)


class MemoryClient:
    def __init__(self, rpc_url: str, attestor_address: str, private_key: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(attestor_address), abi=ATTESTOR_ABI,
        )
        self.account = Account.from_key(private_key) if private_key else None

    def publish(self, trace: Trace, reason_code: str = "") -> dict:
        if self.account is None:
            raise ValueError("private_key required to publish")
        agent_id = _to_bytes32(trace.agent_id)
        d = trace.to_dict()
        th = trace_hash(d)
        idg = input_digest(d["input"])
        rc = _to_bytes32(reason_code) if reason_code else b"\x00" * 32

        tx = self.contract.functions.attest(
            agent_id, th, idg, int(trace.model_version), rc,
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "gas": 250_000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return {
            "tx_hash": tx_hash.hex(),
            "trace_hash": th.hex(),
            "input_digest": idg.hex(),
            "block": receipt.blockNumber,
        }

    def read(self, agent_id: str, index: int) -> dict:
        a = _to_bytes32(agent_id)
        th, idg, ts, mv, rc = self.contract.functions.attestations(a, index).call()
        return {
            "trace_hash": "0x" + th.hex(),
            "input_digest": "0x" + idg.hex(),
            "timestamp": ts,
            "model_version": mv,
            "reason_code": "0x" + rc.hex(),
        }

    def verify(self, trace: Trace, on_chain_index: int) -> dict:
        d = trace.to_dict()
        local_hash = "0x" + trace_hash(d).hex()
        local_digest = "0x" + input_digest(d["input"]).hex()
        on_chain = self.read(trace.agent_id, on_chain_index)
        return {
            "match": (local_hash == on_chain["trace_hash"]
                      and local_digest == on_chain["input_digest"]),
            "local_trace_hash": local_hash,
            "on_chain_trace_hash": on_chain["trace_hash"],
            "local_input_digest": local_digest,
            "on_chain_input_digest": on_chain["input_digest"],
        }



    def estimate_gas(self, trace: Trace, reason_code: str = "") -> int:
        """Estimate gas for an attestation; useful for budgeting agents."""
        agent_id = _to_bytes32(trace.agent_id)
        d = trace.to_dict()
        th = trace_hash(d)
        idg = input_digest(d["input"])
        rc = _to_bytes32(reason_code) if reason_code else b"\x00" * 32
        return int(self.contract.functions.attest(
            agent_id, th, idg, int(trace.model_version), rc,
        ).estimate_gas({"from": self.account.address if self.account else None}))
