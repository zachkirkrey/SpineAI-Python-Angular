// Defines Finale resource middleware for logging access requests.
const url = require('url');
const { v4: uuidv4 } = require('uuid');


function writeLog(action, sequelize, req, res, context) {
  const urlObj = url.parse(req.url);

  let id = '';
  let uuid = '';
  for (let key in req.query) {
    if (key.includes('.id')) {
      id = req.query[key];
    }
    if (key.includes('.uuid')) {
      uuid = req.query[key];
    }
  }

  sequelize.models.ApiLog.create({
    uuid: uuidv4(),
    creation_datetime: Date.now(),
    user: req.query.oauth2UserEmail || '',
    user_ip: req.connection.remoteAddress,
    action: action,
    api_url: req.url,
    object_type: urlObj.pathname,
    object_id: id,
    object_uuid: uuid
  })
  .catch((err) => {
    if (err) {
      // TODO(billy): Log errors into the database as well.
      console.log(err);
    }
  });
}

module.exports = function(sequelize) {
  return {
    list: {
      fetch: {
        before: function(req, res, context) {
          writeLog('list', sequelize, req, res, context);
          return context.continue;
        },
      }
    },
    read: {
      fetch: {
        before: function(req, res, context) {
          writeLog('read', sequelize, req, res, context);
          return context.continue;
        },
      },
    },
  };
};
