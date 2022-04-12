const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('LogoImage', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    uuid: {
        type: DataTypes.STRING,
        allowNull: false
    },
    creation_datetime: {
        type: DataTypes.DATE,
        allowNull: false
    },
    png_base64_str: {
        type: DataTypes.STRING,
        allowNull: false
    },
    active: {
        type: DataTypes.BOOLEAN,
        allowNull: true
    },
  });
};
