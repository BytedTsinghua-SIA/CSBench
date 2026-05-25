const { ValidationError } = require('./errors')
const { generateId } = require('./utils')
const {
  validateNewPerson,
  validateUpdatePerson,
} = require('./validators')

const findById = (_persons, _id) => {
  throw new Error('Not implemented')
}

const findByName = (_persons, _name) => {
  throw new Error('Not implemented')
}

const countPersons = (_persons) => {
  throw new Error('Not implemented')
}

const addPerson = (_persons, _newPerson, _options = {}) => {
  throw new Error('Not implemented')
}

const removePerson = (_persons, _id) => {
  throw new Error('Not implemented')
}

const updatePerson = (_persons, _id, _updates) => {
  throw new Error('Not implemented')
}

class PhonebookStore {
  constructor(initialPersons = []) {
    this.persons = [...initialPersons]
  }

  list() {
    return [...this.persons]
  }

  count() {
    return this.persons.length
  }

  findById(id) {
    return findById(this.persons, id)
  }

  findByName(name) {
    return findByName(this.persons, name)
  }

  add(person, options = {}) {
    const result = addPerson(this.persons, person, options)
    this.persons = result.persons
    return result.person
  }

  remove(id) {
    const result = removePerson(this.persons, id)
    this.persons = result.persons
    return result.removed
  }

  update(id, updates) {
    const result = updatePerson(this.persons, id, updates)
    this.persons = result.persons
    return result.person
  }
}

module.exports = {
  ValidationError,
  findById,
  findByName,
  countPersons,
  addPerson,
  removePerson,
  updatePerson,
  PhonebookStore,
}
