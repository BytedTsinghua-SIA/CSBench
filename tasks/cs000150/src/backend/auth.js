const createUser = (_users, _input) => {
  throw new Error('Not implemented')
}

const login = (_users, _credentials, _password = 'secret') => {
  throw new Error('Not implemented')
}

const getCurrentUser = (_users, _token) => {
  throw new Error('Not implemented')
}

const requireAuth = (_currentUser) => {
  throw new Error('Not implemented')
}

module.exports = {
  createUser,
  login,
  getCurrentUser,
  requireAuth,
}
