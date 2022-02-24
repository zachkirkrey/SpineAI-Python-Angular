const basicAuth = require('basic-auth');
const config = require('config');
const cors = require('cors');
const debug = require('debug')('spineai-express');
const express = require('express');
const expressProxy = require('express-http-proxy');
const fs = require('fs');
const helmet = require('helmet');
const https = require('https');
const normalizePort = require('normalize-port');
const path = require('path');
const restifyClients = require('restify-clients');
const session = require('express-session');
const sessionFileStore = require('session-file-store')(session);
const yaml = require('node-yaml');

const api = require('./services/api');
const upload = require('./services/upload');
const {
    OAuth2
} = require('./services/oauth2');
const search = require('./services/search');

console.log('NODE_ENV: ' + config.util.getEnv('NODE_ENV'));

const server = express();

// Set X-Frame-Options: SAMEORIGIN and X-Content-Type-Options: nosniff.
// NOTE(billy): Installed as part of UCLA vulnerability scan.
server.use(helmet.frameguard());
server.use(helmet.noSniff());
// Remove the X-Powerd-By: Express header.
server.disable('x-powered-by');

server.use(cors({
    origin: config.get('webserver.cors.origin'),
    optionsSuccessStatus: 200
}));

// Password protect entire server with basic HTTP authentication.
if (config.get('webserver.password.enabled')) {
    let httpPassword = config.get('webserver.password.password');
    console.log(`HTTP authentication password: ${httpPassword}`);
    var auth = function (req, resp, next) {
        var user = basicAuth(req);
        if (!user || user.pass != httpPassword) {
            resp.set('WWW-Authenticate', 'Basic realm="Access to SpineAI Dev app"');
            return resp.status(401).send();
        }
        return next();
    }
    server.use(auth);
}

// express-session
server.use(session({
    secret: config.get('webserver.session.secret'),
    store: new sessionFileStore({}),
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: 'auto',
        httpOnly: true,
        maxAge: 259200000,
        sameSite: true
    }
}));

let uploadDir = config.get('uploadService.uploadDir');
let apiClient = restifyClients.createJsonClient(config.get('restifyClient'));
let uploader = new upload.Uploader(uploadDir, apiClient);
server.post('/upload', uploader.upload.bind(uploader));

server.use('/api', api);
server.use('/backend', expressProxy(config.get('backendService.url')));

server.use('/oauth2', OAuth2.getRouter());

// Angular endpoint.
server.use(express.json());
server.use(express.urlencoded({
    extended: true
}));
server.get('*.*', express.static('angular_dist', {
    fallthrough: false
}));
server.use(function (req, res) {
    res.sendFile('angular_dist/index.html', {
        root: __dirname
    });
});

if (config.get('webserver.https.enabled')) {
    const httpsPort = normalizePort(process.env.EXPRESS_HTTPS_PORT || '443');
    const httpsServer = https.createServer({
            key: fs.readFileSync(config.get('webserver.https.keyFile')),
            cert: fs.readFileSync(config.get('webserver.https.certFile'))
        }, server)
        .listen(httpsPort, () => {
            console.log('Server started!');
        });
    // Redirect HTTP traffic to HTTPS.
    if (config.get('webserver.https.redirectHTTP')) {
        const http = require('http');
        http.createServer(function (req, res) {
            res.writeHead(301, {
                "Location": "https://" + req.headers['host'] + req.url
            });
            res.end();
        }).listen(80);
    }

    // Reload HTTPS cert and key when files change.
    let certTimeout;
    fs.watch(config.get('webserver.https.certFile'), () => {
        clearTimeout(certTimeout);

        console.log('New HTTPS cert detected. Reloading certs...');
        certTimeout = setTimeout(() => {
            httpsServer._sharedCreds.context.setCert(fs.readFileSync(
                config.get('webserver.https.certFile')));
            httpsServer._sharedCreds.context.setKey(fs.readFileSync(
                config.get('webserver.https.keyFile')));
        }, 30000);
    });
} else {
    //const port = normalizePort(process.env.EXPRESS_PORT || '80');
    const port = normalizePort('8083');
    server.listen(port, () => {
        debug('Listening on port %o', port);
        console.log(`Server started on port ${port}!`);
    });
}