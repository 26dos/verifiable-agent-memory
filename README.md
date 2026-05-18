# verifiable-agent-memory

Verifiable trace registry for AI agent decisions.

This repo explores a lightweight audit layer for autonomous agents: store a
compact commitment to an agent's decision trace, keep the full trace off-chain,
and let reviewers verify later that the trace matches the committed record.

The implementation uses Solidity contracts plus a Python SDK, but the systems
question is about agent observability: what evidence should exist after an
agent takes an important action?

## What It Demonstrates

- **Trace commitments**: publish `keccak256(trace)` plus metadata instead of
  storing full reasoning traces directly.
- **Agent identity registry**: map agent ids to operator accounts.
- **Single and batched attestations**: support per-decision records and
  Merkle-root commitments for higher-volume agents.
- **Python producer/verifier SDK**: publish traces from agent code and verify
  trace integrity later.
- **Lifecycle docs**: define how traces move from generation to storage,
  commitment, retrieval, and verification.

## Architecture

```
agent runtime
    |
    v
trace schema
    |
    +--> off-chain trace store
    |
    v
trace hash + metadata
    |
    v
attestation contracts
    |
    v
verifier SDK / audit workflow
```

## Install

Contracts:

```bash
forge build
```

Python SDK:

```bash
cd sdk
pip install -e .
```

## Usage

Producer side:

```python
from onchain_memory import MemoryClient, Trace, InputSnapshot, Decision, ReasoningStep

trace = Trace(
    agent_id="risk-agent/v1",
    model_id="claude-sonnet-4-6",
    input=InputSnapshot(prices={"ETH": 2050.0}),
    steps=[ReasoningStep(role="model", content="...")],
    decision=Decision(kind="rebalance", params={"size_usd": 100}),
)

client = MemoryClient(rpc_url=..., attestor_address=..., private_key=...)
receipt = client.publish(trace, reason_code="scheduled_rebalance")
```

Verifier side:

```python
client = MemoryClient(rpc_url=..., attestor_address=...)
result = client.verify(trace, on_chain_index=42)
assert result["match"]
```

## Contracts

| Contract | Purpose |
| --- | --- |
| `AgentRegistry` | Maps agent ids to operator accounts |
| `MemoryAttestor` | Per-decision attestations indexed by `(agentId, idx)` |
| `BatchAttestor` | Merkle-root commitments for high-volume agents |

Gas costs and the batch-vs-single tradeoff are documented in
[docs/gas.md](docs/gas.md). The attestation lifecycle is documented in
[docs/lifecycle.md](docs/lifecycle.md).

## Why This Belongs Near Agent Evaluation Work

Evaluation tells you how an agent behaves before deployment. Trace attestation
helps preserve evidence about what an agent saw and decided after deployment.
Together they support a more inspectable agent lifecycle:

1. evaluate behavior against labeled cases
2. deploy with constrained tools and structured outputs
3. commit to decision traces for later review
4. verify that the reviewed trace matches the committed record

## License

BSD-3-Clause. See [LICENSE](LICENSE).
