const { ValidationError } = require('./errors')

const mapError = (_error) => {
  throw new Error('Not implemented')
}

const unknownEndpoint = (_request, _response) => {
  throw new Error('Not implemented')
}

const errorHandler = (_error, _request, _response, _next) => {
  throw new Error('Not implemented')
}

module.exports = {
  mapError,
  unknownEndpoint,
  errorHandler,
  ValidationError,
}
