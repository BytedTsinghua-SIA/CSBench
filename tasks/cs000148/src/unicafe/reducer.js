const initialState = {
  good: 0,
  ok: 0,
  bad: 0,
}

const counterReducer = (_state = initialState, _action) => {
  throw new Error('Not implemented')
}

const applyFeedbackSequence = (_actions, _state = initialState) => {
  throw new Error('Not implemented')
}

const good = () => ({ type: 'GOOD' })
const ok = () => ({ type: 'OK' })
const bad = () => ({ type: 'BAD' })
const reset = () => ({ type: 'RESET' })

module.exports = {
  initialState,
  counterReducer,
  applyFeedbackSequence,
  good,
  ok,
  bad,
  reset,
}
