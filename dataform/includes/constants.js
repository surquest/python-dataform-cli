const config = {
    "gcp": {
        "project": {
            "id":"analytics-data-mart"
        },
    },
    "sources": {
        "appsflyer": {
            "dataset": "adm_appsflyer_reporting",
            "tables": {
                "installs": "installs",
                "events": "events"
            }
        },
        "ironsource": {
            "dataset": "adm_ironsource_raw",
            "tables": {
                "impressions": "impression"
            }
        },

    }
};

module.exports = {
    config
}