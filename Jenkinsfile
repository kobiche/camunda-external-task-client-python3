#!groovy

@Library('cib-pipeline-library@master') _


standardPythonPipeline(
    uiParamPresets: ['CREATE_PYTHON_ARTIFACT': true,
                     'DEPLOY_ANY_BRANCH_TO_REPOSITORY': true,
                     "UNIT_TESTS": false],
    versionfile: 'camunda/VERSION',
    helmChartPaths: [],
    gitTagPrefix: "v"
)
