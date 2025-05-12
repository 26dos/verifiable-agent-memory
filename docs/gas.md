# Gas costs

Measured on `forge test --gas-report`, optimizer 200 runs, solc 0.8.24,
local anvil chain.

| Function                                  | Gas (median) |
|-------------------------------------------|-------------:|
| `AgentRegistry.register`                  |        ~78k  |
| `AgentRegistry.deactivate`                |        ~31k  |
| `MemoryAttestor.attest` (first call)      |       ~115k  |
| `MemoryAttestor.attest` (subsequent)      |        ~76k  |
| `BatchAttestor.attestBatch`               |        ~74k  |
| `BatchAttestor.verifyInclusion` (depth 5) |        ~12k  |

The first `attest` for an agent is more expensive because it sets the slot
for `nextIndex[agentId]`. After that it's a warm SSTORE.

The break-even point between per-trace `attest` and `attestBatch` is around
**4 traces**: at 4+ traces in a batch, the merkle root is cheaper. Below
that, just call `attest` directly.
