const config = require('config');
const config_jwt = require('./api/config.json');
const server = require('./app');
const rjwt = require('restify-jwt-community');
const jwt = require('jsonwebtoken');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.get('sequelize.init'));
let User = require('./models/user')(sequelize);

server.use(rjwt(config_jwt.jwt).unless({
    path: ['/user']
}));

server.post('/user', function (req, res, next) {
    let {
        username,
        password
    } = req.body;
    User
        .findOne({
            where: {
                username: req.body.username,
                password: req.body.password,
            }
        })
        .then(data => {
            console.log('response', data.dataValues)
            let token = jwt.sign(data.dataValues, config_jwt.jwt.secret, {
                expiresIn: '60m' // token expires in 15 minutes
            });
            console.log('token', token)
            // retrieve issue and expiration times
            let {
                iat,
                exp
            } = jwt.decode(token);
            res.send({
                iat,
                exp,
                token
            });
        })
});
server.listen(config.get('restify.port'), function () {
    const host = server.address().address;
    const port = server.address().port;

    console.log('listening at http://%s:%s', host, port);
});