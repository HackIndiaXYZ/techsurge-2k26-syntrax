# Database Authorization and RLS

For the MVP, browser clients never hold database credentials. Only the FastAPI service accesses tables. If Supabase Row Level Security is enabled, deny direct anonymous writes on every canonical table and use a server-only role for the API. A read-only demo view may expose an API projection, not raw database access.

Production would require authenticated policyholder identities, tenant partitioning, insurer/operator roles, formal RLS policies, audit access controls, key rotation, and reviewed service-role usage. Those are production gaps, not implemented claims.
