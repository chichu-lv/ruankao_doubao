# Schema migration

Migrations live in `schemas/migrations/` and are ordered, versioned and backup-gated. `0001-initial.json` creates only the named private ArchitectPass tables and unique logical keys. It may not delete or rename pre-existing user data. A rollback first exports all created tables, then requires explicit confirmation before removing only objects created by that migration.

