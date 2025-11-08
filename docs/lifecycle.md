# Attestation lifecycle

```
                 (off-chain)                       (on-chain)
                 ┌─────────┐                       ┌──────────┐
   inputs  ─────▶│ agent   │── trace ──hash──────▶ │ Attestor │
   model   ─────▶│         │                        │  contract │
                 └─────────┘                       └──────────┘
                      │                                  │
                      ▼                                  ▼
                 store trace                       emit Attested(...)
                 (S3 / IPFS / local)               with (traceHash, inputDigest)
```

## Producer side

1. Agent makes a decision; produce a `Trace` (see `sdk/onchain_memory/schema.py`).
2. Compute `trace_hash(trace)` and `input_digest(trace.input)`.
3. Call `MemoryAttestor.attest(agentId, traceHash, inputDigest, modelVersion)`.
4. Persist the full trace anywhere durable.

## Consumer side

1. Receive a trace from somebody (the agent operator, an aggregator, etc.).
2. Look up `attestations[agentId][index]` on chain.
3. Re-hash the received trace; compare to `traceHash`.
4. If they match, the trace really is what the agent committed to.
5. Re-hash the `input` portion; compare to `inputDigest` (gives a second
   verification path).

## Why two hashes?

`traceHash` covers everything: input, reasoning, decision. It's the
authoritative identity of the trace.

`inputDigest` covers only the input snapshot. It's there because some
consumers care about "what did the agent see?" without needing the full
reasoning trace — e.g., for replaying the same input through a different
model.



## When to batch

Use `MemoryAttestor.attest` (single) when:
  - You make ≤ 3 decisions per minute on the chain you're committing to.
  - You need each decision to land in a specific block (e.g. for ordering).

Use `BatchAttestor.attestBatch` (merkle) when:
  - You make many small decisions and only need eventual auditability.
  - You can tolerate a delay between decision and on-chain commitment.
  - Gas is precious — see `docs/gas.md` for the break-even point.

## A word on retention

The on-chain hash is forever (cheap). The off-chain trace is your
responsibility. We recommend:
  - Producer-side: store traces in append-only storage (S3 with object lock,
    IPFS pin, etc.) keyed by trace_hash.
  - Public consumer: any third party who wants to verify a trace must
    hold their own copy of the trace, or trust an aggregator.
