const path = require('path')
const fs = require('fs')
const { seedPersons } = require('./data')
const { PhonebookStore } = require('./store')

const defaultPath = path.join(__dirname, '..', 'data', 'phonebook.json')

const ensureFile = (_filePath, _seedData = seedPersons) => {
  throw new Error('Not implemented')
}

const readStore = (_filePath) => {
  throw new Error('Not implemented')
}

const writeStore = (_filePath, _store) => {
  throw new Error('Not implemented')
}

const createRepository = (_options = {}) => {
  throw new Error('Not implemented')
}

const repoList = async (_filePath) => {
  throw new Error('Not implemented')
}

const repoCount = async (_filePath) => {
  throw new Error('Not implemented')
}

const repoFindById = async (_filePath, _id) => {
  throw new Error('Not implemented')
}

const repoAdd = async (_filePath, _person) => {
  throw new Error('Not implemented')
}

const repoUpdate = async (_filePath, _id, _updates) => {
  throw new Error('Not implemented')
}

const repoRemove = async (_filePath, _id) => {
  throw new Error('Not implemented')
}

const repoUpsertByName = async (_filePath, _person) => {
  throw new Error('Not implemented')
}

module.exports = {
  defaultPath,
  ensureFile,
  readStore,
  writeStore,
  createRepository,
  repoList,
  repoCount,
  repoFindById,
  repoAdd,
  repoUpdate,
  repoRemove,
  repoUpsertByName,
}
