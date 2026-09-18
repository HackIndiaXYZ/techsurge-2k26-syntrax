# ADR 003 Synthetic Wallet

## Context

The official PS forbids real accounts, rails and money.

## Decision

Model a synthetic wallet and immutable synthetic transaction ledger.

## Alternatives

UPI sandbox, bank API, stablecoin testnet, or no wallet.

## Reason

It demonstrates settlement and idempotency without misrepresenting payment capability.

## Consequences

Every UI amount carries a synthetic label; the ledger cannot be described as a real payment integration.
