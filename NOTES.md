# notes

agents are doing real economic actions on-chain (trading, liquidating, voting).
when one of them does something stupid (or worse, malicious), there's no
way to look back and say "given the inputs at the time, what did the agent
think it was doing?".

idea: agents publish a *commitment* on-chain when they make a decision.
the commitment is a hash of:
  - input snapshot (prices, position state)
  - reasoning trace (or a hash of it, if too big)
  - model id + version
  - decision (the action taken)

on-chain: tiny, gas-cheap. just (hash, tags, timestamp).
off-chain: full trace. anyone can verify the hash matches.

questions:
  - merkle tree for batch commitments (cheaper)?
  - signature schemes — eth ecdsa for now, eventually bls?
  - retention: how long do we keep the off-chain artifacts? IPFS?



## Upgrade path

The current contracts are non-upgradeable on purpose. If we need to add a
field to attestations later, the cleaner answer is to deploy a new
`MemoryAttestor` and let agents reference both during a migration window.
The pattern of doing on-chain attestations is meant to be cheap and append-
only — proxies fight that.

## gas

target: per-attestation < 100k gas. currently ~76k for warm SSTORE. ok.

## signatures

eth ecdsa for now. would consider bls if we move to a network with native pairings.

## hashing

sorted-keys json + utf8 + keccak. simple to implement in any language.

## retention

off-chain trace storage is the operator's problem. recommended: s3 with object lock keyed by trace_hash.

## deploy

hardcoded deployer address; revisit when going to mainnet.

## contract size

attestor + registry < 24kb each. plenty of headroom.

## reason codes

added bytes32 reason code field; lets producers tag attestations (e.g. keccak("liquidation_response")).
