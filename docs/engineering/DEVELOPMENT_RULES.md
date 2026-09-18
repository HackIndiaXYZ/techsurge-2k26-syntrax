# Development Rules

Implement the smallest vertical slice first. Server-side code owns validation, consensus, policy evaluation, payout and money-like calculations; the browser renders results. Use integer paise for synthetic payout amounts, UTC timestamps, UUIDs, typed models, and transaction tests. Never add real customer/payment data, secrets, or an undocumented service.
