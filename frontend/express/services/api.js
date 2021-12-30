const config = require('config');
const expressProxy = require('express-http-proxy');

const { OAuth2 } = require('./oauth2');

module.exports = async (req, res, next) => {

  let userEmail = '';
  try {
    let user = await OAuth2.getUser(req);
    console.log(user);
    if (user && user.email) {
      userEmail = user.email;
    }
  } catch (err) {
    // It's safe to silently pass when a user cannot be fetched for API logging
    // purposes.
  }

  // In the future, perform authentication or only allow safe requests.
  expressProxy(config.get('restifyClient.url'), {
    proxyReqPathResolver: function (req) {
      let url = req.url;
      if (url.includes('?')) {
        url += '&';
      } else {
        url += '?';
      }
      url += `oauth2UserEmail=${encodeURI(userEmail)}`;
      return url;
    }
  })(req, res, next);
}
