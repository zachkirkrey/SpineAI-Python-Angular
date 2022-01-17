const config = require('config');
const config_jwt = require('./api/config.json');
const server = require('./app');
const rjwt = require('restify-jwt-community');
const jwt = require('jsonwebtoken');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.get('sequelize.init'));


server.listen(config.get('restify.port'), function() {
  const host = server.address().address;
  const port = server.address().port;

  console.log('listening at http://%s:%s', host, port);
});
