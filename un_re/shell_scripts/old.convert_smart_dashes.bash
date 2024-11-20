# While this is able to be called standalone, this should be called from 
# file_cleaner.py.
# Convert "smart" dashes to ASCII dashes.
#===============================================================================
LOCAL_SCRIPT_NAME=$1
TMP_FILE=$2

if [ ! -f $LOCAL_SCRIPT_NAME ]; then
        echo "ERROR        : LOCAL_SCRIPT_NAME is not found."
        echo "LOCAL_NAME   : $LOCAL_SCRIPT_NAME"
        echo "TMP_FILE     : $TMP_FILE"
        exit 1

# elif [ "$VERBOSE." != "." ]; then
#         if [ $VERBOSE -eq 1 ]; then
#                 echo "LOCAL_NAME   : $LOCAL_SCRIPT_NAME"
#                 echo "TMP_FILE     : $TMP_FILE"
#         fi

fi


        cat $LOCAL_SCRIPT_NAME  |
	sed "s/\o342\o200\o223/-/g"  > $TMP_FILE

        diff $LOCAL_SCRIPT_NAME $TMP_FILE > /dev/null
        RET=$?

        if [ $RET -ne 0 ]; then
                echo "               Notice: Converted smart quotes to ASCII quotes."
                mv $TMP_FILE $LOCAL_SCRIPT_NAME
        else
                rm $TMP_FILE
        fi

