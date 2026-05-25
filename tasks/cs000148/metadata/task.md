# State Management (Part 6)

## Background
You are implementing core state management logic for small React applications. The work covers Redux reducers and action creators, Redux Toolkit slices, async/thunk-style flows, React Query data handling, and a notification context built with useReducer.

## Core Tasks
1. Redux reducers and actions:
   - Implement Unicafe feedback reducer and helper to apply action sequences.
   - Implement anecdote reducer with voting, adding, and sorting.
   - Implement filter and notification reducers with action creators.
2. Redux Toolkit modeling:
   - Define slice-like objects for filter, anecdotes, and notifications.
   - Provide a store configuration that combines reducers.
3. Async and backend support:
   - Build thunk-style action sequences for initializing, creating, and voting.
   - Build Fetch request payloads and vote updates.
4. React Query and context:
   - Map query states to view states and merge mutation results.
   - Validate anecdote length and handle notification timing with a reducer/context model.

## Scoring Points (1–3)
- Reducers and actions behave correctly and are immutable.
- Async and query helpers produce correct action sequences and state updates.
- Notifications and sorting behave as specified, including time-based expiration.
