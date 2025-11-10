DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL ,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(10) DEFAULT 'user'
);

DROP TABLE IF EXISTS public.books;

CREATE TABLE IF NOT EXISTS public.books (
    id SERIAL PRIMARY KEY,
    book_name VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS public.books_borrowed;

CREATE TABLE IF NOT EXISTS public.books_borrowed (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    book_id INT REFERENCES books(id),
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    book_state VARCHAR(12)
);

DROP TABLE IF EXISTS public.categories;

CREATE TABLE IF NOT EXISTS public.categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS public.categories_per_books;

CREATE TABLE IF NOT EXISTS public.categories_per_books (
    id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(id),
    category_id INT REFERENCES categories(id)
);

