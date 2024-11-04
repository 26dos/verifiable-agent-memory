<div align="center">

# onchain-agent-memory

**Cryptographic attestation registry for AI agent reasoning traces.**

![Solidity](https://img.shields.io/badge/Solidity-0.8.24-363636?style=for-the-badge&logo=solidity&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue?style=for-the-badge)

[Install](#install) · [Usage](#usage) · [Lifecycle](docs/lifecycle.md) · [Contracts](#contracts)

</div>

---

## Why?

Autonomous agents are starting to take real economic actions on-chain. When
something goes wrong (a bad trade, a failed liquidation, a contested vote),
there's no canonical record of what the agent *actually believed* when it
acted. This repo gives agents a way to commit to their reasoning trace
on-chain, in O(1) gas, so a verifiable record exists later.

The contracts are deliberately minimal: they store `keccak256(trace)` plus
metadata. The trace itself lives off-chain (S3, IPFS, the operator's
database — whatever works). Anyone holding a trace can prove it really is
what the agent committed to.

## Install

```bash
# contracts (foundry)
forge build

# python sdk
cd sdk
pip install -e .
```

## Usage

Producer (agent side):

```python
from onchain_memory.client import MemoryClient
from onchain_memory.schema import Trace, InputSnapshot, Decision, ReasoningStep

trace = Trace(
    agent_id="my/trader-v1",
    model_id="claude-sonnet-4-5",
    input=InputSnapshot(prices={"ETH": 2050.0}),
    steps=[ReasoningStep(role="model", content="...")],
    decision=Decision(kind="buy", params={"size_usd": 100}),
)

client = MemoryClient(rpc_url=..., attestor_address=..., private_key=...)
receipt = client.publish(trace)
# {"tx_hash": "0x...", "trace_hash": "0x...", "block": 19500001}
```

Consumer (verifier side):

```python
client = MemoryClient(rpc_url=..., attestor_address=...)
on_chain = client.read("my/trader-v1", index=0)
# Now reconstruct the trace however you got it (gossip, API, database)
# and call client.verify(trace, on_chain_index=0).
```

## Contracts

| Contract            | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `AgentRegistry`     | Maps agent ids to operator EOAs. Identity layer.       |
| `MemoryAttestor`    | Per-decision attestations. Indexed by `(agentId, idx)`.|
| `BatchAttestor`     | Merkle-root commitments for high-volume agents.        |

## License

BSD-3-Clause. See [LICENSE](LICENSE).
