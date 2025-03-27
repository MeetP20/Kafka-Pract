-- init.sql (Automatically runs when the container starts)
CREATE TABLE IF NOT EXISTS kafka (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    address VARCHAR(255) NOT NULL
);
