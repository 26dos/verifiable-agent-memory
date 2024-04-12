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
