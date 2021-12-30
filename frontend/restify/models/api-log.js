const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('ApiLog', {
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
    user: {
      type: DataTypes.STRING,
      allowNull: false
    },
    user_ip: {
      type: DataTypes.STRING,
      allowNull: false
    },
    action: {
      type: DataTypes.STRING,
      allowNull: false
    },
    api_url: {
      type: DataTypes.STRING,
      allowNull: false
    },
    object_type: {
      type: DataTypes.STRING,
      allowNull: false
    },
    object_id: {
      type: DataTypes.STRING,
      allowNull: false
    },
    object_uuid: {
      type: DataTypes.STRING,
      allowNull: false
    }
  });
};
