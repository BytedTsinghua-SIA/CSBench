# Phonebook Backend (Part 3)

## Background
You are building the backend for a simple phonebook application. The server is built with Node.js and Express and exposes a REST API. The data starts as a hardcoded list, then moves to a small database module. The backend must also serve a production frontend build from a `dist` directory.

## Core Tasks
1. Implement REST endpoints for phonebook entries:
   - `GET /api/persons` returns all entries.
   - `GET /api/persons/:id` returns a single entry or 404 if missing.
   - `POST /api/persons` adds a new entry with a generated id.
   - `DELETE /api/persons/:id` removes an entry.
   - `PUT /api/persons/:id` updates an entry (used when the frontend updates a duplicate name).
2. Add `/info` that shows the current count and request time.
3. Add middleware:
   - Request logging using morgan with the tiny format and POST body logging.
   - Unknown endpoint handling and centralized error handling.
4. Validation rules:
   - Name and number are required.
   - Names must be unique.
   - Name length is at least 3 characters.
   - Phone number format: two parts separated by `-`, first part has 2–3 digits, and total length is at least 8.
5. Move data operations into a database module with async functions (simulating MongoDB persistence).
6. Serve static frontend assets from the `dist` directory.
7. Provide `npm start` and `npm run dev` scripts (`node --watch`).


## Scoring Points (1–3)
- Correct API behavior, status codes, and validation errors.
- Clean separation between routing, validation, and persistence layers.
- Logging, static frontend serving, and README link included.
