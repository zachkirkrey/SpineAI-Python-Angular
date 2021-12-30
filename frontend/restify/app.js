/**
 * This Restify server provides a REST API for the SpineAI database.
 */
'use strict';

const http = require('http');

const config = require('config');
const debug = require('debug')('spineai-restify');
const finale = require('finale-rest');
const Sequelize = require('sequelize');
const restify = require('restify');
const restifyCors = require('restify-cors-middleware');
const yaml = require('node-yaml');
const yargs = require('yargs');

// Initialize Sequelize ORM.
console.log('Loading database %o', config.get('sequelize.init.storage'))
const sequelize = new Sequelize(config.get('sequelize.init'));
require('./models')(sequelize);

// Initialize Restify.
var server = restify.createServer();
const cors = restifyCors({
  preflightMaxAge: 5,
  origins: ['*'],
  allowHeaders: ['Authorization', 'API-Token', 'Content-Range'], //Content-range has size info on lists
  exposeHeaders: ['Authorization', 'API-Token-Expiry', 'Content-Range']
});

server.pre(cors.preflight);
server.use(cors.actual);

server.use(restify.plugins.acceptParser(server.acceptable));
server.use(restify.plugins.queryParser());
server.use(restify.plugins.bodyParser());

finale.initialize({
  app: server,
  sequelize: sequelize
});

require('./api')(finale, sequelize);

module.exports = server;
