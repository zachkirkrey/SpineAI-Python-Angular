from yoyo import step

# All the migrations in this file are designed to fail on initialization of a blank database,
# but will be ignored as pony will initialize the tables if they don't exist

step(
    "ALTER TABLE Study ADD COLUMN archived_status BOOL NOT NULL DEFAULT 0",
    "ALTER TABLE Study DROP COLUMN archived_status", \
    ignore_errors='apply',
)
