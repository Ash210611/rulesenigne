#!/usr/bin/env bash
set -e

export WORKSPACE=$PWD

PROPERTY_FILE=$WORKSPACE/Rules_Engine.properties
touch "$PROPERTY_FILE"

INI_FILE=$WORKSPACE/un_re/delete_me.ini
export NUM_FAILED=0

export XML_DIR=$WORKSPACE/dummy_solutions/data_ops_blueprints_tdv_ddl
export XML_FILE=dev.changelog.xml
export LOG_FILE=$WORKSPACE/Rules_Engine.log
export XML_FILENAME=$XML_DIR/$XML_FILE

poetry run run_rules -i ${INI_FILE} -v | tee Rules_Engine.log
