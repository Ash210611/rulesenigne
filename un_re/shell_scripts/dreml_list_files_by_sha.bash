#!/bin/bash
#======== ========= ========= ========= ========= ========= ========= ==========
# Purpose: 	See Usage explanation below for complete description of what 
# 		this does.
#
#======== ========= ========= ========= ========= ========= ========= ==========
# History of dreml_list_files_by_sha.bash
# 11/20/2018	SWC Wrote it
#
#======== ========= ========= ========= ========= ========= ========= ==========
show_usage ()
{
cat <<-EOF

This script will get a list of files that were changed by the Git SHA.

Usage:
        $BASE -d DIR -l LOG_FILE -s SHA

where
        DIR 
                indicates the directory of the Git repo to check.

        LOG_FILE 
                will contain the list of files that were changed

        SHA 
                indicates which Git SHA commit to check

EOF
}
#======== ========= ========= ========= ========= ========= ========= ==========
export DIR=""
export SHA=""
export LOG_FILE=""

# Parse the command-line parameters
if [ $# -eq 0 ]; then
	show_usage
	exit 1
fi

while getopts d:hl:s: option
do
        case $option in
		d) 	DIR=$OPTARG
			;;
                h) 	show_usage
			exit 2
                        ;;
		l)	LOG_FILE=$OPTARG
			;;
		s)	SHA=$OPTARG
			;;
                \?) 	show_usage
			exit 3
                        ;;
		*)	show_usage
			exit 4
			;;
        esac
done

#======== ========= ========= ========= ========= ========= ========= ==========
# Validate the environmental variables.

if [ "$DIR." = "." ]; then
	echo "Error: The DIR variable is unspecified."
	exit 5 
elif [ ! -d $DIR ]; then
	echo "Error: DIR is not found."
	echo "Tried to find $DIR"
	exit 6
fi

if [ "$SHA." = "." ]; then
	echo "Error: The SHA variable is unspecified."
	exit 7
elif [ "$LOG_FILE." = "." ]; then
	echo "Error: The LOG_FILE variable is unspecified."
	exit 8
fi

touch $LOG_FILE

if [ ! -f $LOG_FILE ]; then
	echo "Error: Cannot find the LOG file."
	echo "Tried to find $LOG_FILE"
	exit 9
fi

#======== ========= ========= ========= ========= ========= ========= ==========
RET=0

cd $DIR

git diff-tree --name-only -r $SHA > $LOG_FILE 2>&1
RET=$?

exit $RET
