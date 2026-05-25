const DEFAULT_MIN_NAME_LENGTH = 3

const validateRequiredFields = (_person) => {
  throw new Error('Not implemented')
}

const validateNameLength = (_name, _minLength = DEFAULT_MIN_NAME_LENGTH) => {
  throw new Error('Not implemented')
}

const validateNumberFormat = (_number) => {
  throw new Error('Not implemented')
}

const validateUniqueName = (_name, _existingNames, _currentName) => {
  throw new Error('Not implemented')
}

const validateNewPerson = (_person, _existingNames) => {
  throw new Error('Not implemented')
}

const validateUpdatePerson = (_person, _existingNames, _currentName) => {
  throw new Error('Not implemented')
}

module.exports = {
  DEFAULT_MIN_NAME_LENGTH,
  validateRequiredFields,
  validateNameLength,
  validateNumberFormat,
  validateUniqueName,
  validateNewPerson,
  validateUpdatePerson,
}
