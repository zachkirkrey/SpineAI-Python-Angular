const config = require('config');
const config_jwt = require('./api/config.json');
const server = require('./app');
const rjwt = require('restify-jwt-community');
const jwt = require('jsonwebtoken');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.get('sequelize.init'));
let User = require('./models/user')(sequelize);
let Study = require('./models/study')(sequelize);

server.use(rjwt(config_jwt.jwt).unless({
    path: ['/user']
}));

server.post('/user', function (req, res, next) {
    User.findOne({
            where: {
                username: req.body.username,
                password: req.body.password,
            }
        })
        .then(data => {
            let login_data = data
            if (login_data != null) {
                let token = jwt.sign(data.dataValues, config_jwt.jwt.secret, {
                    expiresIn: '60m' // token expires in 60 minutes
                });
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
            } else if (login_data == null) {
                const user = new User({
                    username: req.body.username,
                    password: req.body.password,
                    uuid: req.body.uuid
                })
                user.save()
                User.findOne({
                        where: {
                            username: req.body.username,
                            password: req.body.password,
                        }
                    })
                    .then(data => {
                        console.log('response', data)
                        let login_data = data
                        if (login_data != null) {
                            let token = jwt.sign(data.dataValues, config_jwt.jwt.secret, {
                                expiresIn: '60m' // token expires in 60 minutes
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
                        }

                    })

            }

        })
});


server.post('/search/pacs', function (req, res, next) {
    Study.findOne({
            where: {
                uuid: req.body.uuid
            }
        })
        .then(data => {
            let searchPacs = data
            if (searchPacs != null) {
                res.send(
                    data.dataValues
                );
            } else if (searchPacs == null) {
                res.send({
                    'message': 'No saved data found!!'
                })
            }

        })
});
server.listen(config.get('restify.port'), function () {
    const host = server.address().address;
    const port = server.address().port;

    console.log('listening at http://%s:%s', host, port);
});