const express = require('express');
const config = require('config');
const got = require('got');
const { v4: uuidv4 } = require('uuid');

class OAuth2 {

  static getRouter() {
    let router = express.Router();
    router.use('/enabled', this.isEnabled);
    router.use('/login', this.login.bind(this));
    router.use('/callback', this.callback);
    router.use('/user', this.user.bind(this));
    router.use('/logout', this.logout);
    return router;
  }

  static isEnabled(req, res) {
    res.send(config.get('oauth2.isEnabled'));
  }

  static login(req, res) {
    let authURL = config.get('oauth2.authURL');
    let authScopes = encodeURI(config.get('oauth2.authScopes'));
    let clientId = config.get('oauth2.clientId');
    let clientSecret = config.get('oauth2.clientSecret');
    let redirectURI = encodeURI(config.get('oauth2.redirectURI'));

    if (req.query.code) {
        this.callback(req, res);
        return;
    }

    if (!req.session.oauth2State) {
        req.session.oauth2State = encodeURI(uuidv4());
    }

    res.redirect(
      `${authURL}/authorize?client_id=${clientId}&redirect_uri=${redirectURI}&response_type=code&scope=${authScopes}&state=${req.session.oauth2State}`);
  }

  static logout(req, res) {
    if (!req.session.oauth2AccessToken) {
        res.redirect(config.get('oauth2.appURI'));
    }

    let authURL = config.get('oauth2.authURL');
    let clientId = config.get('oauth2.clientId');
    let logoutURI = encodeURI(config.get('oauth2.logoutRedirectURI'));
    let tokenHint = req.session.oauth2IdToken;

    req.session.oauth2AccessToken = null;
    req.session.oauth2UserId = null;
    req.session.oauth2UserEmail = null;

    res.redirect(
      `${authURL}/logout?client_id=${clientId}&id_token_hint=${tokenHint}&post_logout_redirect_uri=${logoutURI}`);
  }

  static callback(req, res) {
    let authURL = config.get('oauth2.authURL');
    let tokenURL = `${authURL}/token`;

    console.log('getting token for code: ', req.query.code);

    got.post(tokenURL,
      {
        form: {
          'client_id': config.get('oauth2.clientId'),
          'client_secret': config.get('oauth2.clientSecret'),
          'code': req.query.code,
          'grant_type': 'authorization_code',
          'redirect_uri': config.get('oauth2.redirectURI')
        }
      })
    .then(gotRes => {
      // Store OAuth2 tokens to session.
      let bodyJson = JSON.parse(gotRes.body);
      console.log(bodyJson);
      req.session.oauth2AccessToken = bodyJson.access_token;
      req.session.oauth2UserId = bodyJson.userId;
      req.session.oauth2IdToken = bodyJson.id_token;
      res.redirect(`/studies`);
    })
    .catch(err => {
      // TODO(billy): Gracefully handle this error.
      let errMsg = `Error POSTing to ${tokenURL}: ${err.message}`;
      console.error(errMsg);
      console.log(`Response body: ${err.response.body}`);
      res.status(500).send({
        error: errMsg,
        responseBody: err.response.body
      });
    });
  }

  static getUser(req) {
    return new Promise((resolve, reject) => {
      if (req.session.oauth2AccessToken) {
        let authURL = config.get('oauth2.authURL');
        let userURL = `${authURL}/userinfo`;
        got.get(userURL,
          {
            headers: {
              'Authorization': 'Bearer ' + req.session.oauth2AccessToken
            }
          })
        .then(gotRes => {
          let bodyJson = JSON.parse(gotRes.body);
          if (bodyJson.email) {
            req.session.oauth2UserEmail = bodyJson.email;
          }
          resolve(bodyJson);
        })
        .catch(err => {
          let errMsg = `Error GETing ${userURL}: ${err.message}`;
          console.log(errMsg);
          console.log(`Response body: ${err.response.body}`);
          reject({
            status: 500,
            error: errMsg,
            responseBody: err.response.body
          });
        });
      } else {
        reject({
          error: 'No stored access token.'
        });
      }
    });
  }

  static user(req, res) {
    let user = this.getUser(req);
    return user
      .then(user => { res.send(user) })
      .catch(err => {
        if (err.status) {
          res.status(err.status).send(err);
        } else {
          res.send(err);
        }
      });
  }
}

exports.OAuth2 = OAuth2;
