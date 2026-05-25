const initialState = { message: null, expiresAt: null }

const notificationReducer = (_state = initialState, _action) => {
  throw new Error('Not implemented')
}

const showNotification = (_message, _durationMs = 5000, _now = Date.now()) => {
  throw new Error('Not implemented')
}

const shouldClear = (_state, _now = Date.now()) => {
  throw new Error('Not implemented')
}

module.exports = {
  initialState,
  notificationReducer,
  showNotification,
  shouldClear,
}
