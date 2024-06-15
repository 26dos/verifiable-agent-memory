// SPDX-License-Identifier: BSD-3-Clause
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {AgentRegistry} from "../AgentRegistry.sol";
import {BatchAttestor} from "../BatchAttestor.sol";

contract BatchAttestorTest is Test {
    AgentRegistry registry;
    BatchAttestor attestor;
    bytes32 constant AGENT = keccak256("a");

    function setUp() public {
        registry = new AgentRegistry();
        attestor = new BatchAttestor(registry);
        registry.register(AGENT, bytes32(0));
    }

    function test_attest_and_verify_2_leaf_tree() public {
        bytes32 a = keccak256("trace-a");
        bytes32 b = keccak256("trace-b");
        bytes32 root = a < b
            ? keccak256(abi.encodePacked(a, b))
            : keccak256(abi.encodePacked(b, a));

        attestor.attestBatch(AGENT, root, 2);

        bytes32[] memory proofA = new bytes32[](1);
        proofA[0] = b;
        bytes32[] memory proofB = new bytes32[](1);
        proofB[0] = a;

        assertTrue(attestor.verifyInclusion(AGENT, 0, a, proofA));
        assertTrue(attestor.verifyInclusion(AGENT, 0, b, proofB));
        assertFalse(attestor.verifyInclusion(AGENT, 0, keccak256("not-here"), proofA));
    }
}
