#!/usr/bin/env python3
"""
Test script for LEX-7 LexNode
Demonstrates the Error-State Model in action
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from lex_node import LexNode

def test_lex_node():
    config_path = '../config/lex_config.yaml'
    node = LexNode(config_path)

    # Test directives
    test_directives = [
        "Buy a new car for $50,000",
        "Invest $1000 in stocks",
        "Save money for emergency fund",
        "Spend on health insurance"
    ]

    print("LEX-7 Node Test - Error-State Lattice")
    print("=" * 50)

    for directive in test_directives:
        print(f"\nInput Directive: {directive}")
        response = node.ingest_directive(directive)
        print(f"Node Response: {response}")
        print("-" * 30)

    # Persist state
    node.persist_state('../models/node_state.pt')
    print("\nState persisted to ../models/node_state.pt")

if __name__ == "__main__":
    test_lex_node()
