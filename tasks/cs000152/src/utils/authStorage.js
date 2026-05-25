class AuthStorage {
  constructor(_namespace = 'auth', _storage = null) {
    throw new Error('Not implemented')
  }

  getAccessToken() {
    throw new Error('Not implemented')
  }

  setAccessToken(_accessToken) {
    throw new Error('Not implemented')
  }

  removeAccessToken() {
    throw new Error('Not implemented')
  }
}

const authStorageScenario = () => {
  throw new Error('Not implemented')
}

module.exports = {
  AuthStorage,
  authStorageScenario,
}
