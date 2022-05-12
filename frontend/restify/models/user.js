const {
    DataTypes, Sequelize
} = require('sequelize');

module.exports = function (sequelize) {
    return sequelize.define('User', {
        id: {
            type: DataTypes.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        uuid: {
            type: DataTypes.STRING,
            allowNull: false
        },
        first_name: {
            type: DataTypes.STRING,
            allowNull: false,
            defaultValue: 'First Name'
        },
        last_name: {
            type: DataTypes.STRING,
            allowNull: false,
            defaultValue: 'Last Name'
        },
        role: {
            type: DataTypes.STRING,
            allowNull: true
        },
        username: {
            type: DataTypes.STRING,
            allowNull: false
        },
        password: {
            type: DataTypes.STRING,
            allowNull: false
        },
        date_added: {
            type: DataTypes.DATE,
            allowNull: false,
            defaultValue: Sequelize.NOW
        }
    });
};
