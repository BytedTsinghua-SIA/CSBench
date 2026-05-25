const express = require('express')
const path = require('path')
const { createRepository } = require('./phonebook/repository')
const { createHandlers } = require('./phonebook/handlers')
const { createLogger } = require('./phonebook/logging')
const { unknownEndpoint, errorHandler } = require('./phonebook/middleware')
const { ROUTES } = require('./phonebook/routes')

const app = express()

app.use(express.json())
app.use(express.static(path.join(__dirname, 'dist')))
app.use(createLogger())

const repository = createRepository()
const handlers = createHandlers(repository)

ROUTES.forEach((route) => {
  app[route.method](route.path, handlers[route.handler])
})

app.use(unknownEndpoint)
app.use(errorHandler)

module.exports = app
