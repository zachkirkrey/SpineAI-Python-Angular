const config = require('config');

const server = require('./app');

server.listen(config.get('restify.port'), function() {
  const host = server.address().address;
  const port = server.address().port;

  console.log('listening at http://%s:%s', host, port);
});
