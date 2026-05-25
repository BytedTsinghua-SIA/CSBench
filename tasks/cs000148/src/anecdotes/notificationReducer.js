const initialState = {
  message: null,
}

const setNotificationAction = (_message) => {
  throw new Error('Not implemented')
}

const clearNotificationAction = () => {
  throw new Error('Not implemented')
}

const buildTimedNotification = (_message, _seconds, _now = Date.now()) => {
  throw new Error('Not implemented')
}

const notificationReducer = (_state = initialState, _action) => {
  throw new Error('Not implemented')
}

module.exports = {
  initialState,
  setNotificationAction,
  clearNotificationAction,
  buildTimedNotification,
  notificationReducer,
}
