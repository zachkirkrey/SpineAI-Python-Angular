'use strict';
const config = require('config');
const Sequelize = require('sequelize');
console.log('Loading login db %o', config.get('sequelize.init.storage'))
const sequelize = new Sequelize(config.get('sequelize.init'));
let User = require('../models/user')(sequelize);
module.exports.authenticate = async function (req, res) {
    const candidate = await User.findOne({
        where: {
            username: req.body.username,
            password: req.body.password,
        }
    })

}