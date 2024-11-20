#!/bin/bash
#======== ========= ========= ========= ========= ========= ========= ==========
# File: bteq_wrapper.bash
#
show_usage ()
{
cat <<-EOF
This script will read the input arguments from an ENV file, and run the 
specified SQL_FILE using the Teradata BTEQ utility.
 
Usage:
        $BASE -e ENV_FILE

where the required variables are

        SERVER 
                specifies the machine where the database is.
        USERNAME
        	specifies the username to connect to that database as.
        PASSWORD
                specifies the password for that user on that database.
        LOGMECH
		specifies the authentication mechanism.  The valid values
                are TD2 and LDAP.

	SQL_FILE specifies the name of the file holding the SQL to run.
	LOG_FILE specifies the name of the file holding the LOG file of results

        TEMP_DIR specifies the subdirectory where the temporary or log files
               will be written.  

EOF

}

# If we could use the TD Wallet, the follow comments would explain that...
#	        Connection to the Teradata server involves using the TD Wallet 
#                to retrieve the username and password.   The connection string
#                will look like this:
#		.LOGON $SERVER/\$tdwallet(u),\$tdwallet(p)
#                Therefore you will use the tdwallet add command to store 
#                values for the username (u) and password (p).
#                See also: http://developer.teradata.com/tools/articles/introducing-teradata-wallet
#======== ========= ========= ========= ========= ========= ========= ==========
# Check that bteq can be found in the path.

which bteq > /dev/null
RET=$?

if [ $RET -ne 0 ]; then
	echo "The bteq utility is not found in your path."
	echo "You might need add this to your PATH: /opt/teradata/client/13.10/bin"
	exit 1
fi
#======== ========= ========= ========= ========= ========= ========= ==========
BASE=`basename $0`

# Parse the command-line parameters
while getopts e:h option
do
        case $option in
                e) ENV_FILE=$OPTARG
                        ;;
                h) show_usage
                        ;;
                \?) show_usage
                        ;;
        esac
done

# Check that the user specified a SQL file as the first argument.

if [ "$ENV_FILE." = "." ]; then
	show_usage
	exit 2
elif [ ! -f $ENV_FILE ]; then
	echo "The ENV_FILE is not found."
	echo "Expected to find $ENV_FILE"
	exit 3
fi

. $ENV_FILE

#======== ========= ========= ========= ========= ========= ========= ==========
# Check that the server variable is set.  If not, ask for that input.

if [ "$SERVER." = "." ]; then
	echo "Please specify a value for the SERVER value."
	exit 4
elif [ "$USERNAME." = "." ]; then
	echo "Please specify the USERNAME value."
	exit 5
elif [ "$PASSWORD." = "." ]; then
	echo "Please specify the PASSWORD value."
	exit 6
elif [ "$LOGMECH." = "." ]; then
	echo "Please specify the LOGMECH value."
	exit 7
elif [ "$SQL_FILE." = "." ]; then
	echo "Please specify the SQL_FILE value."
	exit 8
elif [ "$LOG_FILE." = "." ]; then
	echo "Please specify the SQL_FILE value."
	exit 9
elif [ "$TEMP_DIR." = "." ]; then
	echo "Please specify the TEMP_DIR value."
	exit 10
elif [ ! -d $TEMP_DIR ]; then
	echo "Error: Cannot find TEMP_DIR"
	echo "Tried to find $TEMP_DIR"
	exit 11
fi
	
cd $TEMP_DIR

#======== ========= ========= ========= ========= ========= ========= ==========
# Before we run the script, check that we can successfully login.

bteq <<-EOF	> $LOG_FILE 2>&1
	.SET ERROROUT STDOUT
	.HEADING 'UNDERLINE OFF'
	.LOGMECH $LOGMECH;
	.LOGON $SERVER/$USERNAME,$PASSWORD
	.LOGOFF
	.QUIT
EOF


# If we could use the TD wallet, we would do this:
#	.LOGON $SERVER/\$tdwallet(u),\$tdwallet(p)

if [ `grep -c 'Error:' $LOG_FILE` -gt 0 ]; then
	cat $LOG_FILE
	echo
	echo "Failed to login successfully."
	echo 
	exit 12
else
	rm $LOG_FILE
fi
#======== ========= ========= ========= ========= ========= ========= ==========
# Finally, call bteq to run the SQL_FILE

bteq <<-EOF	| tail -n +28 						\
		| grep -v  '+---------+' 				\
		| egrep -v 'Exiting BTEQ|EOF on INPUT|logged off' 	\
		> $LOG_FILE
	.SET ERROROUT STDOUT
	.HEADING 'UNDERLINE OFF'
	.LOGMECH $LOGMECH;
	.LOGON $SERVER/$USERNAME,$PASSWORD
	.SET ECHOREQ OFF
	.SET MAXERROR 1
	select (current_timestamp (format 'MM-DD-YYYYbHH:MI:SS') (char(21))) "Date:",
		User "User:" ;
	.RUN FILE $SQL_FILE
	.LOGOFF
	.QUIT
EOF

# Use the -w switch to avoid misinterpreting the Liquibase changeset 
# attribute "failOnError:false"

# Warning: 9432 Immediately alter table to have a unique primary index
# That happens if they create a unique index with the same column as the non-
# unique primary index.

# We used to check for errors like this
# if [ `egrep -cwi 'Error|Failure|Warning' $LOG_FILE` -gt 0 ]; then

if [ `grep -c '*** RC (return code) = 0' $LOG_FILE` -eq 0 ]; then
	# cat $LOG_FILE
	# The parent process can manage displaying the results since
	# the output was tee'd

	# Please do not change this return code from 8, so that
	# OneApp can look for it.
	RET=8
else
	RET=0
fi

# rm $LOG_FILE

exit $RET
