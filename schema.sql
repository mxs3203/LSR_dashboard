DROP TABLE IF EXISTS lsr_data;

CREATE TABLE lsr_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temp TEXT NOT NULL,
    name TEXT NOT NULL,
    input_curve TEXT NOT NULL,
    lsr_params TEXT NOT NULL
);