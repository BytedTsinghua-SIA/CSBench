# GraphQL Library (Part 8)

## Background
You are implementing a GraphQL-based library application with authors, books, and users. The backend must support queries, mutations, authentication, subscriptions, and efficient resolvers. The frontend logic should render authors/books, manage cached updates, and handle genres and login flows.

## Core Tasks
1. Backend GraphQL logic:
   - Implement counts, list queries, filters by author/genre, and mutations for adding books and editing authors.
   - Add user creation, login, and token-based authorization for protected mutations.
   - Validate inputs and surface errors in a GraphQL-friendly way.
   - Implement subscription handling for `bookAdded` and an optimized author bookCount resolver.
2. Frontend data handling:
   - Render Authors and Books views, normalize author data, and keep cache in sync after mutations.
   - Filter books by genre and build recommendations by favorite genre.
   - Implement login/session helpers and subscription updates.
3. Advanced updates:
   - Ensure cache updates after subscriptions and genre-based queries remain consistent.

## Scoring Points (1–3)
- Correct GraphQL behavior for queries, mutations, and auth-protected operations.
- Frontend cache and filtering logic matches expected view outputs.
- Subscriptions and optimized author counts behave correctly.
