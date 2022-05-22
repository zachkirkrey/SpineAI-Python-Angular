const {
    DataTypes, Sequelize
} = require('sequelize');

module.exports = function (sequelize) {
    return sequelize.define('Action', {
        id: {
            type: DataTypes.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        name: {
            type: DataTypes.STRING,
            allowNull: false
        },
        creation_datetime: {
            type: DataTypes.DATE,
            allowNull: false,
            defaultValue: Sequelize.NOW
        },
        study: {
            type: DataTypes.INTEGER,
            allowNull: false,
            references: {
                model: sequelize.models.Study,
                key: 'id'
            }
        }
    });
};