from onchain_memory.merkle import merkle_root, merkle_proof, _hash_pair


def test_two_leaf_root_matches_pair_hash():
    a = b"\x01" * 32
    b = b"\x02" * 32
    assert merkle_root([a, b]) == _hash_pair(a, b)


def test_proof_recovers_root():
    leaves = [bytes([i]) * 32 for i in range(8)]
    root = merkle_root(leaves)
    for i in range(len(leaves)):
        proof = merkle_proof(leaves, i)
        leaf = leaves[i]
        for sib in proof:
            leaf = _hash_pair(leaf, sib)
        assert leaf == root


def test_odd_leaf_count_handled():
    leaves = [bytes([i]) * 32 for i in range(5)]
    root = merkle_root(leaves)
    proof = merkle_proof(leaves, 4)
    leaf = leaves[4]
    for sib in proof:
        leaf = _hash_pair(leaf, sib)
    assert leaf == root
