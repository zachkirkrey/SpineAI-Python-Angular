const config = require('config');
const fs = require('fs');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.get('sequelize.init'));

const csv = require('./csv');
const uuid = require('uuid');

let User = require('../models/user')(sequelize);


module.exports = function (finale, sequelize) {
    // NOTE(billy): Ideally we could tell sequelize to use the defaultScope
    // instead of using excludeAttributes on finale, but we can't due to
    // https://github.com/sequelize/sequelize/issues/8612
    let apiLogResource = finale.resource({
        model: sequelize.models.ApiLog,
        endpoints: ['/apilogs', '/apilog/:uuid']
    });
    let canalSegmentationResource = finale.resource({
        model: sequelize.models.CanalSegmentation,
        endpoints: ['/canalsegmentations', '/canalsegmentation/:uuid']
    });
    let classificationResource = finale.resource({
        model: sequelize.models.Classification,
        endpoints: ['/classifications', '/classification/:uuid']
    });
    let diskSegmentationResource = finale.resource({
        model: sequelize.models.DiskSegmentation,
        endpoints: ['/disksegmentations', '/disksegmentation/:uuid']
    })
    let imageSeriesResource = finale.resource({
        model: sequelize.models.ImageSeries,
        endpoints: ['/imageseries', '/imageseries/:uuid'],
        excludeAttributes: ['image_pickled', 'metadata_pickled']
    });
    let imageResource = finale.resource({
        model: sequelize.models.Image,
        endpoints: ['/image', '/image/:uuid'],
        excludeAttributes: ['png_base64_str']
    });
    let ingestionResource = finale.resource({
        model: sequelize.models.Ingestion,
        endpoints: ['/ingestions', '/ingestion/:uuid'],
        excludeAttributes: ['file_archive_bytes']
    });
    let reportResource = finale.resource({
        model: sequelize.models.Report.scope('defaultScope'),
        endpoints: ['/reports', '/report/:uuid'],
        excludeAttributes: ['report_bytes'],
        associations: true
    });
    let segmentationResource = finale.resource({
        model: sequelize.models.Segmentation,
        endpoints: ['/segmentations', '/segmentation/:uuid']
    });
    let studyResource = finale.resource({
        model: sequelize.models.Study,
        endpoints: ['/studies', '/study/:uuid'],
        associations: false
    });
    let actionResource = finale.resource({
        model: sequelize.models.Action,
        endpoints: ['/action', '/action/:id'],
        associations: false
    });
    let referralResource = finale.resource({
        model: sequelize.models.ReferralReason,
        endpoints: ['/referralreasons', '/referralreason/:uuid'],
        associations: false
    });
    let symptomsResource = finale.resource({
        model: sequelize.models.Symptoms,
        endpoints: ['/symptoms', '/symptom/:uuid'],
        associations: false
    });
    let treatmentsResource = finale.resource({
        model: sequelize.models.OtherTreatments,
        endpoints: ['/treatments', '/treatment/:uuid'],
        associations: false
    });
    let historyResource = finale.resource({
        model: sequelize.models.History,
        endpoints: ['/history', '/history/:uuid'],
        associations: false
    });
    let questionsResource = finale.resource({
        model: sequelize.models.OtherQuestions,
        endpoints: ['/questions', '/question/:uuid'],
        associations: false
    });
    let logoImageResource = finale.resource({
        model: sequelize.models.LogoImage,
        endpoints: ['/logoimage', '/logoimage/:uuid'],
        associations: false
    });
    let userResource = finale.resource({
        model: sequelize.models.User,
        endpoints: ['/users', '/users/:uuid'],
        associations: false
    });



    // Log access to the following resources.
    if (config.get('api.apilog.enabled')) {
        const apiLogMiddleware = require('./api-log-middleware')(sequelize);
        [
            canalSegmentationResource,
            classificationResource,
            diskSegmentationResource,
            imageSeriesResource,
            ingestionResource,
            reportResource,
            segmentationResource,
            studyResource,
            actionResource,
            referralResource,
            symptomsResource,
            treatmentsResource,
            historyResource,
            questionsResource,
            logoImageResource,
            userResource
        ].forEach(resource => resource.use(apiLogMiddleware));
    }

    studyResource.list.fetch.before(function (req, res, context) {
        console.log(context);
        return context.continue;
    });

    actionResource.list.fetch.before(function (req, res, context) {
        context.shallow = true;
        return context.continue;
    });

    studyResource.update.fetch(function(req, res, context) {
        console.log("<<<<<< Updating user >>>>>>");
        console.log(req.body);
        return context.continue;
    });

    // Send a Report as the given type.
    function sendReportAs(res, as, report) {
        as = as.toLowerCase();
        if (as == 'pdf') {
            res.setHeader('Content-Type', 'application/pdf');
            res.end(report.report_bytes);
        } else if (as == 'html') {
            res.setHeader('Content-Type', 'text/html');
            res.end(report.report_bytes);
        } else if (as == 'json') {
            res.setHeader('Content-Type', 'application/json');
            res.end(report.report_bytes);
        } else if (as == 'csv') {
            res.setHeader('Content-Type', 'text/csv');
            res.setHeader('Content-disposition', `filename=${report.Studies[0].name}.csv`);
            res.end(csv.sendCsv([report]));
        // }else if (as == 'htmlsimple'){
        //     res.setHeader('Content-Type', 'application/json');
        //     report_html = (report.report_bytes).toString();
        //     res.json({"result":report_html});
        } else {
            throw new Error(`Invalid "as" value: "${req.query.as}"`);
        }
    }


    reportResource.read.fetch.before(function (req, res, context) {
        // We normally ignore the report_bytes column, but if as= is requested,
        // provide it.
        if ('as' in req.query) {
            context.options.attributes = [...this.resource.attributes];
            context.options.attributes.push('report_bytes');
        }
        return context.continue;
    });
    reportResource.read.send.before(function (req, res, context) {
        if ('as' in req.query) {
            let as = req.query.as.toLowerCase();
            sendReportAs(res, as, context.instance);
            return context.skip;
        }
        return context.continue;
    });
    reportResource.list.fetch.before(function (req, res, context) {
        // We normally ignore the report_bytes column, but if as= is requested,
        // provide it.
        if ('as' in req.query) {
            context.options.attributes = [...this.resource.attributes];
            context.options.attributes.push('report_bytes');
            if (!req.query.as.includes('summary')) {
                context.count = 1;
            }
        }
        return context.continue;
    });
    reportResource.list.send.before(function (req, res, context) {
        if ('as' in req.query) {
            if (context.instance.length == 0) {
                throw new Error(`Requested render as=${req.query.as}, but no report found.`);
            }

            let as = req.query.as.toLowerCase();
            if (as == 'summarycsv') {
                res.setHeader('Content-Type', 'text/csv');
                res.setHeader('Content-disposition', `filename=summary.csv`);

                let reports = context.instance;
                if ('csvcol' in req.query) {
                    res.end(csv.sendCsv(reports, req.query.csvcol));
                } else {
                    res.end(csv.sendCsv(reports));
                }
                return context.skip;
            } else {
                sendReportAs(res, as, context.instance[0]);
                return context.skip;
            }
        }
        return context.continue;
    });

    imageResource.read.fetch.before(function (req, res, context) {
        if ('as' in req.query) {
            context.options.attributes = [...this.resource.attributes];
            context.options.attributes.push('png_base64_str');
        }
        return context.continue;
    });
    imageResource.read.send.before(function (req, res, context) {
        if ('as' in req.query) {
            if (req.query.as == 'img') {
                let base64Str = context.instance.png_base64_str;
                let img = Buffer.from(base64Str, 'base64');

                res.setHeader('Content-Type', 'image/png');
                res.setHeader('Content-Length', img.length);
                res.end(img);

                return context.skip;
            }
        }
        return context.continue;
    });

    userResource.list.fetch.before(function (req, res, context) {
        return context.continue;
    });

    userResource.create.fetch(function (req, res, context) {
        let userUuid = uuid.v4();
        req.body.uuid = userUuid;
        return context.continue;
    });

    userResource.delete.fetch(function(req, res, context) {
        console.log("<<<<<<< Deleting user >>>>>>>");
        return context.continue;
    });

    userResource.update.fetch(function(req, res, context) {
        console.log("<<<<<< Updating user >>>>>>");
        return context.continue;
    });
};
