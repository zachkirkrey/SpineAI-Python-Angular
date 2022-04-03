from yoyo import step

# All the migrations in this file are designed to fail on initialization of a blank database,
# but will be ignored as pony will initialize the tables if they don't exist

step(
    "ALTER TABLE Ingestion ADD COLUMN study INTEGER NULL REFERENCES Study(id) ON DELETE CASCADE",
    "ALTER TABLE Ingestion DROP COLUMN study",
    ignore_errors='apply',
)

step(
    "CREATE INDEX idx_ingestion__study ON Ingestion (study)",
    "DROP INDEX idx_ingestion__study",
    ignore_errors='apply',
)

step(
    "ALTER TABLE OtherQuestions ADD COLUMN updation_datetime DATETIME",
    "ALTER TABLE OtherQuestions DROP COLUMN updation_datetime",
    ignore_errors='apply',
)
