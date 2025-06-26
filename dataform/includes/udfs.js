function getColumnAppName(gameColumn, lgoGames, lrtGames, unknownValue = '<unknown>', lgoGame = 'landlord-go', lrtGame = 'landlord-tycoon', trailingComma = ',') {
    let appName;

    if (lgoGames.includes(gameColumn)) {
        appName = lgoGame;
    } else if (lrtGames.includes(gameColumn)) {
        appName = lrtGame;
    } else {
        appName = unknownValue;
    }

    return `CASE WHEN ${gameColumn} IN (${lgoGames.map(game => `'${game}'`).join(', ')}) THEN '${appName}' ELSE '${unknownValue}' END as app_name${trailingComma}`;
}

function getColumnNullableId(columnName, alias = null) {
    const caseStatement = `
        CASE
            WHEN NULLIF(${columnName}, '') IS NOT NULL
                THEN CAST(${columnName} AS STRING)
            ELSE null
        END AS ${alias === null ? columnName : alias}
    `;
    return caseStatement.trim();
}

function getFQN(dataset, table, config) {

    console.log(config);
    const GCP = config["gcp"];
    if (!GCP){
        throw new Error(`GCP not found in config`);
    }
    const projectId = GCP["project"]["id"];
    const datasetConfig = config.sources[dataset];
    if (!datasetConfig) {
        throw new Error(`Dataset ${dataset} not found in config`);
    }
    const tableName = datasetConfig.tables[table];
    if (!tableName) {
        throw new Error(`Table ${table} not found in dataset ${dataset}`);
    }
    return `${projectId}.${datasetConfig.dataset}.${tableName}`;
}

function getConfig(){
    let env = 'dev';
    if(dataform.projectConfig.vars.env){
        env = dataform.projectConfig.vars.env;
    }

    const {environment} = require(`includes/configs/${env}.js`);

    return environment
}

module.exports = {
    getColumnAppName,
    getColumnNullableId,
    getFQN,
    getConfig
};
