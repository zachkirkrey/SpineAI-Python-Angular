const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Image', {
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
    image_series: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.ImageSeries,
        key: 'id'
      }
    },
    slice: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    total_slices: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    png_base64_str: {
      type: DataTypes.STRING,
      allowNull: false
    }
  }, {
    defaultScope: {
      attributes: {
        exclude: ['png_base64_str']
      }
    }
  });
};
