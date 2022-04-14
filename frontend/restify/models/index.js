/**
 * This module defines Sequelize models for the SpineAI database.
 *
 * The SpineAI database is defined in and initialized by Pony ORM in python.
 */
const {
    DataTypes
} = require('sequelize');

/**
 * Defines Sequelize models for many-to-many relationships created by Pony ORM.
 * @param {Object} sequelize sequelize.Sequelize
 * @param {Object} tableA sequelize.Model
 * @param {Object} tableB sequelize.Model
 */
function defineManyToMany(sequelize, tableA, tableB) {
    tableAName = tableA.getTableName();
    tableBName = tableB.getTableName();
    joinTable = sequelize.define(tableAName + '_' + tableBName, {
        [tableAName]: {
            type: DataTypes.INTEGER,
            allowNull: false
        },
        [tableBName]: {
            type: DataTypes.INTEGER,
            allowNull: false
        }
    });
    tableA.belongsToMany(tableB, {
        through: joinTable,
        foreignKey: tableAName.toLowerCase()
    });
    tableB.belongsToMany(tableA, {
        through: joinTable,
        foreignKey: tableBName.toLowerCase()
    });
}

/**
 * Define Sequelize magic for one-to-many relationships created by Pony ORM.
 *
 * This is subtle: Pony requires relationships to be defined two-way in the
 * python API. However, it does the right thing and obeys database
 * normalization and only defines one foreign key under the hood.
 *
 * Sequelize, meanwhile, sucks, and only lets you use its getForeign()
 * association magic if foreign keys exist both ways, disobeying database
 * normalization.
 *
 * To fix this and get the magic both ways, we:
 *   - Define the one -> many relationship using standard Sequelize notation.
 *     (because the many table actually has as a foreign key to one, which
 *     Sequelize supports)
 *   - The get() functions for many -> one relationship manually.
 *     (because Sequelize won't allow us to use its magic without definition
 *     another foreign key, which Pony doesn't do and disobeys database
 *     normalization anyways.)
 *
 * @param {Object} tableOne sequelize.Model (eg. Study)
 * @param {Object} tableMany sequelize.Model (eg. Classification)
 * @param {string} foreignKey Foreign key in tableMany to tableOne. Defaults to tableOne.getTableName().toLowerCase().
 */
function defineOneToMany(tableOne, tableMany, foreignKey) {
    tableOneName = tableOne.getTableName();
    tableManyName = tableMany.getTableName();
    foreignKey = foreignKey || tableOneName.toLowerCase();
    tableOne.hasMany(tableMany, {
        foreignKey: foreignKey
    });

    oneAsFunc = 'get' + tableOneName;
    tableMany.prototype[oneAsFunc] = function () {
        return tableOne.findOne({
            where: {
                id: this[foreignKey]
            }
        });
    };
}

/**
 * Same as defineOneToMany() but for one-to-one relationships.
 */
function defineOneToOne(tableA, tableB, Aas, Bas, foreignKey) {
    tableAName = tableA.getTableName();
    tableBName = tableB.getTableName();

    // tableA.hasOne(tableB, {
    //   as: Bas,
    //   foreignKey: foreignKey
    // });

    // asFunc = 'get' + Aas;
    // tableB.prototype[asFunc] = function() {
    //   return tableA.findOne({
    //     where: {
    //       id: this[foreignKey]
    //     }
    //   });
    // };

    tableB.belongsTo(tableA, {
        as: Aas,
        foreignKey: foreignKey
    });
}

module.exports = function (sequelize) {
    let ApiLog = require('./api-log.js')(sequelize);
    let CanalSegmentation = require('./canal-segmentation')(sequelize);
    let Classification = require('./classification')(sequelize);
    let DiskSegmentation = require('./disk-segmentation')(sequelize);
    let ImageSeries = require('./image-series')(sequelize);
    let Image = require('./image.js')(sequelize);
    let Ingestion = require('./ingestion')(sequelize);
    let Report = require('./report')(sequelize);
    let Segmentation = require('./segmentation')(sequelize);
    let Study = require('./study')(sequelize);
    let Action = require('./action')(sequelize);
    let ReferralReason = require('./referral-reason')(sequelize);
    let Symptoms = require('./symptoms')(sequelize);
    let OtherTreatments = require('./other-treatments')(sequelize);
    let History = require('./history')(sequelize);
    let OtherQuestions = require('./questions')(sequelize);
    let LogoImage = require('./logo-image')(sequelize);

    defineOneToMany(Study, Classification);
    defineOneToMany(Study, Segmentation);
    defineOneToMany(Study, ImageSeries);
    defineOneToMany(Classification, Segmentation);
    defineOneToMany(Study, CanalSegmentation);
    defineOneToMany(Study, DiskSegmentation);
    defineOneToMany(ImageSeries, Classification, 'input_series');
    defineOneToMany(ImageSeries, Image, 'image_series');
    defineOneToMany(Study, Action);
    defineOneToMany(Study, OtherQuestions);
    defineOneToMany(Study, Ingestion);

    defineOneToOne(
        Segmentation,
        CanalSegmentation,
        'Segmentation',
        'CanalSegmentation',
        'segmentation');
    defineOneToOne(
        Segmentation,
        DiskSegmentation,
        'Segmentation',
        'DiskSegmentation',
        'segmentation');
    defineOneToOne(
        ImageSeries,
        Segmentation,
        'RawSeries',
        'RawSegmentation',
        'raw_segmentation_series');
    defineOneToOne(
        ImageSeries,
        Segmentation,
        'PostprocessedSeries',
        'PostprocessedSegmentation',
        'postprocessed_segmentation_series');
    defineOneToOne(
        ImageSeries,
        Segmentation,
        'PreprocessedSeries',
        'PreprocessedSegmentation',
        'preprocessed_patient_series');

    defineManyToMany(sequelize, Report, Study);
    defineManyToMany(sequelize, Classification, Report);
    defineManyToMany(sequelize, History, Study);
    defineManyToMany(sequelize, ReferralReason, Study);
    defineManyToMany(sequelize, Study,Symptoms);
    defineManyToMany(sequelize, OtherTreatments, Study);

    Study.addScope('defaultScope', {});
    Study.addScope('deep', {
        include: [{
                model: Report
            },
            {
                model: CanalSegmentation
            }
        ]
    });
    Study.addScope('includeDisk', {
        include: [{
            model: DiskSegmentation
        }]
    });
    Study.addScope('includeReports', {
        include: [{
            model: Report
        }, ]
    });
    Study.addScope('includeActions', {
        include: [{
            model: Action
        }, ]
    });
    Study.addScope('includeLastAction', {
        include: [
            {
                model: Action,
                order: [['creation_datetime', 'DESC']],
                limit: 1,
            },
        ]
    });
    Study.addScope('includeHistory', {
        include: [{
            model: History
        }, ]
    });
    Study.addScope('includeReferralReason', {
        include: [{
            model: ReferralReason
        }, ]
    });
    Study.addScope('includeSymptoms', {
        include: [{
            model: Symptoms
        }, ]
    });
    Study.addScope('includeOtherTreatments', {
        include: [{
            model: OtherTreatments
        }, ]
    });
    Study.addScope('includeQuestions', {
        include: [{
            model: OtherQuestions
        }, ]
    });
    CanalSegmentation.addScope('defaultScope', {
        include: [{
            model: Segmentation,
            as: 'Segmentation'
        }]
    });

    DiskSegmentation.addScope('defaultScope', {
        include: [{
            model: Segmentation,
            as: 'Segmentation'
        }]
    });

    Segmentation.addScope('defaultScope', {
        include: [
            // { model: ImageSeries, as: 'RawSeries' },
            {
                model: ImageSeries,
                as: 'PostprocessedSeries'
            },
            {
                model: ImageSeries,
                as: 'PreprocessedSeries'
            }
        ]
    });

    ImageSeries.addScope('defaultScope', {
        attributes: {
            exclude: ['image_pickled', 'metadata_pickled']
        },
        include: [{
            model: Image
        }]
    });

    Report.addScope('simple', {});

    return {
        ApiLog: ApiLog,
        CanalSegmentation: CanalSegmentation,
        Classification: Classification,
        DiskSegmentation: DiskSegmentation,
        ImageSeries: ImageSeries,
        Ingestion: Ingestion,
        Report: Report,
        Segmentation: Segmentation,
        Study: Study,
        Action: Action,
        History:History,
        ReferralReason:ReferralReason,
        Symptoms:Symptoms,
        OtherTreatments:OtherTreatments,
        LogoImage:LogoImage
    }
}
