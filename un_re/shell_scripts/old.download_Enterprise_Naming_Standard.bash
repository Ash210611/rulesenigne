#!/bin/bash
#==============================================================================
# Purpose: See the show_usage function below.
#
# This script will use wget to download the specified file.
# 
#==============================================================================
show_usage ()
{
cat <<-EOF

This script will download the Enterprise Naming Standard file

Running the script with no input parameters will display this
usage explanation.

Usage: `basename $0` -l LOG_FILE

where   -l will write the internal log messages to the specified LOG_FILE
	and LOG_FILE indicates the filename to write them in

EOF
exit 1
}
#======== ========= ========= ========= ========= ========= ======== ==========
# Display the usage explanation if no input parameters are specified.

if [ $# -eq 0 ]; then
        show_usage
fi

export SPECIFIED_LOG=0
export LOG_FILE

#======== ========= ========= ========= ========= ========= ======== ==========
# Read the command-line options

while getopts hl: option
do
        case $option in
                h)      show_usage
                        ;;
		l)	LOG_FILE=$OPTARG
			SPECIFIED_LOG=1
			# echo "Will write output to $OPTARG"
			;;
                *)      show_usage
                        ;;
        esac
done

#======== ========= ========= ========= ========= ========= ======== ==========
DIR=`dirname $0`
cd $DIR
DIR=`pwd`

TARGET_DIR=../resources
cd $TARGET_DIR
TARGET_DIR=`pwd`

cd $DIR
BASE=`basename $0`

#======== ========= ========= ========= ========= ========= ======== ==========
# Validate the input arguments


if [ $SPECIFIED_LOG -eq 0 ]; then
	echo "Error: Please specify a filename where to log the results"
	echo
	show_usage
	exit 1
fi

#======== ========= ========= ========= ========= ========= ======== ==========
export URL='https://centralhub.cigna.com/project/epms12282/dataarch/Shared%20Documents/SEARCH%20Abbreviations%201.0.xlsm?web=1'
# The Sharepoint URL fails, saying unauthorized

export URL='https://confluence.sys.cigna.com/download/attachments/112594290/Enterprise%20Naming%20Standard%202015.xlsx?version=7&modificationDate=1564581549000&api=v2'
export DOWNLOADED_NAME=$DIR/"Enterprise Naming Standard 2015.xlsx"

export URL='https://centralhub.cigna.com/project/epms12282/dataarch/Shared%20Documents/SEARCH%20Abbreviations%201.0.xlsm?web=1'

export USERNAME=SVP_HIVE_DDL_RE
export PASSWORD=NHMbDy3ayj7_6qY3R_Ka
TOKEN=`echo -ne "$USERNAME:$PASSWORD" | base64 --wrap 0`

export TARGET_FILE=$DIR/"Enterprise Naming Standard 2015.xlsx"

# Use wget to download it.
# The -nc option willprevent clobbering the original, although,
# that should be impossible here since we previously
# checked for existence
# -q is the quiet option, turns off wget output

# wget -q -nc $URL
# curl -s -u "$USERNAME:$PASSWORD" -X GET --header 'Accept: application/text' $URL  | tee $LOG_FILE
# curl -X GET $URL -H "Authorization: Basic $TOKEN"
if [ -f "$TARGET_FILE" ]; then
	rm "$TARGET_FILE"
fi

# curl -O -J $URL -H "Authorization: Basic $TOKEN" >$LOG_FILE 2>&1 
wget $URL --no-check-certificate -O "$TARGET_FILE" 	\
	--user=$USERNAME 				\
	--password=$PASSWORD >$LOG_FILE 2>&1

if [ ! -f "$TARGET_FILE" ]; then
	echo "         Unable to download the Enterprise Naming Standard file." | tee -a $LOG_FILE
	exit 8
else
	# echo "         Used wget to download the Enterprise Naming Standard file." | tee -a $LOG_FILE
	mv "$TARGET_FILE" $TARGET_DIR/Enterprise_Naming_Standards_2015.xlsx
	# ls -la $TARGET_DIR
fi

#===============================================================================
# Cleanup


echo "               `date`"				>> $LOG_FILE
echo "               Done downloading ENS file."	>> $LOG_FILE

exit $RET


