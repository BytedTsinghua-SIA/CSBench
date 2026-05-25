const { setAnecdotesAction, createAnecdoteAction, createVoteAction } = require('./anecdoteReducer')
const { buildTimedNotification } = require('./notificationReducer')

const initializeAnecdotes = (_items) => {
  throw new Error('Not implemented')
}

const createAnecdoteThunk = (_anecdote, _seconds = 5) => {
  throw new Error('Not implemented')
}

const voteAnecdoteThunk = (_anecdote, _seconds = 5) => {
  throw new Error('Not implemented')
}

module.exports = {
  initializeAnecdotes,
  createAnecdoteThunk,
  voteAnecdoteThunk,
}
