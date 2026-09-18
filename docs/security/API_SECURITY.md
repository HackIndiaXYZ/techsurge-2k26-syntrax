# API Security

Telemetry and simulation mutation routes require a server-validated demo token; read routes may be public only if they expose synthetic data. Validate content type and size, rate-limit mutations, return generic errors, include correlation IDs, and restrict CORS to known frontend origins. Use HTTPS on hosted environments. Do not expose database/admin credentials in API responses.
