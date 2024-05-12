// SPDX-License-Identifier: BSD-3-Clause
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import {AgentRegistry} from "../AgentRegistry.sol";

contract AgentRegistryTest is Test {
    AgentRegistry registry;

    function setUp() public {
        registry = new AgentRegistry();
    }

    function test_register_assigns_operator() public {
        bytes32 id = keccak256("agent1");
        bytes32 model = keccak256("model-v1");
        registry.register(id, model);

        (address operator, bytes32 modelId,, bool active) = registry.agents(id);
        assertEq(operator, address(this));
        assertEq(modelId, model);
        assertTrue(active);
    }

    function test_register_reverts_on_duplicate() public {
        bytes32 id = keccak256("dup");
        registry.register(id, bytes32(0));
        vm.expectRevert(AgentRegistry.AgentExists.selector);
        registry.register(id, bytes32(0));
    }

    function test_deactivate_only_operator() public {
        bytes32 id = keccak256("agent2");
        registry.register(id, bytes32(0));
        address other = address(0xBEEF);
        vm.prank(other);
        vm.expectRevert(AgentRegistry.NotOperator.selector);
        registry.deactivate(id);
    }
}
