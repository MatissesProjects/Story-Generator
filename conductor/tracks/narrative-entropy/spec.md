# ⏳ Track: Narrative Entropy

## Overview
Introduce dynamic decay and conflict resolution to the story's memory and lore, ensuring the world is not static. Over time, relationships cool down, rumors distort facts, and contradictions between the LLM and the database are actively resolved via "Lore Duels".

## Core Objectives
- **Relationship Decay**: Trust, Fear, and Affection drift back toward 0 over time if not actively maintained.
- **Lore Volatility**: Minor lore facts might be slightly altered or forgotten by the system to simulate the unreliability of history/rumors.
- **Lore Duels**: When `canon_checker.py` detects a contradiction, trigger an automated resolution where the system decides if the world changed, someone lied, or it was just a hallucination.

## Functional Requirements
1. **Entropy Engine**: `entropy_engine.py` to handle the decay logic for relationships and story state during global ticks.
2. **Canon Conflict Resolution**: Extend `canon_checker.py` to use an LLM prompt to reconcile contradictions dynamically instead of just warning the player.

## Dependencies
- `simulation_manager.py`: To trigger entropy over time.
- `db.py`: To update relationships and lore.
- `canon_checker.py`: To intercept and resolve lore conflicts.
