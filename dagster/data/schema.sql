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
        household_id INTEGER,
        street_address VARCHAR,
        zip_code VARCHAR,
        location VARCHAR
    );

CREATE TABLE persons_bronze (
    person_id BIGINT,
    address_id BIGINT,
    name VARCHAR,
    year_of_birth BIGINT,
    income BIGINT
);