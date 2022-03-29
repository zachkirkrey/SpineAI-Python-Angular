const config = require('config');
const config_jwt = require('./api/config.json');
const server = require('./app');
const rjwt = require('restify-jwt-community');
const jwt = require('jsonwebtoken');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.get('sequelize.init'));
const {
    DataTypes
} = require('sequelize');
let User = require('./models/user')(sequelize);




//server.use(rjwt(config_jwt.jwt).unless({
//    path: ['/user','/reports']
//}));

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
                    expiresIn: '7d' // token expires in 60 minutes
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

server.post('/save/history', function (req, res, next) {
    //History Save
    let Study = require('./models/study')(sequelize);
    let History = require('./models/history')(sequelize);
    tableAName = History.getTableName();
    tableBName = Study.getTableName();

    let joinTable = sequelize.define(tableAName + '_' + tableBName, {
        [tableAName]: {
            type: DataTypes.INTEGER,
            allowNull: false
        },
        [tableBName]: {
            type: DataTypes.INTEGER,
            allowNull: false
        }
    });

    History.belongsToMany(Study, {
        through: joinTable,
        foreignKey: tableAName.toLowerCase()
    });
    Study.belongsToMany(History, {
        through: joinTable,
        foreignKey: tableBName.toLowerCase()
    });
    //History Save
    let history = parseInt(req.body.history)
    let study = parseInt(req.body.study)
    console.log('req.body', history, study)
    joinTable.destroy({
        where: {},
        truncate: true
    }).then(data => {
        joinTable.create({
                History: history,
                Study: study,
            })
            .then(data => {
                console.log('history_save', data)
                res.send({
                    'message': 'Data saved successfully'
                })
            })
    })

});
server.post('/save/ReferralReason', function (req, res, next) {
    //Referral Reason Save
    let Referral = require('./models/referral-reason')(sequelize);
    let Study = require('./models/study')(sequelize);
    tableReferral = Referral.getTableName();
    studyTable = Study.getTableName();
    let refStudyTable = sequelize.define(tableReferral + '_' + studyTable, {
        [tableReferral]: {
            type: DataTypes.INTEGER,
            allowNull: false
        },
        [studyTable]: {
            type: DataTypes.INTEGER,
            allowNull: false
        }
    });

    Referral.belongsToMany(Study, {
        through: refStudyTable,
        foreignKey: tableReferral.toLowerCase()
    });
    Study.belongsToMany(Referral, {
        through: refStudyTable,
        foreignKey: studyTable.toLowerCase()
    });
    //Referral Reason Save
    let ref = parseInt(req.body.referralreason)
    let study = parseInt(req.body.study)
    console.log('req.body', ref, study)
    refStudyTable.destroy({
        where: {},
        truncate: true
    }).then(data => {
        refStudyTable.create({
                ReferralReason: ref,
                Study: study
            })
            .then(data => {
                console.log('refStudyTable', data)
                res.send({
                    'message': 'Data saved successfully'
                })
            })
    })

});
server.listen(config.get('restify.port'), function () {
    const host = server.address().address;
    const port = server.address().port;

    console.log('listening at http://%s:%s', host, port);
});