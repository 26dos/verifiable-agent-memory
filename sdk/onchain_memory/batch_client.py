"""Client for the BatchAttestor contract."""
from web3 import Web3
from eth_account import Account
from eth_utils import keccak

from .merkle import merkle_root, merkle_proof
from .hash import trace_hash
from .schema import Trace


BATCH_ATTESTOR_ABI = [
    {
        "inputs": [
            {"name": "agentId", "type": "bytes32"},
            {"name": "root", "type": "bytes32"},
            {"name": "size", "type": "uint64"},
        ],
        "name": "attestBatch",
        "outputs": [{"name": "index", "type": "uint64"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "agentId", "type": "bytes32"},
            {"name": "batchIndex", "type": "uint64"},
            {"name": "traceHash", "type": "bytes32"},
            {"name": "proof", "type": "bytes32[]"},
        ],
        "name": "verifyInclusion",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class BatchClient:
    def __init__(self, rpc_url: str, batch_attestor_address: str, private_key: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(batch_attestor_address),
            abi=BATCH_ATTESTOR_ABI,
        )
        self.account = Account.from_key(private_key) if private_key else None

    def publish_batch(self, agent_id: str, traces: list[Trace]) -> dict:
        leaves = [trace_hash(t.to_dict()) for t in traces]
        root = merkle_root(leaves)
        agent_id_b = keccak(text=agent_id)
        tx = self.contract.functions.attestBatch(
            agent_id_b, root, len(traces),
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "gas": 200_000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return {
            "tx_hash": tx_hash.hex(),
            "root": "0x" + root.hex(),
            "leaves": ["0x" + l.hex() for l in leaves],
            "block": receipt.blockNumber,
        }

    def proof_for(self, traces: list[Trace], index: int) -> list[str]:
        leaves = [trace_hash(t.to_dict()) for t in traces]
        return ["0x" + p.hex() for p in merkle_proof(leaves, index)]

    def verify(self, agent_id: str, batch_index: int, trace: Trace,
               proof: list[str]) -> bool:
        agent_id_b = keccak(text=agent_id)
        leaf = trace_hash(trace.to_dict())
        proof_b = [bytes.fromhex(p[2:]) if p.startswith("0x") else bytes.fromhex(p)
                   for p in proof]
        return bool(self.contract.functions.verifyInclusion(
            agent_id_b, batch_index, leaf, proof_b,
        ).call())
