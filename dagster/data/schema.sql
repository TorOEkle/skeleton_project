CREATE TABLE adress_bronze (
        household_id INTEGER,
        street_address VARCHAR,
        zip_code VARCHAR,
        location VARCHAR
    );

CREATE TABLE adress_silver (
        household_id INTEGER,
        street_address VARCHAR,
        zip_code VARCHAR,
        location VARCHAR,
        full_adress VARCHAR
    );

CREATE TABLE persons_bronze (
        person_id INTEGER,
        household_id INTEGER,
        name VARCHAR,
        year_of_birth INTEGER,
        income INTEGER
        
    );

CREATE TABLE household_data (
    household_id BIGINT,
    mean_yob REAL,
    household_income BIGINT
);

CREATE TABLE household_gold (
    household_id BIGINT,
    mean_yob REAL,
    household_income BIGINT,
    full_adress VARCHAR
);

