from yoyo import step

# All the migrations in this file are designed to fail on initialization of a blank database,
# but will be ignored as pony will initialize the tables if they don't exist

step(
    "ALTER TABLE Study ADD COLUMN mrn TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE Study DROP COLUMN mrn",
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN email TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE Study DROP COLUMN email",
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN date_of_birth DATETIME NOT NULL DEFAULT ''",
    "ALTER TABLE Study DROP COLUMN date_of_birth DATETIME NOT NULL DEFAULT ''",
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN phone_number TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE Study DROP COLUMN phone_number",
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN diagnosis TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE Study DROP COLUMN diagnosis",
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN created_by INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE Study DROP COLUMN created_by", \
    ignore_errors='apply',
)

step(
    "ALTER TABLE Study ADD COLUMN appointment_date DATETIME NULL",
    "ALTER TABLE Study DROP COLUMN appointment_date",
    ignore_errors='apply',
)
