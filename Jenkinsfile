@Library('epf') _

String containerImage  = 'registry.cigna.com/enterprise-devops/aws-d-megatainer'
String containerVersion = '1.0.14-2'

String cloud_name = "evernorth-qp-gov-solns-openshift-devops1"
String eks_cloud_name = "evernorth-qp-gov-solns-eks-prod"

def rules_engine_container = [
        image: "registry-dev.cigna.com/maa-dataops-rules-engine/maa-dataops-rules-engine-build",
        version: "1.0.1",
        cpu: 2000,
        memory: 2000
]

boolean RUN_HELLO = params.RUN_HELLO ?: false
boolean RUN_RE = params.RUN_RE ?: false

//==============================================================================
def PARAMETER_LIST = [
	string(
        	defaultValue: 'projectname1',
                description: 'Enter the folder(s) name you would like to deploy separated by commas (NO SPACES). DEFAULT: folder1',
                name: 'FOLDER_TO_DEPLOY',
                trim: true),
	booleanParam(defaultValue: true, name: 'RUN_UN_RE')
	] 

//==============================================================================
def hello_script = '''
        set +x
        printf "%80s\n" " " | tr ' ' '='

	echo "Hello, World."
	echo

        printf "%80s\n" " " | tr ' ' '='
	echo "Directory listing:"
	ls -la
	echo

        printf "%80s\n" " " | tr ' ' '='
	echo "Environment variables:"
	env | sort
	echo
        '''

//==============================================================================
def hello_phase = [
	freestyleType      : 'Hello',
	branchPattern      : 'dev.*|test|main|feature.*|release',
	sdlcEnvironment    : "Dev",
	container          : [
				image: "${containerImage}",		// The Megatainer
                                version: "${containerVersion}",
                                cpu: 2000,
                                memory: 2000
		],
	script: hello_script
]

//==============================================================================
def un_re_script = '''
        set +x
        printf "%80s\n" " " | tr ' ' '='
	export PATH=.:$PATH

	echo "Installing UN_RE..."

	chmod +x UN_RE.sh
	UN_RE.sh -install

	ls -la /opt/app-root/lib/python3.9/site-packages
	find /opt/app-root -name 'UN_RE*'
	find /opt/app-root -name 'UN_RE_LE*'

        printf "%80s\n" " " | tr ' ' '='
	echo "Executing UN_RE..."

	XML_DIR=$WORKSPACE
	XML_FILENAME=$XML_DIR/liquibase.xml

	UN_RE.sh -execute DATABRICKS 1 $XML_DIR $XML_FILENAME

        '''

//==============================================================================
def un_re_phase = [
	freestyleType      : 'UN_RE',
	branchPattern      : 'dev.*|test|main|feature.*|release',
	container          : rules_engine_container,
	sdlcEnvironment    : "Dev",
	extraCredentials: [
                usernamePassword(
                        credentialsId: 'quay_dev_user_pass',
                        usernameVariable: 'UN_RE_DMV_USER',
                        passwordVariable: 'UN_RE_DMV_PSWD'
                )
        ],
    script: '''
    set -ex

    export WORKSPACE=$PWD

    PROPERTY_FILE=$WORKSPACE/Rules_Engine.properties
    touch "$PROPERTY_FILE"

    #INI_FILE=un_re/delete_me.ini
    INI_FILE=$WORKSPACE/un_re/my_rules.ini
    touch "$INI_FILE"
    echo "[UN_RE]" >> ${INI_FILE}
    echo "PARALLEL_DEGREE = 8" >> ${INI_FILE}
    echo "VERBOSE = 1" >> ${INI_FILE}
    echo "INPUT_SQL_DIR = $WORKSPACE/dummy_solutions/data_ops_blueprints_tdv_ddl/tables" >> ${INI_FILE}
    echo "XML_FILENAME = $WORKSPACE/dummy_solutions/data_ops_blueprints_tdv_ddl/dev.changelog.xml" >> ${INI_FILE}
    echo "RULES_ENGINE_TYPE = TERADATA_DDL" >> ${INI_FILE}

    cat $INI_FILE

    export NUM_FAILED=0

    export XML_DIR=$WORKSPACE/dummy_solutions/data_ops_blueprints_tdv_ddl
    export XML_FILE=dev.changelog.xml
    export LOG_FILE=$WORKSPACE/Rules_Engine.log

    poetry env use 3.9
    poetry install
    poetry run run_rules -i ${INI_FILE} -v | tee ${LOG_FILE}
    '''

// 	script: un_re_script

]

//==============================================================================
if (!RUN_HELLO) {
    hello_phase.branchPattern = "ignored_branch_not_to_run"
}
else {
    currentBuild.displayName = env.BUILD_NUMBER + " Without UN_RE"
}

if (!RUN_RE) {
    un_re_phase.branchPattern = "ignored_branch_not_to_run"
}
else {
    currentBuild.displayName = env.BUILD_NUMBER + " With UN_RE"
}


ansiColor('xterm') {
    cignaBuildFlow {
        additionalProperties = [
                parameters([
                        booleanParam(
                                defaultValue: true,
                                name: 'RUN_HELLO',
                                description: 'If true then run hello world from megatainer/cloudkit.'
                        ),
                        booleanParam(
                                defaultValue: true,
                                name: 'RUN_RE',
                                description: 'If true then run rules engine from quay image.'
                        ),
                ])
        ]
        cloudName = "${cloud_name}"
        gitlabConnectionName = 'cigna_github'
        phases = [hello_phase, un_re_phase]
    }
}




// steve stuff
// // Setup the list of phases depending on the user's input parameters
//
// def MISSING_PARAMS = false
//
// if ( params.RUN_UN_RE == null ){
// 	MISSING_PARAMS = true
// 	}
//
// def run_these_phases = []
//
// run_these_phases += hello_phase
//
// if ( !MISSING_PARAMS ) {
// 	if ( params.RUN_UN_RE == true) {
// 		currentBuild.displayName = env.BUILD_NUMBER + " With UN_RE"
// 		run_these_phases += un_re_phase
// 		}
// 	else	{
// 		currentBuild.displayName = env.BUILD_NUMBER + " Without UN_RE"
// 		}
// 	}
// else 	{
// 	currentBuild.displayName = env.BUILD_NUMBER + " Creating Params"
// 	}
//
// //==============================================================================
// // use AnsiColor plug-in - https://plugins.jenkins.io/ansicolor/
// ansiColor('xterm') {
//     cignaBuildFlow {
//
// 	additionalProperties = [
//         	parameters(PARAMETER_LIST)
//     		]
//
//     cloudName = "${cloud_name}"
//     gitlabConnectionName = 'cigna_github'
//     phases = run_these_phases
//
//     }   // End of cignaBuildFlow
// }   // End of ansiColor