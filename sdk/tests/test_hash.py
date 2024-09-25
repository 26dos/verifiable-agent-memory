from onchain_memory.hash import canonicalize, trace_hash


def test_canonicalize_sorts_keys():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonicalize(a) == canonicalize(b)


def test_trace_hash_changes_with_value():
    a = trace_hash({"x": 1})
    b = trace_hash({"x": 2})
    assert a != b


def test_trace_hash_unicode():
    h = trace_hash({"note": "hello — 世界"})
    assert len(h) == 32
