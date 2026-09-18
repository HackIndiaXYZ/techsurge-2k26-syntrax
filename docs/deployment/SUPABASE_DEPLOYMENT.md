# Supabase PostgreSQL Deployment

Use Supabase as PostgreSQL persistence, not as a browser-accessible financial backend. Apply migrations, load only synthetic seeds, disable anonymous writes through RLS, and store service credentials only in FastAPI server environment. Verify constraints for source event, payout and wallet transaction uniqueness after migration.
