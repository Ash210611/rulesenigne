// Antrl grammar for Teradata v16.20
// 
// This successfully compiles with Antlr 4.7 and parses all test cases so far.
//
// Adapted from this grammar for SqlBase referenced by Jeremy Davis:
//	http://git.sys.cigna.com/cima/Valids/blob/ValidsContol/valids.parser/src/main/antlr/SqlBase.g4
//
// History: 
// 06/22/2021   SWC     Started adding syntax for TD 16.20 now that we are 
//                      upgraded from TD15.10
//
// 03/02/2021   SWC	Clarified usage of the boolean_comparison and 
//                      boolean_condition rules.
//
// 09/04/2020	SWC	Added the Drop Stats statement
//
// 07/20/2020 	SWC	Added the TRANSLATE_CHK function
//
// 07/09/2020	SWC	Added some alter partitioning rules
//
// 12/04/2018	SWC	Added the optional windowing function to the 
//			sum_function rule.
//
// 10/03/2018	SWC	Created rule ct_kind to enable attributes to be specified
//			in different orders.
//			Adjusted the rules for update with a from clause.
//
// 03/15/2018	SWC	Found a test case that defines a PRIMARY KEY.   While the
//			documentation shows that a constraint_name is required.
//			TD does not require in practice.
//
//			Also improved the rule that checks for Foreign Key
//			references.
//
// 01/23/2018	SWC	Updated the compress_what rule to allow compression
//			of TIMESTAMP STRING.
//
// 05/22/2017	SWC 	started adapting and extending it for TD15.
//
//==============================================================================
// Key Rules
// primaryExpression	line 1966
// query		line 1823
// table_column		line 687
//
//==============================================================================

grammar TD16;

root 
		: single_statement* EOF
		;

single_statement
		: v1=statement
			{System.out.println();
			 System.out.println("Parsed single_statement      : " + $v1.text);
			 System.out.println("========= ========= ========= ========= ========= =====");}
			// NOTE: That text is searched by DREML
		| DOT v2=dot_command
			{System.out.println ();
			 System.out.println ("Parsed dot_command           : " + $v2.text);
			 System.out.println ("========= ========= ========= ========= ========= =====");}
    		;

statement 	: sql_command
		| help_procedure
		| help_session
		| set_session
		;

sql_command	: comment_on
			// For Statement Type, see details
		| create_table
			{System.out.println ("Statement Type               : CREATE TABLE");}
		| alter_table			// Eventually, rather than list these 
			// For Statement Type, see details.
		| create_view
			{System.out.println ("Statement Type               : CREATE VIEW");}
		| begin_transaction		// alphabetically, it would be more 
		| call_procedure		// efficient to list them in order
			{System.out.println ("Statement Type               : CALL");}
		| close_cursor			// of probability.
		| collect_stats
			{System.out.println ("Statement Type               : COLLECT STATS");}
		| create_constraint
		| create_index
			{System.out.println ("Statement Type               : CREATE INDEX");}
		| create_procedure
		| create_table_as
			// For Statement Type, see details.
		| create_type
		| default_database
			{System.out.println ("Statement Type               : DEFAULT DATABASE");}
		| delete_statement
			{System.out.println ("Statement Type               : DELETE");}
		| drop_index
		| drop_stats
			{System.out.println ("Statement Type               : DROP STATS");}
		| drop_table
			{System.out.println ("Statement Type               : DROP TABLE");}
		| drop_view
			{System.out.println ("Statement Type               : DROP VIEW");}
		| end_transaction
		| execute_immediate
		| grant_permission
			{System.out.println ("Statement Type               : GRANT");}
		| insert_into
			{System.out.println ("Statement Type               : INSERT");}
		| merge_into
			{System.out.println ("Statement Type               : MERGE");}
		| open_cursor
		| set_operation_delimited	// Regular Select queries are set operations.
			{System.out.println ("Statement Type               : SELECT");}
		| show_column
		| show_function
		| show_statistics
		| show_table
		| show_type
		| rename_table
			{System.out.println ("Statement Type               : RENAME TABLE");}
		| update_basic
			{System.out.println ("Statement Type               : UPDATE");}
		;

//=============================================================================
// Alter Table
// Not specifying much of this, because Cigna Rules Engine blocks Alter Table
// commands for CCW.  However, I need to be able to parse the command so that 
// we can send it to the Rules Engine and be rejected there.

alter_table			// TD15.10 SQL Data Definition Language, p175
		: alter_table_basic 
		// alter_table_join
		// alter_table_revalidation
		// alter_table_release_rows
		;

	alter_table_basic
		: ALTER TABLE 	// All Alter Table commands start with those 2 words
			(v1=database_name DOT)? v2=table_name
			alter_table_basic_alternations
			DELIMITER
                        {
                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
			}
		;

	alter_table_basic_alternations
		: alter_table_columns (COMMA alter_table_columns)*
			{
			System.out.println ("Statement Type               : ALTER TABLE COLUMN");
			}
		| alter_table_constraints (COMMA alter_table_constraints)*
			{
			System.out.println ("Statement Type               : ALTER TABLE CONSTRAINT");
			}
		| alter_table_option_list
			{
			System.out.println ("Statement Type               : ALTER TABLE OPTIONS");
			}
		| alter_table_other
			{
			System.out.println ("Statement Type               : ALTER TABLE OTHER");
			}
		;

	alter_table_columns
		: ADD v1=table_column (INTO column_name)?
			// The alter-table column specifier is the same as the
			// create_table column specifier
			{
			System.out.println("Found AT Add column          : " + $v1.text); }
			// That output is checked by the Rules Engine in DREAM
		| ADD v2=column_name (datatype_attribute)*
			// For example ADD Column_C NULL COMPRESS
			// I don't find the syntax diagram allows that.
			// Nevertheless TD uses it to modify attributes,
			// not add a column exactly.
			{System.out.println("Found AT Add col dt_attribute: " + $v2.text); }
			// The DREAM Rules Engine looks for all these Found AT signals
		| DROP v6=identifier
			{System.out.println("Found AT Drop Column         : " + $v6.text); }
		| RENAME v7=column_name (AS | TO) column_name
			{System.out.println("Found AT Rename Column       : " + $v7.text); }
		| LEFT_PAREN v8=table_column (COMMA table_column)* RIGHT_PAREN (INTO column_name)
			{System.out.println("Found AT Other               : " + $v8.text); }
		// Grouping the following 2 alternatives to modify or drop the PI, 
		// so that those commands will get the same backup strategy as
		// the other ALTER TABLE COLUMN commands
		| modify_primary
		| MODIFY NO PRIMARY INDEX? alter_partitioning?
		;

	alter_table_constraints
		: ADD  (CONSTRAINT v3=constraint_name)?
			FOREIGN KEY v3_1=column_list v3_2=references
			{
			System.out.println("Found AT Add Foreign Key     : " + $v3.text);
			System.out.println("Foreign key column list      : " + $v3_1.text);
			System.out.println("Foreign key references       : " + $v3_2.text);
			}
		| ADD (CONSTRAINT v4=constraint_name)?
			CHECK LEFT_PAREN v4_1=boolean_condition RIGHT_PAREN
			{
			System.out.println("Found Check Constraint       : " + $v4_1.text); 
			}
		| DROP (CONSTRAINT v5=constraint_name)?
			FOREIGN KEY v5_1=column_list v5_2=references
			{
			System.out.println("Found AT Drop Foreign Key    : " + $v5.text);
			System.out.println("Foreign key column list      : " + $v5_1.text);
			System.out.println("Foreign key references       : " + $v5_2.text);
			}
		| DROP (CONSTRAINT v6=constraint_name)?
			{
			System.out.println("Found AT Drop Constraint     : " + $v6.text); 
			}
		;

	alter_table_option_list
		: COMMA alter_table_option (COMMA alter_table_option)*
		;

	alter_table_option
		: v1=alter_table_options
			{System.out.println("found ct_option              : " + $v1.text);}
		;

	alter_table_options	// This almost matches the Create Table option list
				// but is slightly different.
		: NO? FALLBACK PROTECTION?
		| WITH JOURNAL TABLE EQUALS qualifiedName
		| (NO | DUAL)? BEFORE? JOURNAL
		| ON COMMIT (DELETE | PRESERVE) ROWS
					// Create table does not have that option
		| NO? LOG
		| (NO | DUAL | LOCAL | NOT LOCAL)? AFTER? JOURNAL
		| CHECKSUM EQUALS integrity_checking
		| DEFAULT FREESPACE
					// Create table does not have this option
		| FREESPACE EQUALS INTEGER_VALUE PERCENT?
		| merge_ratio
		| DATABLOCKSIZE EQUALS INTEGER_VALUE (BYTES | KBYTES | KILOBYTES)?
		| (MINIMUM | MAXIMUM | DEFAULT) DATABLOCKSIZE
		| BLOCKCOMPRESSION EQUALS block_compression_option
		| WITH NO? CONCURRENT? ISOLATED LOADING (FOR (ALL | INSERT | NONE))?
		;

	alter_table_other
		: normalize		// Same as the create table normalize below
		| DROP NORMALIZE
		| MODIFY alter_partitioning
		| FROM TIME ZONE EQUALS (PLUS_SIGN | MINUS_SIGN)? STRING
			(COMMA TIMEDATEWZCONTROL EQUALS INTEGER_VALUE)?
			(COMMA WITH TIME ZONE)?
		| (SET | RESET) DOWN
		// There are MANY more Alter Table options.
		// Only adding enough for now to test with.
		;

	modify_primary			// TD15.10 SQL Data Definition Language, p179
		: MODIFY (NOT? UNIQUE)? PRIMARY AMP? INDEX? (index_name | NOT NAMED)?
			column_list? alter_partitioning?
		;

	alter_partitioning
		: PARTITION BY alter_partitioning_level (COMMA alter_partitioning_level)*
			with_insert_delete?
		| alter_partitioning_add_drops (COMMA alter_partitioning_add_drops)*
			with_insert_delete?
		| NOT PARTITIONED
		;

	with_insert_delete
		: WITH ( (INSERT INTO? save_table) | DELETE)
		;

	save_table
		: table_name
		;
	alter_partitioning_add_drops
		: ADD range_expression
		| DROP range_expression (ADD range_expression)?
		;

	alter_partitioning_level
		: alter_partitioning_level_option (ADD constant?)
		;

	alter_partitioning_level_option
		// Notice how the options here are different than the options
		// used in the 'partition_level' rule for the Create Table statement
		: primaryExpression	// aka partitioning_expression
		| COLUMN (NO? AUTO_COMPRESS)?
		| COLUMN (NO? AUTO_COMPRESS)? (ALL BUT)? column_partition
		;

	range_expression
		: RANGE range_expression_option
		// How to handle RANGE#Ln ?
		;

	range_expression_option
		: BETWEEN primaryExpression (AND primaryExpression)? (EACH range_size)?
			( (COMMA UNKNOWN) |
				no_range_or_unknown )?
		| no_range_or_unknown
		| UNKNOWN
		| WHERE primaryExpression
		;

	no_range_or_unknown
		: NO RANGE ((OR UNKNOWN) | (COMMA UNKNOWN))?
		;

//=============================================================================
// Rules for the Begin Transaction command
				// TD15.10 SQL Data Manipulation Language, p290

begin_transaction
		: BT | (BEGIN TRANSACTION)
		;

//=============================================================================
// Rules for Calling a stored procedure

call_procedure	: CALL qualifiedName 
			(LEFT_PAREN sproc_parameter (COMMA sproc_parameter)* RIGHT_PAREN)
			DELIMITER
		;

	sproc_parameter	
		: sproc_parameter_literal
		| sproc_parameter_variable
		| primaryExpression		// for example a function call like Coalesce
		;
	sproc_parameter_literal
		: STRING
		| INTEGER_VALUE
		| DECIMAL_VALUE
		| IDENTIFIER
		;
	sproc_parameter_variable
		: COLON identifier
		;

// This is too simple.  See the TD Syntax diagram. Need to specify In and Out parameters.

//=============================================================================
// Rules for the Close Cursor command
				// TD14 SQL Quick Reference, p323
close_cursor
		: CLOSE cursor_name DELIMITER
		;
//=============================================================================
// Rules for Collect Stats

collect_stats			// TD15.10 SQL Data Definition Language, p977
		: COLLECT (SUMMARY)? (STATISTICS | STATS) 
			collect_using?  
			collect_target? (COMMA collect_target)*
			collect_on 
			DELIMITER
		| COLLECT (SUMMARY)? (STATISTICS | STATS)
			ON? (TEMPORARY)? qualifiedName (COLUMN PARTITION)?  
				(FROM collect_from_option)?
			collect_target? (COMMA collect_target)*
				// I know the documentation does not show that
				// this sequence of clauses is allowed.
				// Nevertheless, it works, and people use it.
			DELIMITER
		;
collect_target	: (UNIQUE)? INDEX index_name
		| (UNIQUE)? INDEX index_name? ALL? LEFT_PAREN column_name (COMMA column_name)* RIGHT_PAREN 
			(ORDER BY (VALUES | HASH) LEFT_PAREN column_name RIGHT_PAREN )?
		| COLUMN collect_column_target (AS? statistics_name)?
		;

	collect_column_target 
		: collect_col_expression
		| statistics_name
		| LEFT_PAREN collect_col_expression (COMMA collect_col_expression)* RIGHT_PAREN
		;

	collect_col_expression 
		: column_name
		| primaryExpression   	// Should be an expression that we can 
					// collect stats on, if we were checking for that.
			collected_expression_datatype?
		| PARTITION
		;

	collected_expression_datatype
		: LEFT_PAREN
			v1=datatype 
				{System.out.println("collect_stats_datatype      : " + $v1.text);}
			(COMMA datatype_attribute)*
			RIGHT_PAREN
		;

	collect_using	: USING collect_using_option (AND collect_using_option)*
		; 

	collect_using_option : collect_using_option_type (FOR CURRENT)?
		;

	collect_using_option_type 
		: SAMPLE
		| SYSTEM SAMPLE
		| SAMPLE INTEGER_VALUE PERCENT
		| NO SAMPLE
		| SYSTEM THRESHOLD (PERCENT | DAYS)?
		| THRESHOLD number (PERCENT | DAYS)
		| NO THRESHOLD (PERCENT | DAYS)?
		| MAXINTERVALS INTEGER_VALUE
		| SYSTEM MAXINTERVALS
		| MAXVALUELENGTH INTEGER_VALUE
		| SYSTEM MAXVALUELENGTH
		;

collect_on	: ON (TEMPORARY)? v1=qualifiedName (COLUMN PARTITION)?  (FROM collect_from_option)?
		{
		System.out.println("Found table name             : " + $v1.text);
		}
		;

	collect_from_option : TEMPORARY? qualifiedName 
		(COLUMN collect_from_option_target)?
		(COMMA COLUMN collect_from_option_target)*
		;

	collect_from_option_target : column_name_or_partition
		| statistics_name
		| LEFT_PAREN column_name_or_partition (COMMA column_name_or_partition)* RIGHT_PAREN
		;

column_name_or_partition : column_name
		| PARTITION
		;

index_name	: identifier
		| LEFT_PAREN index_name RIGHT_PAREN;
statistics_name	: IDENTIFIER;

column_name	: identifier
		;

//=============================================================================
// Rules for the Comment On command

comment_on	  			// TD15.10 SQL Data Definition Language, p1061
	: COMMENT ON?
            	object_kind
		v1=comment_object_name
		((AS | IS)? v2=STRING)?
		DELIMITER
			{System.out.println("Found comment-on object      : " + $v1.text);
			 System.out.println("Found comment-on string      : " + $v2.text);}
			// NOTE: That text is used by DAMODRE
		;

	comment_object_name
		: qualifiedName
		| qualifiedName DOT IDENTIFIER
		;

	object_kind
		: COLUMN
			{System.out.println ("Statement Type               : COMMENT ON COLUMN");}
		| FUNCTION
		| GLOP SET
		| MACRO
		| METHOD
		| PROCEDURE
		| PROFILE
		| ROLE
		| TRIGGER
		| TYPE
		| VIEW
		| DATABASE
        	| FILE
        	| TABLE
			{System.out.println ("Statement Type               : COMMENT ON TABLE");}
        	| USER;

//=============================================================================
// Rules for the Create Constraint command

create_constraint			// TD15.10 SQL Data Definition Language, page 1029
		: CREATE CONSTRAINT v1=IDENTIFIER
			v2=datatype COMMA (NOT? NULL COMMA)?
			VALUES LEFT_PAREN name_value_pair (COMMA name_value_pair)* RIGHT_PAREN
			COMMA constraint_function (COMMA constraint_function)*
			DELIMITER
			{System.out.println("constraint_name              : " + $v1.text);
			 System.out.println("  constraint_datatype       : " + $v2.text);
			}
		;

	name_value_pair	: 
			v1=identifier COLON v2=simpleValue
			{System.out.println("constraint_pair_name         : " + $v1.text);
			 System.out.println("constraint_pair_value        : " + $v2.text);
			}
		;
		
	simpleValue
    		: NULL
    		| MINUS_SIGN? number
    		| STRING
    		| (DATE|TIMESTAMP) FORMAT? STRING
		;

	constraint_function
		: DELETE SYSLIB DOT identifier
		| INSERT SYSLIB DOT identifier
		| SELECT SYSLIB DOT identifier
		| UPDATE SYSLIB DOT identifier
		;
//=============================================================================
// rules for the Create Index command

create_index			// TD15.10 SQL Data Definition Language, p371
		:  create_one_index (create_mult_index)* create_index_end
		;

	create_one_index
		: (CREATE UNIQUE INDEX| CREATE INDEX) index_name? ALL? column_list ordering? loading?
		;

	create_mult_index
		: COMMA UNIQUE? INDEX index_name? ALL? column_list ordering? loading?
		;

	create_index_end
		: ON TEMPORARY? (database_name DOT)? table_name
			DELIMITER
		;

//=============================================================================
// Rules for the Create Procedure command

create_procedure		// TD15.10 SQL Data Definition Language, p497
		: (CREATE | REPLACE) PROCEDURE qualifiedName
			LEFT_PAREN proc_parameter? (COMMA proc_parameter)* RIGHT_PAREN
			(DYNAMIC RESULT SETS INTEGER_VALUE)?
			(SQL SECURITY proc_privilege_option)?
			proc_statement+
				// The delimiter follows each proc_statement
		;

	proc_parameter
		: (IN | OUT | INOUT)? parameter_name datatype
		;

	proc_privilege_option
		: CREATOR
		| DEFINER
		| INVOKER
		| OWNER
		;
	proc_statement
		: v1=proc_conditional_statement
			{System.out.println("Proc conditional statement   : " + $v1.text); 
			 System.out.println(); 
			}
		| proc_assignment_statement
		| v2=sql_command
			{System.out.println("Proc sql command statement   : " + $v2.text); 
			 System.out.println(); 
			}

		| set_operation INTO local_variable_name (COMMA local_variable_name)* DELIMITER
			// I don't find that statement in the syntax diagram,
			// but it is needed for assigning local bind variables.

		| proc_prepare_statement
		| proc_fetch_statement
		| proc_leave_statement
		| (proc_label COLON)? proc_iteration_statement proc_label? DELIMITER
		| proc_diagnostic_statement
		| proc_compound_statement
		;

	proc_prepare_statement
		: PREPARE proc_statement_name FROM (STRING | IDENTIFIER) DELIMITER
		;

	proc_leave_statement
		: LEAVE proc_label DELIMITER
		;
	proc_label
		: IDENTIFIER
		;

	proc_fetch_statement
		: FETCH ((NEXT | FIRST)? FROM)? cursor_name INTO
			local_variable_name (COMMA local_variable_name)*
			DELIMITER
		;
	proc_diagnostic_statement
		: (SIGNAL | RESIGNAL) 
			( proc_condition_name | SIGNAL SQLSTATE VALUE? sqlstate_code )
			(SET proc_condition_information_item EQUALS INTEGER_VALUE)?
				// Should it equal an integer?
				// What is this item?
			DELIMITER
		| GET DIAGNOSTICS proc_diagnostic_what
			DELIMITER
		;

	proc_condition_information_item
		: IDENTIFIER
		;

	proc_diagnostic_what
		: identifier EQUALS identifier (COMMA identifier EQUALS identifier)*
		| EXCEPTION INTEGER_VALUE  
			identifier EQUALS identifier (COMMA identifier EQUALS identifier)*
		;

	proc_iteration_statement
		: WHILE boolean_condition DO proc_statement+ END WHILE
		| LOOP proc_statement+ END LOOP 
		| FOR IDENTIFIER AS (cursor_name CURSOR FOR)?
			cursor_specification
			DO proc_statement+ END FOR
		| REPEAT proc_statement+ 
			UNTIL boolean_condition END REPEAT
		;

	cursor_name
		: IDENTIFIER
		;
	cursor_specification
		: set_operation	// Is a cursor a simplified query?
				// Why does the syntax diagram refer to "other SELECT clauses"?
		;
	proc_conditional_statement
		: IF v1=boolean_condition THEN (proc_statement)+
			(ELSEIF boolean_condition THEN (proc_statement)+)*
			(ELSE (proc_statement)+)?
			END IF DELIMITER
				// The syntax diagram does not show the ending delimiter.
			{System.out.println("  conditional statement      : " + $IF.text + 
				' ' + $v1.text + ' ' + $THEN.text); 
			}
		// | CASE boolean_condition, todo
		;

	proc_assignment_statement
		: SET proc_assignment_target EQUALS proc_assignment_source DELIMITER
		;
	
	proc_compound_statement
		: identifier? BEGIN
			proc_local_declaration*
			proc_cursor_declaration*
			v1=proc_condition_handler*
			proc_statement*
			END identifier?
			DELIMITER
		;

	proc_cursor_declaration
		: DECLARE identifier (SCROLL | NO SCROLL)? CURSOR
			(WITHOUT RETURN | 
			 	WITH RETURN ONLY? (TO (CALLER | CLIENT))?)?
			FOR  (	cursor_specification 
					(FOR ((READ ONLY) | UPDATE))? 
				| proc_statement_name)
			(PREPARE proc_statement_name FROM (STRING | IDENTIFIER))?
			DELIMITER
		; 

	proc_condition_handler
		: DECLARE identifier CONDITION      proc_condition_handler_for?
		| DECLARE (CONTINUE | EXIT) HANDLER proc_condition_handler_for? 
		;

	proc_condition_handler_for
		: FOR proc_condition_handler_for_what DELIMITER?
		;

	proc_condition_handler_for_what
		: proc_condition_handler_for_what_alt1 
			(COMMA proc_condition_handler_for_what_alt1)*
			proc_handler_action_statement
		| proc_condition_handler_for_what_alt2
			(COMMA proc_condition_handler_for_what_alt2)*
		| proc_condition_handler_for_what_alt1 
			(COMMA proc_condition_handler_for_what_alt1)*
		;

	proc_handler_action_statement
		: proc_statement
			// Could be a single statement, or a compound statement.
			// Certain types of single statements would not be valid by themselves,
			// like local vars, cursors, and handler declarations.
		;
	proc_condition_handler_for_what_alt1
		: SQLSTATE VALUE? sqlstate_code 
		;

	proc_condition_handler_for_what_alt2
		: SQLEXCEPTION
		| SQLWARNING
		| NOT FOUND
		| proc_condition_name
		;
	proc_local_declaration
		: DECLARE proc_variable_name 
			(COMMA proc_variable_name)* 
			datatype (DEFAULT (NULL | STRING | number))?
			DELIMITER
		| DECLARE proc_condition_name CONDITION (FOR sqlstate_code)?
			DELIMITER
				// I'm not sure what valid sqlstate_codes would be
		;
	local_variable_name	: COLON IDENTIFIER 	// for a bind variable
				| IDENTIFIER ;		// for a parameter reference
	proc_statement_name	: IDENTIFIER ;
	proc_variable_name 	: IDENTIFIER ;
	proc_condition_name 	: IDENTIFIER ;
	sqlstate_code 		: IDENTIFIER 
				| INTEGER_VALUE;
	proc_assignment_target	: IDENTIFIER ;
	proc_assignment_source	: primaryExpression ;

//=============================================================================
// rules for the Create Table command

create_table	 			// TD15.10 SQL Data Definition Language, p21
		: (CT | CREATE ct_kind* TABLE)
			(v1=database_name DOT)? v2=table_name
			(COMMA v3=ct_option_list)?
      			LEFT_PAREN tableElement (COMMA tableElement)*  RIGHT_PAREN
			v5=ct_index_clause? (COMMA? v6=ct_index_clause)*
			on_commit_clause?
			DELIMITER
			{
			if ($v1.text != null) {
				System.out.println("Found database identifier    : " + $v1.text);
				}
			System.out.println("Found table name             : " + $v2.text);
			}
		;

	tableElement 			// TD15.10 SQL Data Definition Language, p22
		: v1=table_column
			{System.out.println("TableElement.alt1            : " + $v1.text);
			}
		| (COLUMN | ROW)? LEFT_PAREN v2=table_column (COMMA table_column)* RIGHT_PAREN 
			(NO? (AUTOCOMPRESS | AUTO COMPRESS))?
			{System.out.println("TableElement.alt2            : " + $v2.text);
			}
		| PERIOD FOR period_name 
			LEFT_PAREN period_begin_column 
				COMMA period_end_column RIGHT_PAREN
		| normalize_option
		| v3=table_constraint
			{System.out.println("table_constraint             : " + $v3.text);
			}
		| user_defined_constraint
    		;

	ct_kind
		: v1=table_set_type
			{System.out.println("  Found table set type       : " + $v1.text);
			}
			// That text is used by DREML
		| temporariness
		;

create_table_as				// TD15.10 SQL Data Definition Language, p27
		: (CT | CREATE ct_kind* TABLE)
			(database_name DOT)? v1=table_name
			(COMMA ct_option_list)?
			column_list?
			AS v4=ctas_source
				(v2=with_data_and_stats_clause | v3=with_data_clause)
			ct_index_clause? (COMMA? ct_index_clause)*
			on_commit_clause?
			DELIMITER
			{
			System.out.println("Found table name             : " + $v1.text);
			if ($v2.text != null) {
				System.out.println ("Statement Type               : BACKUP TABLE");
				System.out.println ("  Source Table               : " + $v4.text);
			} else 	{
				System.out.println ("Statement Type               : CREATE TABLE AS SELECT");
				if ($v3.text != null) {
					System.out.println("with_data_clause             : " + $v3.text);
				}
			}
			}
		;

with_data_and_stats_clause
		: WITH DATA AND STATS
		;
with_data_clause
		: WITH NO? DATA (AND NO? (STATISTICS | STATS))?
		;

ctas_source	: qualifiedName
		| LEFT_PAREN 
			SELECT (ASTERISK | (column_name (COMMA column_name)* ) )
			FROM v1=qualifiedName 
			where_clause? 
			group_by_clause?
			RIGHT_PAREN
			{
			System.out.println("Found relation source        : " + $v1.text);
			// NOTE: That text is searched by DREML
			}
		| LEFT_PAREN 
			set_operation 
			RIGHT_PAREN
		; 
normalize_option: NORMALIZE (ALL BUT column_list)? ON column_name (ON overlap_condition)?
		;

overlap_condition
		: OVERLAPS 
		| MEETS OR OVERLAPS
		| OVERLAPS OR MEETS
		;

table_constraint: 	// TD 15.10 Data Definition Language, p26
			// That page shows the constraint_name is required.
			// However it is not required in practice.
		(CONSTRAINT constraint_name)? 
			v1=constraint_type
			{
			System.out.println("Found constraint type        : " + $v1.text);
			}
			// That text is used by DREML
		;

user_defined_constraint
		: constraint_name CONSTRAINT;

constraint_name	: identifier;

constraint_type	: (UNIQUE | PRIMARY KEY) column_list
		| CHECK LEFT_PAREN boolean_condition RIGHT_PAREN
		| FOREIGN KEY v1=column_list v2=references
			{
			System.out.println("Foreign key column list      : " + $v1.text);
			System.out.println("Foreign key references       : " + $v2.text);
			}
		;

references	: 	// TD15.10 Data Definition Language, p26
		REFERENCES (WITH NO? CHECK OPTION)?
			qualifiedName
			column_list?
		;

period_name	: identifier;

period_begin_column
		: column_name;

period_end_column
		: column_name
		| UNTIL_CHANGED
		;
table_column	: v1=column_name 
			v2=datatype 
			(v3=datatype_attribute)*
			{System.out.println("Found column_name            : " + $v1.text);
			 System.out.println("  datatype                   : " + $v2.text);
			 System.out.println("  datatype_attribute         : " + $v3.text);}
			// NOTE: That text is searched by DAMODRE
		;

datatype	: INT
		| INTEGER
		| SMALLINT
		| v1=BIGINT
			//{System.out.println("  found attribute:           : " + $v1.text);}
		| BYTEINT
		| DATE (AT (LOCAL | TIME ZONE (interval | interval_expression)))?
		| (CHARACTER | CHAR ) (LEFT_PAREN INTEGER_VALUE RIGHT_PAREN)?
		| (TIME | TIMESTAMP) (LEFT_PAREN fractional_seconds_precision RIGHT_PAREN)? (WITH TIME ZONE)?
		| INTERVAL YEAR precision? (TO MONTH)?
		| INTERVAL MONTH precision?
		| INTERVAL DAY precision? (TO (HOUR | MINUTE | SECOND fractional_seconds_precision?))?
		| INTERVAL HOUR precision? (TO (MINUTE | SECOND fractional_seconds_precision?))?
		| INTERVAL MINUTE precision? (TO SECOND fractional_seconds_precision?)?
		| INTERVAL SECOND precision? (COMMA fractional_seconds_precision?)?
		| PERIOD LEFT_PAREN DATE RIGHT_PAREN
		| PERIOD LEFT_PAREN (TIME | TIMESTAMP) precision? (WITH TIME ZONE)? RIGHT_PAREN
		| REAL
		| DOUBLE PRECISION
		| FLOAT (LEFT_PAREN INTEGER_VALUE RIGHT_PAREN)?
		| NUMBER ( LEFT_PAREN (INTEGER_VALUE | ASTERISK) (COMMA INTEGER_VALUE)? RIGHT_PAREN )?
		| (DEC | DECIMAL | NUMERIC) ( LEFT_PAREN INTEGER_VALUE (COMMA INTEGER_VALUE)? RIGHT_PAREN )?
			// DEC is not found on the syntax diagram, but TD Studio accepts it.
		| (BYTE | GRAPHIC) (LEFT_PAREN INTEGER_VALUE RIGHT_PAREN)?
		| (VARCHAR | CHAR VARYING | VARBYTE | VARGRAPHIC) LEFT_PAREN INTEGER_VALUE RIGHT_PAREN
		| LONG VARCHAR
		| LONG VARGRAPHIC
		| ((BLOB | BINARY LARGE OBJECT) | ( CLOB | CHARACTER LARGE OBJECT)) 
			(LEFT_PAREN INTEGER_VALUE (v2=IDENTIFIER)? RIGHT_PAREN)?
			{ 			// Better would be a string of "GKM"
			if ( $v2.text != null ) {
				String G = new String ("G");
				String K = new String ("K");
				String M = new String ("M");
				if (	! G.equals($v2.text) && 
					! K.equals($v2.text) && 
					! M.equals($v2.text) )
				System.out.println("Error: Size must be G, K, or M, not: " + $v2.text);
				}
			}
		| (XML | XMLTYPE)
		| JSON INTEGER_VALUE? (((CHARACTER | CHAR) SET character_set) | (STORAGE FORMAT (BSON | UBJSON)))?
//		| (SYSUDTLIB DOT)? (UDT _name | ST_Geometry | MBR | ARRAY_name | VARRAY_name)
		| (SYSUDTLIB DOT)? IDENTIFIER	// Could be a UDT - User Defined Type
		;

// ARRAY_name	: 'UNKNOWN';	// This is out of scope for now.
// MBR		: 'UNKNOWN';	// This is out of scope for now.
// ST_Geometry	: 'UNKNOWN';	// This is out of scope for now.
// VARRAY_name	: 'UNKNOWN';	// This is out of scope for now.

datatype_attribute
		: (UPPERCASE | UC)
		| NOT? (CASESPECIFIC | CS)
		| FORMAT v1=STRING
			{System.out.println("datatype_attribute.format   : " + $v1.text);}
		| TITLE v3=STRING
			{System.out.println("  column title               : " + $v3.text);}
		| NAMED identifier
		| default_kind
		| WITH DEFAULT
		| (CHARACTER | CHAR) SET character_set
		| NOT? NULL
		| NO COMPRESS
		| COMPRESS compress_what?
		| COMPRESS USING identifier (DOT identifier)? 
			DECOMPRESS USING identifier (DOT identifier)?
		| (CONSTRAINT identifier)? v2=datatype_constraint
			{System.out.println("Found data type constraint   : " + $v2.text);}
			// That text is used by DREML
		| GENERATED (ALWAYS | (BY DEFAULT)) AS v1=IDENTITY 
			(LEFT_PAREN generated_limit* RIGHT_PAREN)?
			{
			System.out.println("datatype_attribute.identity  : Found " + $v1.text);
			}
		;

	compress_what
		: compress_value
		| LEFT_PAREN compress_value (COMMA compress_value)* RIGHT_PAREN
		;

	compress_value
		: number
		| STRING
		| DATE STRING           // For example, DATE '0001-01-01'
		| NULL
		| LEFT_PAREN compress_what (COMMA compress_what)* RIGHT_PAREN
		| TIMESTAMP STRING
		| TIME STRING
		| unicode_literal
		;

	generated_limit
		: START WITH   	INTEGER_VALUE
		| INCREMENT BY 	INTEGER_VALUE
		| MINVALUE	(PLUS_SIGN | MINUS_SIGN)? INTEGER_VALUE
		| NO MINVALUE
		| MAXVALUE	INTEGER_VALUE
		| NO MAXVALUE
		| NO? CYCLE
		;

datatype_constraint
		: UNIQUE
		| PRIMARY KEY
		| CHECK boolean_condition
		| v1=references
			{
			System.out.println("Foreign key references       : " + $v1.text);
			}
		;

default_kind	: DEFAULT  (STRING | number)
		| DEFAULT USER
		| DEFAULT DATE STRING
		| DEFAULT TIME STRING
		| DEFAULT TIMESTAMP STRING
		| DEFAULT NULL
		| DEFAULT CURRENT_DATE
		| DEFAULT CURRENT_TIME
		| DEFAULT CURRENT_TIMESTAMP (LEFT_PAREN precision RIGHT_PAREN)?
		;

character_set	: UNICODE
		| LATIN
		;

fractional_seconds_precision
		: INTEGER_VALUE;

precision	: INTEGER_VALUE;

ct_option_list	: ct_option (COMMA ct_option)*
		;

	ct_option	: v1=ct_options
			{System.out.println ("Found regulated option       : " + $v1.text);}
			// 5/5/2023 SWC They want to regular all options now.
		;

	ct_options
		: FALLBACK PROTECTION?
		| NO v1=FALLBACK PROTECTION?
		| WITH JOURNAL TABLE EQUALS qualifiedName
		| NO? LOG
		| (NO | DUAL)? BEFORE? JOURNAL
		| (NO | DUAL | LOCAL | NOT LOCAL)? AFTER? JOURNAL
		| CHECKSUM EQUALS integrity_checking
		| FREESPACE EQUALS INTEGER_VALUE PERCENT?
		| merge_ratio
		| DATABLOCKSIZE EQUALS INTEGER_VALUE (BYTES | KBYTES | KILOBYTES)?
		| (MINIMUM | MAXIMUM | DEFAULT) DATABLOCKSIZE
		| BLOCKCOMPRESSION EQUALS block_compression_option
		| WITH NO? CONCURRENT? ISOLATED LOADING (FOR (ALL | INSERT | NONE))?
		| MAP EQUALS v2=map_name
			// {System.out.println("Found regulated option       : MAP = " + $v2.text);}
			// Does LQBPP remove all these options?
		;

	map_name	// See TD V16.20 SQL Data Definition Language Syntax, p23
		: IDENTIFIER
		;

	integrity_checking
		: ON
		| OFF
		| DEFAULT
		| NONE		// NONE is deprecated, nevertheless, it is still allowed.
		| ALL           // ALL is not documented, nevertheless it is allowed
		;

	block_compression_option
		: DEFAULT
		// AUTOTEMP -- I need a syntax diagram for how to specify this.
		| MANUAL
		| NEVER
		;
	merge_ratio	
		: DEFAULT MERGEBLOCKRATIO
		| MERGEBLOCKRATIO EQUALS INTEGER_VALUE PERCENT?
		| NO MERGEBLOCKRATIO
		;

ct_index_clause	: ct_index_pi
		| ct_index_npi
		| ct_index_pai
		| ct_index_si
		| partition_by_clause
		;

    ct_index_pi
        : v2=ct_index_unique? PRIMARY INDEX v1=index_name? column_list
		{System.out.println("Found primary index          : " + $v1.text);
		 System.out.println("  uniqueness                 : " + $v2.text);
		}
		// NOTE: That text is used by DREML
        ;

    ct_index_npi
        : NO PRIMARY INDEX
		{
		System.out.println("Found regulated option       : NO PRIMARY INDEX"); 
		}
		// NOTE: That text is used by DREML
        ;

    ct_index_pai
        : PRIMARY AMP INDEX? v1=index_name? column_list
		{System.out.println("Found primary amp index      : " + $v1.text);}
		// NOTE: That text is used by DREML
        ;

    ct_index_si
        : v2=ct_index_unique? INDEX v1=index_name? column_list loading?
		{System.out.println("Found index                  : " + $v1.text);
		 System.out.println("  uniqueness                 : " + $v2.text);
		}
		// NOTE: That text is used by DREML
        | INDEX v1=index_name? ALL? column_list ordering? loading?
		{System.out.println("Found index                  : " + $v1.text);}
		// NOTE: That text is used by DREML
        ;

//    ct_index_partition
//        : partition_by_clause
//        ;

    ct_index_unique
        : UNIQUE
        ;

table_set_type 	: MULTISET
    		| SET
    		;

temporariness	: GLOBAL TEMPORARY
			{
			System.out.println("Found database identifier    : GLOBAL_TEMPORARY");
			}
		| VOLATILE
			{
			System.out.println("Found database identifier    : VOLATILE");
			}
		;

column_list 	: LEFT_PAREN identifier (COMMA identifier)* RIGHT_PAREN
    		;

partition_by_clause
		: PARTITION BY v=partition_by_expression
			{System.out.println("partition_by_expression      : " + $v.text);}
		;

partition_by_expression
        : LEFT_PAREN? partition_level (COMMA partition_level)* RIGHT_PAREN?
        ;

//partition_by_expression
//		: v=partition_level (COMMA partition_level)*
//			{System.out.println("partition_level              : " + $v.text);}
//		| LEFT_PAREN partition_by_expression RIGHT_PAREN
//		;

partition_level	: COLUMN (NO? AUTO_COMPRESS)? (ADD constant)?
		| COLUMN (NO? AUTO_COMPRESS)? (ALL BUT)? column_partition (ADD constant)?
		| CASE_N 
			LEFT_PAREN 
			boolean_condition
				(COMMA (boolean_condition | partition_no_case))*
			RIGHT_PAREN
		| RANGE_N
			LEFT_PAREN
			test_expression BETWEEN v=partition_range
			(COMMA partition_range_list)* (COMMA partition_no_range)?
			RIGHT_PAREN
			{System.out.println("partition_range              : " + $v.text);}
		;

	test_expression
		: primaryExpression
		| column_name;

	partition_range
		: v1=primaryExpression AND (v2=primaryExpression | ASTERISK) (EACH r=range_size)?
			{System.out.println("primaryExpression_1          : " + $v1.text);
			 System.out.println("  primaryExpression_2        : " + $v2.text);
			 System.out.println("  range_size                 : " + $r.text);}
		| ASTERISK AND (primaryExpression | ASTERISK)
		| partition_range_list;

	partition_no_range
		: NO RANGE
		| NO RANGE OR UNKNOWN
		| NO RANGE COMMA UNKNOWN
		| UNKNOWN;

	partition_range_list
		: partition_range_list_part_1
			partition_range_list_part_2*
			partition_range_list_part_3?
		;

	partition_range_list_part_1
		: primaryExpression (AND primaryExpression)? (EACH range_size)?
		| ASTERISK          (AND primaryExpression)?
		;

	partition_range_list_part_2
		: COMMA primaryExpression (AND primaryExpression)? (EACH range_size)?
		;

	partition_range_list_part_3
		: COMMA primaryExpression AND (primaryExpression | ASTERISK) (EACH range_size)?
		;

	range_size
		: number
		| INTERVAL (INTEGER_VALUE | STRING) interval_type
		;

partition_no_case
		: NO CASE
		| NO CASE OR UNKNOWN
		| NO CASE COMMA UNKNOWN
		| UNKNOWN;

constant	: INTEGER_VALUE		//? Is that the right definition for a constant?
		| STRING
		;

column_partition: LEFT_PAREN (COLUMN | ROW)? (column_name | column_list) (NO? AUTO_COMPRESS)? RIGHT_PAREN
		;

loading		: WITH NO? LOAD IDENTITY
		;

ordering	: ORDER BY (VALUES | HASH)?  (LEFT_PAREN column_name RIGHT_PAREN)
		;

on_commit_clause: ON COMMIT (DELETE | PRESERVE) ROWS
		;
//=============================================================================
// Rules for the Create Type command

create_type	  			
		: create_type_distinct		DELIMITER
		| create_type_structured	DELIMITER
		;

create_type_distinct			// TD15.10 SQL Data Definition Language, p692
		:	CREATE TYPE
			(SYSUDTLIB DOT)?
			v1=udt_name AS datatype 
			((CHARACTER | CHAR) SET server_character_set)?
			FINAL
			{System.out.println("create_type_distinct.name    : " + $v1.text);}
		;			// There is a LOT more syntax to add to this rule.

create_type_structured 			// TD15.10 SQL Data Definition Language, p681
		:	CREATE TYPE
			(SYSUDTLIB DOT)?
			v1=udt_name AS
			LEFT_PAREN create_type_attribute (COMMA create_type_attribute)* RIGHT_PAREN
			INSTANTIABLE? 
			NOT FINAL
			create_type_structured_method
			{System.out.println("create_type_structured.name  : " + $v1.text);}
		;			// There is a LOT more syntax to add to this rule.

	create_type_attribute
		: v1=attribute_name (udt_name | predefined_datatype ((CHARACTER | CHAR) SET server_character_set)?)
			{System.out.println("create_type_attribute.name   : " + $v1.text);}
		;

	udt_name	: identifier;
	attribute_name	: identifier;
	predefined_datatype
		: v1=datatype
			{System.out.println("predefined_datatype         : " + $v1.text);}
		;
	server_character_set
		: character_set;

	create_type_structured_method
		: (INSTANCE | CONSTRUCTOR)? METHOD (SYSUDTLIB DOT)? v1=method_name
			LEFT_PAREN cst_method_parameter (COMMA cst_method_parameter)* RIGHT_PAREN
			RETURNS (
				(datatype ((CHARACTER | CHAR) SET server_character_set)?)
				| ( (SYSUDTLIB DOT)? udt_name))
			(AS LOCATOR)?
			(CAST FROM (datatype | (SYSUDTLIB DOT)? udt_name) (AS LOCATOR)? )?
			(SPECIFIC (SYSUDTLIB DOT)? specific_method_name)?
			(SELF AS RESULT)?
			cst_method_clause*
			{System.out.println("cst_method_name              : " + $v1.text);}
		;

	method_name	: identifier;
	specific_method_name
			: identifier;

	cst_method_parameter
		: parameter_name (
			(datatype ((CHARACTER | CHAR) SET server_character_set)?)
			| ( (SYSUDTLIB DOT) udt_name))
			(AS LOCATOR)?
		;
			
	parameter_name : identifier;

	cst_method_clause
		: cst_language_clause
		| cst_SQL_data_access
		| cst_parameter_style
		;

	cst_language_clause
		: LANGUAGE v1=IDENTIFIER	// What other languages are allowed?
			{ 
			String s1 = new String ("C");
			if (! s1.equals($v1.text))
			System.out.println("Error: Language must be C, not: " + $v1.text);}
		;				// But do not make 'C' a token!
		
	cst_SQL_data_access
		: NO SQL;		// This is the only valid specification

	cst_parameter_style
		: SPECIFIC (SYSUDTLIB DOT)? specific_method_name
		| PARAMETER STYLE (SQL | TD_GENERAL)
		| NOT? DETERMINISTIC
		| CALLED ON NULL INPUT
		| RETURNS NULL ON NULL INPUT
		;
//=============================================================================
// Rules for the Create View or Replace View command

create_view				// TD15.10 SQL Data Definition Language, p329
		: (CREATE VIEW|CV|REPLACE VIEW) (v1=database_name DOT)? v2=table_name (column_list)? AS
			LEFT_PAREN?
		  	(locking_clause)? set_operation_in_view
			RIGHT_PAREN?
			DELIMITER
			{
                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
			System.out.println("Found view name              : " + $v2.text);
                        }
		;
					// the query in a view has the check option 
					// which a regular query doesn not have.

	locking_clause	: (LOCK | LOCKING) 	
					// LOCK is not in the syntax diagram.
					// Nevertheless TD Studio accepts it as valid.
			(lock_username | lock_database | lock_table | lock_view | lock_row) 
		  	(FOR | IN)? lock_type
		  	(MODE)? (NOWAIT)?
		;

	lock_username	: identifier;
	lock_database 	: DATABASE? identifier;
	lock_table 	: TABLE? qualifiedName;
	lock_view 	: VIEW? qualifiedName;
	lock_row 	: ROW;

	lock_type	
		: ACCESS
		| (EXCLUSIVE | EXCL)
		| SHARE
		| READ (OVERRIDE)?
		| WRITE
		| CHECKSUM
		| LOAD COMMITTED
		;

	set_operation_in_view	
		: set_operation_in_view UNION ALL? 	set_operation_in_view
		| set_operation_in_view MINUS 		set_operation_in_view
		| set_operation_in_view EXCEPT 		set_operation_in_view
		| set_operation_in_view INTERSECT	set_operation_in_view
		| query_in_view
		;

	query_in_view	: 
		(SEL | SELECT)		// The syntax diagram only shows SELECT.
					// Nevertheless TD Studio accepts SEL too.
		(DISTINCT | ALL)? 
        	(TOP number PERCENT?)?
		(WITH TIES)?
		projection_list
		(FROM relation (COMMA relation)*)?
		where_clause?
		group_by_clause?
		aggregate_filter_clause*// This rule includes the having and qualify clauses.
		(WITH CHECK OPTION)?	// This option is not in a regular 
					// query, only in a view query.
      		standard_order_by_clause?
      		(LIMIT limit=(INTEGER_VALUE | ALL))?
      		(APPROXIMATE AT confidence=number CONFIDENCE)?
    		;

		// Note that views cannot select with normalize like regular 
		//queries can.

//=============================================================================
// rules for the default DATABASE command

default_database			// TD15.10 SQL Data Definition Language, p767
		: DATABASE v1=database_name DELIMITER
			{System.out.println("Found database identifier    : " + $v1.text);}
			// NOTE: That text is used by DAMODRE
		;

//=============================================================================
// Rules for the DELETE statement.
// Note there is a basic form, and a join form.
// Starting with the basic form...
			// TD15.10 SQL Data Manipulation, p327

delete_statement: delete_basic
		| delete_join
		;
	
delete_basic	: (DELETE | DEL) 
			with_isolated_loading?
			correlation_name?
			FROM delete_from
			delete_where?
			DELIMITER
		;

delete_join	: (DELETE | DEL) 
			with_isolated_loading?
			correlation_name?
			(FROM delete_from (COMMA delete_from)*)?
			delete_where?
			DELIMITER
		;

	delete_from
		: v1=qualifiedName  (AS? correlation_name)?
		;
	correlation_name
		: qualifiedName
		;

	delete_where
		: ALL
		| WHERE boolean_condition;

	with_isolated_loading
		: WITH NO? CONCURRENT? ISOLATED LOADING;

//=============================================================================
// Rules for the Drop Index command

drop_index			// TD15.10 SQL Data Definition Language, p448
		: drop_index_by_name		DELIMITER
		| drop_index_by_definition	DELIMITER
		;

	drop_index_by_name
		: DROP INDEX qualifiedName ON TEMPORARY? qualifiedName
		;

	drop_index_by_definition
		: DROP INDEX 
			( index_name | 
				( LEFT_PAREN column_name (COMMA column_name)* RIGHT_PAREN) )
			( ORDER BY (VALUES | HASH)? (LEFT_PAREN column_name RIGHT_PAREN)? )?
			ON TEMPORARY? qualifiedName
		;

//=============================================================================
// Rules for the Drop Stats command

drop_stats			// TD15.10 SQL Data Definition Language, p1016
		: DROP (STATISTICS | STATS | STAT)
			drop_stats_specific_target? (COMMA drop_stats_specific_target)*
			ON? qualifiedName
			DELIMITER
		| DROP (STATISTICS | STATS | STAT)
			ON? qualifiedName
			drop_stats_specific_target? (COMMA drop_stats_specific_target)*
				// I know the doc says the ON clause should
				// come last, but this does work, and people
				// do write it this way.
			DELIMITER
		;

	drop_stats_specific_target
		: drop_stats_specific_index
		| drop_stats_specific_column
		;

	drop_stats_specific_index
		: UNIQUE? INDEX qualifiedName? ALL? 
			LEFT_PAREN column_name (COMMA column_name)* RIGHT_PAREN
			( ORDER BY (VALUES | HASH)? LEFT_PAREN column_name RIGHT_PAREN )?
		;
	drop_stats_specific_column
		: COLUMN column_name (AS? statistics_name)?
		| COLUMN PARTITION
		| COLUMN LEFT_PAREN ( (column_name (AS? statistics_name)?)? | PARTITION)
			(COMMA ( (column_name (AS? statistics_name)?)? | PARTITION) )*
			 RIGHT_PAREN
		| COLUMN statistics_name
		;
		
//=============================================================================
// Syntax Rules for the Drop Table command

drop_table      : DROP TEMPORARY? TABLE qualifiedName ALL? DELIMITER;

//=============================================================================
// Rules for the Drop View command

drop_view	: DROP VIEW qualifiedName DELIMITER;

//=============================================================================
// Rules for the BTEQ dot commands

dot_command		// TD14.10 Basic Teradata Query Reference, page 124ff
		: dot_command_specific DELIMITER?
		;
	dot_command_specific
		:      COMPILE (FILE | DD | DDNAME) EQUALS? filename
                                (WITH (SPL | NOSPL)?)?
			{System.out.println ("Statement Type               : DOT COMPILE"); }
		| SET? ECHOREQ  (ON | OFF | ERRORONLY)?
			{System.out.println ("Statement Type               : DOT SET"); }
		| SET? ERRORLEVEL errorlevel_setting (COMMA errorlevel_setting)*
		| SET? ERROROUT (STDOUT | STDERR)
			{System.out.println ("Statement Type               : DOT SET");}

		|      EXIT (INTEGER_VALUE | ACTIVITYCO | ERRORCODE | ERRORLEVEL)?
		|      EXPORT RESET
		|      EXPORT export_target FILE EQUALS? filename
		| SET? FOLDLINE (ON | OFF)? (ALL | integer_list)?
		| SET? FORMAT   (ON | OFF)?
		|      GOTO identifier
			{System.out.println ("Statement Type               : DOT GOTO"); }
		|      IF (ERRORCODE | ACTIVITYCOUNT | ERRORLEVEL) 
				v1=comparison_operator INTEGER_VALUE
				THEN (DOT? dot_command | v2=sql_command | )
			{System.out.println ("Statement Type               : DOT IF");
			 System.out.println ("dot comparison_operator      : " + $v1.text);
			 System.out.println ("  sql_command                : " + $v2.text);}
		|      LABEL identifier
			{System.out.println ("Statement Type               : LABEL");}
		|      LOGMECH identifier
		|      LOGOFF
		|      LOGON v3=logon_option
			 	{System.out.println("Found logon option    :" + $v3.text);}
		| SET? MAXERROR INTEGER_VALUE?
		|      OS ECHO (QUOTED_IDENTIFIER (DOUBLE_RIGHT_ANGLE filename)? )?
			{System.out.println ("Statement Type               : DOT OS"); }
		|      OS RM filename
			{System.out.println ("Statement Type               : DOT OS"); }
		|      OS TOUCH filename
			{System.out.println ("Statement Type               : DOT OS"); }
		| SET? PAGELENGTH INTEGER_VALUE
		|      QUIT (INTEGER_VALUE | ACTIVITYCO | ERRORCODE | ERRORLEVEL)?
			{System.out.println ("Statement Type               : DOT QUIT");}
		|      REMARK (STRING | QUOTED_IDENTIFIER)
			{System.out.println ("Statement Type               : DOT REMARK");}
		|      RUN (FILE | DD | DDNAME) EQUALS? filename (COMMA SKIP_IT EQUALS INTEGER_VALUE)?
                | SET? SESSION (TRANSACTION | TRANS) (BTET | ANSI)
			{System.out.println ("Statement Type               : DOT SET");}
                | SET? SESSION CHARSET (STRING | INTEGER_VALUE)
			{System.out.println ("Statement Type               : DOT SET");}
		| SET? SIDETITLES  (ON | OFF)? (v4=valid_sidetitle_option)?
			{ 
			if ($v4.text == "ALL") {
			 	System.out.println("Found sidetitle option: ALL");
				} 
			else if ($v4.text != null) {
			 	System.out.println("Found sidetitle option:" + $v4.text);
				// It would be ideal to test if the values are in the valid range.
				}
			}
		| SET? SKIPLINE    (ON | OFF)? (ALL | v5=integer_list)?
			{System.out.println ("Statement Type               : DOT SET");
			 System.out.println ("dot skipline integer_list    : " + $v5.text);}
		| SET? TIMEMSG (DEFAULT | QUERY | NONE)?
		| SET? TITLEDASHES (ON | OFF)? (valid_titledashes_option)?
		| SET? WIDTH INTEGER_VALUE?
			{System.out.println ("Statement Type               : DOT SET"); }
		;

	errorlevel_setting
		: errorlevel_severity (COMMA errorlevel_severity)*
		| ON
		| OFF
		;
	errorlevel_severity
		: errorlevel_errno? SEVERITY INTEGER_VALUE?
		;
	errorlevel_errno
		: INTEGER_VALUE
		| LEFT_PAREN INTEGER_VALUE (COMMA INTEGER_VALUE)* RIGHT_PAREN
		| UNKNOWN
		;

	logon_option
		: tdpid logon_option
		| userid
		| userid COMMA
		| userid COMMA password (COMMA acctid)?
		| COMMA COMMA acctid
		;
	filename: qualifiedName
		;
	export_target
		: DATA
		| INDICDATA
		| REPORT (BOM | NOBOM | EJECT | NOEJECT)?
		| DIF    (BOM | NOBOM | DATALABELS)?
		;
	tdpid	: DECIMAL_VALUE DECIMAL_VALUE DECIMAL_VALUE SLASH
			// for a TCP/IP address, like '10.120' '.134' '.184'
		| IDENTIFIER (DOT IDENTIFIER)* SLASH
		;
	userid 	: IDENTIFIER
		| QUOTED_IDENTIFIER
		| DOLLAR IDENTIFIER LEFT_PAREN userid RIGHT_PAREN	// For calls to tdwallet
		;
	password: IDENTIFIER
		| QUOTED_IDENTIFIER
		| DOLLAR IDENTIFIER LEFT_PAREN password RIGHT_PAREN	// For calls to tdwallet
		;
	acctid	: IDENTIFIER
		| QUOTED_IDENTIFIER
		;
	integer_list	
		: INTEGER_VALUE (COMMA INTEGER_VALUE)*;

	valid_sidetitle_option
		: INTEGER_VALUE				// Should be 0
		| INTEGER_VALUE (COMMA INTEGER_VALUE)*	// Should be from 1 to 10
		| ALL
		;
	valid_titledashes_option
		: INTEGER_VALUE 			// Should be 0
		| INTEGER_VALUE (COMMA INTEGER_VALUE)*	// Should be from 1 to 10
		| ALL
		;

//=============================================================================
// Rules for the End Transaction command

end_transaction
		: ET | (END TRANSACTION)
		;

//=============================================================================
// rules for the Execute Immediate command

execute_immediate
		: EXECUTE IMMEDIATE identifier DELIMITER
		;

//=============================================================================
// Rules for the Grant command

// NOTE: Teradata has a LOT more options than this!
// We don't want to specialize in this right now.

grant_permission
		: GRANT grantText (COMMA grantText)* 
			ON tableName=qualifiedName 
			TO userName=qualifiedName
			DELIMITER
		; 

	grantText
		: INSERT
		| SELECT
		| UPDATE
		| DELETE
		;

//=============================================================================
// Rules for Help Procedure
                        // TD15.10 SQL Data Definition Language, p549
help_procedure  : HELP PROCEDURE qualifiedName
                        (ATTRIBUTES | ATTR | ATTRS)
                        DELIMITER?
                ;

//=============================================================================
// Rules for Help Session
			// TD15.10 SQL Data Definition Language, p899

help_session	: HELP SESSION CONSTRAINT? DELIMITER?;

//=============================================================================
// Rules for the Insert command
// NOTE:  INSERT has more options than I am specifying for now.
			// TD15.10 SQL Data Manipulation Language, p353

insert_into	: (INSERT | INS) 
			with_isolated_loading?
			INTO? 
			(database_name DOT)? table_name
			into_source
			DELIMITER
		;

	into_source
		: column_list? set_operation 
			// could have hash-by, local-order_by, and logging-errors here.

                | column_list
                     VALUES  LEFT_PAREN primaryExpression (COMMA primaryExpression?)* RIGHT_PAREN

                |    VALUES? LEFT_PAREN primaryExpression (COMMA primaryExpression?)* RIGHT_PAREN

			// The syntax diagram does not show that consecutive 
			// commas (ie. no expression) is allowed.  Nevertheless
			// TD will accept it as supplying a null value
			// in that position
		| DEFAULT VALUES
		;


//=============================================================================
// Rules for the MERGE command		// TD 15.10 SQL Quick Ref, p209

merge_into	: MERGE INTO? qualifiedName
			(AS? correlation_name)?
			USING (using_values | 
				using_subquery |
				using_source_table_name)
			ON boolean_condition
			when_matched_clause?
			when_not_matched_clause?
			merge_logging_clause?
			DELIMITER ;

	using_values
		: VALUES LEFT_PAREN using_expression (COMMA using_expression)* RIGHT_PAREN
			AS?
			qualifiedName column_list?  ;

	using_subquery
		: LEFT_PAREN query RIGHT_PAREN
			AS?
			qualifiedName column_list?  ;

	using_source_table_name
		: qualifiedName (AS? correlation_name)? column_list?  ;

	when_matched_clause
		: WHEN MATCHED THEN (UPDATE | UPD) 
			SET 	       qualifiedName EQUALS primaryExpression
	                        (COMMA qualifiedName EQUALS primaryExpression)* ;


	when_not_matched_clause
		: WHEN NOT MATCHED THEN (INSERT | INS)
			(VALUES | column_list VALUES)?
			LEFT_PAREN insert_expression
				(COMMA insert_expression)* RIGHT_PAREN ;

	insert_expression
		: qualifiedName
		| primaryExpression
		;

	using_expression
		: column_list
		;

	merge_logging_clause
		: TODO
		;
//=============================================================================
// Rules for the Rename table command

rename_table    : RENAME TABLE qualifiedName (TO|AS) qualifiedName 
			DELIMITER
		;

//=============================================================================
// Rules for the Update command

update_basic	: update_basic_no_from			DELIMITER
		| update_basic_with_from		DELIMITER
		| update_basic_with_joined_tables	DELIMITER
		;
		
	update_basic_no_from	
		: (UPDATE | UPD) with_isolated_loading? 
			qualifiedName (AS? identifier)?
			update_what
		;

	update_basic_with_from
		: (UPDATE | UPD) with_isolated_loading? table_name
			FROM update_from_what
			update_what
		;
	update_basic_with_joined_tables
		: (UPDATE | UPD) with_isolated_loading? table_name
			FROM       (table_name | set_operation) (AS? identifier)? 
			    (COMMA (table_name | set_operation) (AS? identifier)?)*
			update_what
		;

	update_from_what
		: table_name (AS? identifier)? 
		| set_operation  (identifier)?
		;
			
	update_what
		: SET          qualifiedName EQUALS primaryExpression
			(COMMA qualifiedName EQUALS primaryExpression)*
			(v1=where_clause | ALL)?
			{if ($v1.text != null)
				System.out.println("Found update where clause    : " + $v1.text);}
			// NOTE: That text is searched by DREML
		;
//=============================================================================
// Rules for the Set Session command
// This is the SQL set-session command, not the BTEQ set-session command

set_session	: (SET SESSION | SS) session_setting DELIMITER;

session_setting	: identifier EQUALS setting_value
		| ACCOUNT EQUALS STRING FOR (SESSION | REQUEST)
		| CALENDAR EQUALS identifier
		| COLLATION identifier
		| session_constraint (COMMA session_constraint)*
		| DATABASE IDENTIFIER
		| DATEFORM EQUALS (ANSIDATE | INTEGERDATE)
		| DEBUG FUNCTION qualifiedName (ON | OFF)
		| FOR NO? CONCURRENT? ISOLATED LOADING
		| FUNCTION TRACE (OFF | USING mask_string FOR TRACE? TABLE qualifiedName)
		| JSON IGNORE ERRORS (ON | OFF)
		| SEARCHUIFDBPATH EQUALS identifier (COMMA identifier)*
		| CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL isolation_level
		;

setting_value	: INTEGER_VALUE
		// Avoid referencing a generic expression here if possible
		;

session_constraint
		: CONSTRAINT EQUALS row_level_security_constraint 
			LEFT_PAREN (NULL | level_name | (category_name (COMMA category_name)*) ) RIGHT_PAREN
		;

row_level_security_constraint
		: identifier;
level_name	: identifier;
category_name	: identifier;
mask_string	: STRING;
isolation_level	: RU
		| READ UNCOMMITTED
		| SR
		| SERIALIZABLE
		;

//=============================================================================
// Rules for the Open Cursor command
			// TD14 SQL Quick Reference, p327

open_cursor	: OPEN cursor_name open_cursor_using?
			DELIMITER
		;

	open_cursor_using
		: USING IDENTIFIER (COMMA IDENTIFIER)*
		;

//=============================================================================
// query, aka SELECT

set_operation_delimited	
		: set_operation DELIMITER
		;

	set_operation
		: set_operation UNION ALL? 	set_operation
		| set_operation MINUS 		set_operation
		| set_operation EXCEPT 		set_operation
		| set_operation INTERSECT	set_operation
		| LEFT_PAREN set_operation RIGHT_PAREN
		| query (AS? IDENTIFIER)?
		;

query	: 			// TD15.10 SQL Data Manipulation Language, p14
		request_modifier* 
		(SELECT | SEL) (WITH DELETED ROWS)? 
		select_quantity?
		(column_name (COMMA column_name)*)?
		projection_list
		(FROM relation (COMMA relation)*)?
		with_clause?
		where_clause?
		group_by_clause?
		aggregate_filter_clause*
		(SAMPLE (WITH REPLACEMENT)? (RANDOMIZED ALLOCATION)? )?
		when_clause?
		expand_on?
		standard_order_by_clause?
		with_clause?
	| LEFT_PAREN query RIGHT_PAREN
	;

projection_list	: v1=ASTERISK
			{System.out.println("Projecting                   : ASTERISK");}
			// NOTE: That text is searched by DREML
		| v2=projected_expression (COMMA projected_expression)*
			{System.out.println("Projected_expression         : "+ $v2.text);}
		;

	// In the following rule, try to match the primaryExpression
	// without the first alternative trying to cast to data type
	// because that helps the primaryExpression look like
	// a function call, rather than a datatype which could a UDT
	// which could be anything.
	projected_expression	
		: v1=primaryExpression 
			((AS? v2=identifier) | 
				(INTO COLON IDENTIFIER))?  // for sproc Bind parameters
			{System.out.println("projected_expression.alt1    : " + $v1.text);
			 if ($v2.text != null)
			 	System.out.println("  expression_alias           :   AS " + $v2.text);
		 	System.out.println();
			}
			// NOTE: That text is searched by DREML
		| v3=primaryExpression 
			(LEFT_PAREN v4=datatype_attribute RIGHT_PAREN)? 
			(LEFT_PAREN v5=datatype           RIGHT_PAREN)?
			((AS? v6=identifier) | 
				(INTO COLON IDENTIFIER))?  // for sproc Bind parameters
			{System.out.println("projected_expression.alt2    : " + $v3.text);
			 if ($v4.text != null)
			 	System.out.println("  datatype_attribute         : " + $v4.text);
			 if ($v5.text != null)
			 	System.out.println("  datatype                   : " + $v5.text);
			 if ($v6.text != null)
			 	System.out.println("  expression_alias           : AS " + $v6.text);
		 	System.out.println();
			}
		| LEFT_PAREN v7=projected_expression RIGHT_PAREN (AS? identifier)?
			{System.out.println("projected_expression.alt3    : " + $v7.text);
			}
		| projected_expression over (AS? identifier)?
		| table_name DOT ASTERISK;

where_clause	: WHERE v1=boolean_condition ((AND | OR) boolean_condition)*
			{System.out.println("Found where clause           : " + $v1.text);}
			// NOTE: That text is searched by DREML
		;

	boolean_condition
		// This boolean_condition rule handles the nesting and 
		// grouping of boolean comparisons together.
		// Other rules should only use this rule for booleans.
		: LEFT_PAREN v1=boolean_condition RIGHT_PAREN
			{System.out.println("nested boolean_condition     : " + $v1.text);}
		| left=boolean_condition AND right=boolean_condition*
			{System.out.println("boolean_condition.left       : " + $left.text);
			 System.out.println("AND boolean_condition.right  : " + $right.text);}
		| left=boolean_condition OR right=boolean_condition*
			{System.out.println("boolean_condition.left       : " + $left.text);
			 System.out.println("OR boolean_condition.right   : " + $right.text);}
		| boolean_comparison
		;
	boolean_comparison
		// This boolean_comparison rule should return a single T/F value
		// Other rules should not refer to this directly, and should
		// refer to the nearby boolean condition, which handles
		// nesting and grouping comparisons in parentheses and AND/ORs.
		//
		// In other words, this rule is private to the boolean_condition rule
		: v1=primaryExpression expression_attributes? 
				v2=comparison_operator 
				v3=primaryExpression expression_attributes?
			{System.out.println("  left primaryExpression     : " + $v1.text);
			 System.out.println("  comparison_operator        : " + $v2.text);
			 System.out.println("  right primaryExpression    : " + $v3.text);
			}
		| v4=like_comparison
			{System.out.println("Finished like_comparison     : " + $v4.text);}
		| v5=in_comparison
			{System.out.println("Finished in_comparison       : " + $v5.text);}
		| primaryExpression NOT? BETWEEN primaryExpression AND primaryExpression
		| EXISTS '(' set_operation ')'
		| primaryExpression IS NOT? NULL
			{if ($NOT.text == null)
				System.out.println("boolean_comparison           : IS NULL");
			else
				System.out.println("boolean_comparison           : IS NOT NULL");}
		| NOT boolean_comparison
		| LEFT_PAREN v6=boolean_condition RIGHT_PAREN
			{System.out.println("Finished nested_comparison    : " + $v6.text);}
			// If this alternative is in the boolean_condition 
			// rule above, why is needed here??   I don't know!
			// But this is what it takes to handle some
			// super-complicated boolean expressions.
		| overlapping_expression OVERLAPS overlapping_expression
		;

	overlapping_expression
		: LEFT_PAREN primaryExpression COMMA primaryExpression RIGHT_PAREN
		| primaryExpression
		;
	
	like_comparison			// TD15.10 SQL Functions, Operators, Expressions, p822
		: primaryExpression      NOT? LIKE                 pattern_expression (ESCAPE escape_character)?
		| primaryExpression      NOT? LIKE (ANY|ALL|SOME)? v1=pattern_list    (ESCAPE escape_character)?
		| primaryExpression      NOT? LIKE (ANY|ALL|SOME)? set_operation      (ESCAPE escape_character)?
		| primaryExpression_list NOT? LIKE (ANY|ALL|SOME)? set_operation      (ESCAPE escape_character)?
		| primaryExpression_list NOT? LIKE (ANY|ALL|SOME)? pattern_list       (ESCAPE escape_character)?
		;
	in_comparison			// TD15.10 SQL Functions, Operators, Expression, p814
		: v2=primaryExpression in_operator LEFT_PAREN in_value ((COMMA | OR) in_value)* RIGHT_PAREN
			{System.out.println("Finished IN list v2 for      : " + $v2.text);}
			// NOTE: That text is searched by DREML
		| v1=primaryExpression in_operator primaryExpression 
			{System.out.println("Finished IN list v1 for      : " + $v1.text);}
		; 
	in_operator
		: NOT? v1=IN
			{System.out.println("Found IN operator            : " + $v1.text);}
		| NOT? IN ANY
		| NOT? IN SOME
		| EQUALS ANY
		| EQUALS SOME 		// ?? p815 says SOME5
		| LT GT ALL
		| NOT IN ALL
		;
	in_value: v1=number
			{System.out.println("Found IN-list value for      : " + $v1.text);}
			// NOTE: That text is searched by DREML
		| v2=STRING
			{System.out.println("Found IN-list value for      : " + $v2.text);}
			// NOTE: That text is searched by DREML
		;			// and Datetime literals?

	escape_character
		: STRING;		// Should this be more specific?

	primaryExpression_list
		: LEFT_PAREN primaryExpression (COMMA primaryExpression)* RIGHT_PAREN;

	pattern_expression
		: STRING;

	pattern_list
		: LEFT_PAREN pattern_expression (COMMA pattern_expression)* RIGHT_PAREN;
		
primaryExpression
		: v1=qualifiedName
			// {System.out.println("primaryExpression.qualifiedNm: " + $v1.text);}
		| STRING
		| number
		| COLON identifier      // a bind variable in a sproc
		| DATE STRING?
		| TIMESTAMP v2=STRING
                        {System.out.println("timestamp.string             : " + $v2.text);}
		| NULL

		| (identifier DOT)? PARTITION (HASH_SIGN identifier)?
		| DATABASE
		| USER
		| interval
              	| v3=current_timestamp

           	| cast_function

		| v4=period_function
                        {System.out.println("period_function              : " + $v4.text);}

                | left=primaryExpression CONCAT right=primaryExpression

		| v5=case_statement
                        {System.out.println("primaryExpression.case_stmt  : " + $v5.text);}

		| CURRENT_DATE
		| CURRENT_TIME

		| sum_function
		| trim_function
		| substring_function
		| rank_function
		| extract_function
		| translate_function
		| position_function
		| xmlagg_function
		| percentile_function

		| v8=functionCall	// All other functions lumped as function calls
                        {System.out.println("functionCall                 : " + $v8.text);}

		| LEFT_PAREN v6=primaryExpression
                        (COMMA? primaryExpression_attribute)*
                        RIGHT_PAREN 
			intervalField?
                        {System.out.println("primaryExpression.expression : " + $v6.text); }

		| l=primaryExpression (o=math_operator r=primaryExpression)+

		| LEFT_PAREN v9=set_operation RIGHT_PAREN intervalField?		
			// this is a subquery
                        {System.out.println("primaryExpression.query      : " + $v9.text);}
			// NOTE: That text is searched by DREML

		| LEFT_PAREN primaryExpression (COMMA primaryExpression)* RIGHT_PAREN	
			// this is a primaryExpression list

		| MINUS_SIGN primaryExpression
		| HEX_CONSTANT
		;

    sum_function
        : SUM LEFT_PAREN primaryExpression RIGHT_PAREN over?
        ;

	percentile_function	// TD15.10 SQL Function, Operations and Expressions, p900
				// This needs to be a separate rule because the syntax is not 
				// all kept within parentheses
		: ( PERCENTILE_CONT | PERCENTILE_DISC)
			LEFT_PAREN 
			percentile_value_expression
			RIGHT_PAREN
			WITHIN GROUP 
			LEFT_PAREN
			ORDER BY percentile_value_expression 
				(ASC | DESC)? (NULLS (FIRST | LAST))?
			RIGHT_PAREN
		;

	percentile_value_expression	// Should be between 0 and 1
		: number
		| primaryExpression
		;

	functionCall
        	: qualifiedName 
			LEFT_PAREN 
				ASTERISK                                     
			RIGHT_PAREN 
			over?
        	| v1=qualifiedName 
			LEFT_PAREN 
				(setQuantifier? v2=functionCall_parameter 
					(COMMA functionCall_parameter)*)? 	
			RIGHT_PAREN 
			primaryExpression_attribute?
			over?
			{System.out.println("  functionCall.name          : " + $v1.text);}
        	;
	functionCall_parameter
		: v1=primaryExpression primaryExpression_attribute*
			{System.out.println("  functionCall.parameter     : " + $v1.text);}
		;

	primaryExpression_attribute
		: v1=datatype 
			(COMMA primaryExpression_attribute)*
                        {System.out.println("primaryExpression.datatype  : " + $v1.text); }
		| v2=datatype_attribute
                        {System.out.println("primaryExpression.attribute  : " + $v2.text); }
		| LEFT_PAREN v3=primaryExpression_attribute RIGHT_PAREN
                        {System.out.println("parenthesized.pe..attribute  : " + $v3.text); }
		;
	xmlagg_function
	// http://www.info.teradata.com/HTMLPubs/DB_TTU_14_10/index.html#page/Teradata_XML/B035_1140_112A/chap9.06.87.html#ww15032764
		: XMLAGG LEFT_PAREN primaryExpression
			(ORDER BY column_name  (ASC | DESC)? (NULLS (FIRST | LAST))? 
			  ( COMMA column_name  (ASC | DESC)? (NULLS (FIRST | LAST))? )* )?
			(RETURNING (CONTENT | SEQUENCE))?
			RIGHT_PAREN
		;
	position_function		// TD15.10 SQL Functions, Operators, Expressions, p1088
					// Calling this out as a special function to avoid
					// confusion with an IN list.
		: POSITION LEFT_PAREN 
			primaryExpression	// Should be a string expression if we were checking types.
			IN
			primaryExpression
			RIGHT_PAREN
		;
			
	translate_function		// TD15.10 SQL Function, Operators, Expressions, p1115
		: (TRANSLATE | TRANSLATE_CHK)
			LEFT_PAREN
			primaryExpression	// Should be a character expression if we were checking types
			USING translate_using
			(WITH ERROR)?
			RIGHT_PAREN	
		| (TRANSLATE | TRANSLATE_CHK)
			LEFT_PAREN
			LEFT_PAREN primaryExpression RIGHT_PAREN
			USING translate_using
			(WITH ERROR)?
			RIGHT_PAREN	
		;

	translate_using			// There are a LOT more syntax options available here
		: LATIN_TO_UNICODE
		| UNICODE_TO_LATIN
		;
	extract_function		// TD15.10 SQL Functions, Operators, Expressions, p741
		: EXTRACT LEFT_PAREN 
			extract_function_part 
			FROM primaryExpression RIGHT_PAREN
		;

	extract_function_part		// This is a different list than the list for interval_type
		: YEAR
		| MONTH
		| DAY
		| HOUR
		| MINUTE
		| SECOND
		| TIMEZONE_HOUR
		| TIMEZONE_MINUTE
		;

	cast_function
		: CAST LEFT_PAREN cast_body RIGHT_PAREN
		;

	cast_body
		: v3=primaryExpression cast_as            
                        {System.out.println("primaryExpression.cast       : " + $v3.text);}
		| cast_date_expression     cast_as 
		| cast_interval_expression cast_as
		| LEFT_PAREN cast_body RIGHT_PAREN 
							// That handles extra nesting.
		;
	cast_interval_expression
		: primaryExpression 		// Should be an interval expression, if we were checking
			(if1=intervalField (TO if2=intervalField)?)?
		| LEFT_PAREN cast_interval_expression RIGHT_PAREN
		;

	cast_date_expression
		: primaryExpression cast_data_attribute
		| LEFT_PAREN cast_date_expression     RIGHT_PAREN
		;
	cast_as
		: AS cast_as_ansi_sql_type
		| AS cast_as_data_definition_list*
		| AS cast_data_attribute
		| LEFT_PAREN cast_as RIGHT_PAREN
		;

	cast_as_ansi_sql_type
		: v4=datatype
                         {System.out.println("  cast_as_datatype           : " + $v4.text);}
		;
	cast_as_data_definition_list 	// p496 says
					// "The new data type or data attributes or both for expression."
		: datatype
		| cast_data_attribute
		;
	cast_data_attribute		// TD15.10 SQL Functions, Operations, Expressions, p508
		: FORMAT STRING		// CAST can have some data type attributes, 
		| NAMED	identifier	// but not as many as Create Table can.
		| TITLE STRING
		| LEFT_PAREN cast_data_attribute RIGHT_PAREN
		;

	substring_function
		: SUBSTR LEFT_PAREN primaryExpression	// the Teradata substring version
			COMMA primaryExpression
			(COMMA primaryExpression)?
			RIGHT_PAREN
		| SUBSTRING LEFT_PAREN primaryExpression	// The ANSI substring version
			FROM primaryExpression
			(FOR primaryExpression)?
			RIGHT_PAREN
		;

	trim_function			// TD15.10 SQL Functions, Operators, Expressions, p1128
		: TRIM LEFT_PAREN 
			( (BOTH | TRAILING | LEADING) trim_expression? FROM)?
			server_character_set?
			v1=primaryExpression	// Would be a string expression if we were checking types.
			{System.out.println("  trimmed expression         : " + $v1.text);
                        }
			expression_attributes?
			RIGHT_PAREN
		;

	expression_attributes
		: expression_attribute (COMMA? expression_attribute)*
		| LEFT_PAREN expression_attributes RIGHT_PAREN
		;
	expression_attribute
		: datatype
		| datatype_attribute
		; 

	trim_expression
		: STRING			// Should be a single byte.
		| primaryExpression
		;

	case_statement			// TD15.10 SQL Functions, Operations, Expressions, p468
    		: CASE			// This is the Searched CASE expression 
			(WHEN v1=boolean_condition THEN v2=primaryExpression)+ 
			(ELSE primaryExpression)? END
			{System.out.println("case_statement.searched.when : " + $v1.text); 
			 System.out.println("case_statement.searched.then : " + $v2.text);}

			// Try to match the searched-case-statement first, to
			// avoid confusion from the valued Case expression

    		| CASE 			// This is the Valued CASE expression
			primaryExpression
			(WHEN v3=boolean_condition THEN v4=primaryExpression)+ 
			(ELSE primaryExpression)? END
			{System.out.println("case_statement.when          : " + $v3.text); 
			 System.out.println("case_statement.then          : " + $v4.text);}

    		| CASE 			// This is the Valued CASE expression variation 2
			primaryExpression
			(WHEN v5=primaryExpression THEN v6=primaryExpression)+ 
			(ELSE primaryExpression)? END
			{System.out.println("case_statement.when          : " + $v5.text); 
			 System.out.println("case_statement.then          : " + $v6.text);}
		;

	equation
		: l=primaryExpression o=math_operator r=primaryExpression
                        {System.out.println("Parsing equation left  side  : " + $l.text);
                         System.out.println("  math_operator              : " + $o.text);
                         System.out.println("  Parsing equation right side: " + $r.text);}
		;
	current_timestamp		// TD15.10 SQL Functions, Operators and Expressions, p293
		: CURRENT_TIMESTAMP 
			(LEFT_PAREN precision RIGHT_PAREN)?
			(LEFT_PAREN? FORMAT STRING RIGHT_PAREN?)?
			(LEFT_PAREN? datatype RIGHT_PAREN?)?
			(AT (LOCAL | (TIME ZONE)? (STRING | time_zone_expression)?))?
		| LEFT_PAREN current_timestamp RIGHT_PAREN
		;

	time_zone_expression		// Should return INTERVAL HOUR(2) TO MINUTE
		: primaryExpression
		;

	interval_expression		// TD15.10 SQL Functions, Operators, and Expressions, p710
		: interval_term
		| interval_expression (PLUS_SIGN | MINUS_SIGN) interval_term
		| LEFT_PAREN date_time_expression MINUS_SIGN date_time_term RIGHT_PAREN interval_start (TO interval_end)
		;

	date_time_expression		// TD15.10 SQL Functions, Operators, and Expressions, p701
		: date_time_term
		| interval_expression PLUS_SIGN date_time_term
		| date_time_expression (PLUS_SIGN | MINUS_SIGN) interval_term
		;

	date_time_term			// TD15.10 SQL Functions, Operators, and Expressions, p701
		: date_time_primary (AT (LOCAL | TIME ZONE interval_expression))?
		;

	date_time_primary		// TD15.10 SQL Functions, Operators, and Expressions, p702
		: column_name
		| STRING
		| functionCall
		| query			// should be a scalar subquery
		;

	interval_term		
		: interval_primary
		| interval_term (ASTERISK | SLASH) numeric_factor
		| numeric_term ASTERISK interval_factor
		;

	interval_factor			// TD15.10 SQL Functions, Operators, and Expressions, p711
		: (PLUS_SIGN | MINUS_SIGN) interval_primary
		;

	interval_primary		// TD15.10 SQL Functions, Operators, and Expressions, p712
		: column_name
		| STRING
		| functionCall
		| query			// should be a scalar subquery
		;
	numeric_term
		: numeric_factor
		| numeric_term (ASTERISK | SLASH) numeric_factor
		;

	numeric_factor
		: (PLUS_SIGN | MINUS_SIGN) numeric_primary
		;

	numeric_primary			// TD15.10 SQL Functions, Operators, and Expressions, p712
		: column_name
		| number
		| functionCall
		| query			// should be a scalar subquery
		| equation
		;
	period_function
		: BEGIN LEFT_PAREN primaryExpression RIGHT_PAREN
		| END   LEFT_PAREN primaryExpression RIGHT_PAREN 
				((IS NOT? UNTIL_CHANGED) | (IS NOT? UNTIL_CLOSED))?
		// There are more period functions available to specify here.
		;

	interval_start
		: intervalField; 

	interval_end
		: (MONTH | HOUR | MINUTE | SECOND) (precision);

	setQuantifier		// Is this used for Teradata function calls??
    		: DISTINCT
    		| ALL
    		;

	timeZoneSpecifier
    		: TIME ZONE interval  
    		| TIME ZONE STRING   
    		;

	over 				// TD15.10 SQL Functions, Operators and Expressions, p856
		: OVER LEFT_PAREN
        		(PARTITION BY partition+=primaryExpression 
				(COMMA partition+=primaryExpression)*)?
        		(ORDER BY standard_order_by_phrase (COMMA standard_order_by_phrase)*)?
			reset_clause?
        		(rowsWindowFrame | rowsBetweenWindowFrame)?
      			RIGHT_PAREN
    		;			// Does TD use ORDER BY like that?

	reset_clause 			// TD 15.10 SQL Functions and Expressions, p286
		: RESET WHEN boolean_condition
		;

	rowsWindowFrame
    		: ROWS (
			UNBOUNDED PRECEDING |
			primaryExpression PRECEDING |
			CURRENT ROW)
		;
	rowsBetweenWindowFrame		// TD15.10 SQL Functions, Operators and Expressions, p856
		: ROWS BETWEEN 
			(UNBOUNDED PRECEDING AND (
				UNBOUNDED FOLLOWING |
				primaryExpression PRECEDING |
				CURRENT ROW |
				primaryExpression FOLLOWING) 
			| primaryExpression PRECEDING AND (
				UNBOUNDED FOLLOWING |
				primaryExpression PRECEDING |
				CURRENT ROW |
				primaryExpression FOLLOWING)
			| CURRENT ROW AND (
				UNBOUNDED FOLLOWING |
				CURRENT ROW |
				primaryExpression FOLLOWING)
			| primaryExpression FOLLOWING AND (
				UNBOUNDED FOLLOWING |
				primaryExpression FOLLOWING)
			)
    		;

	rank_function
		: RANK          // TD15.10 SQL Functions, Operators, Expressions and Predicates, p909
				// This is the Teradata RANK function, not the Analytic RANK function
			LEFT_PAREN
			primaryExpression (ASC | DESC)?
			(COMMA primaryExpression (ASC | DESC)? )*
			RIGHT_PAREN
		| RANK          // TD15.10 SQL Functions, Operators, Expressions and Predictes, p906
			LEFT_PAREN RIGHT_PAREN OVER LEFT_PAREN
				// Note the rank function over clause is different than other
				// over clauses, by including a WITH TIES clause
			(PARTITION BY primaryExpression
				(COMMA primaryExpression)*)?
			(ORDER BY standard_order_by_phrase (COMMA standard_order_by_phrase)*)?
			reset_clause?
			(WITH TIES (LOW | HIGH | AVG | DENSE) )?
			RIGHT_PAREN
		;

//------------------------------------------------------------------------------
td_unpivot	: 	// TD15.10 SQL Functions, Operators, Expressions, and Predicates, p1173
			(TD_SYSFNLIB DOT)?
			TD_UNPIVOT LEFT_PAREN ON 
			(table_name | set_operation) 
			USING 
			VALUE_COLUMNS
				LEFT_PAREN value_columns_value (COMMA value_columns_value)* RIGHT_PAREN
			UNPIVOT_COLUMN
				LEFT_PAREN value_columns_value RIGHT_PAREN
			COLUMN_LIST
				LEFT_PAREN value_columns_value (COMMA value_columns_value)* RIGHT_PAREN
			( COLUMN_ALIAS_LIST
				LEFT_PAREN value_columns_value (COMMA value_columns_value)* RIGHT_PAREN
				(INCLUDE_NULLS EQUALS ('No' | 'Yes'))? 
				)?
			RIGHT_PAREN
		;
			
	value_columns_value
		: STRING
		// Are there more kinds of values?
		;
			
//------------------------------------------------------------------------------
unpivot		// TD 16.20 SQL Function, Operators, Expressions, and Predicates, p112

		: UNPIVOT 
			((INCLUDE | EXCLUDE) NULLS)?
			LEFT_PAREN 
			unpivot_source
			RIGHT_PAREN
			AS? table_name column_name_list_wrapped?
		;

	unpivot_source
		: column_name FOR column_name IN cname_literal_list_wrapped
		| column_name_list_wrapped FOR column_name IN cname_literal_list_wrapped
		;

	column_name_list_wrapped
		: LEFT_PAREN column_name_list RIGHT_PAREN
		;

	column_name_list
		: column_name (COMMA column_name)*
		;

	cname_literal_list_wrapped
		: LEFT_PAREN cname_literal_list RIGHT_PAREN
		;

	cname_literal_list
		: cname_literal_item (COMMA cname_literal_item)*
		;

	cname_literal_item
		: column_name (AS? cname_literal)?
		| column_name_list_wrapped (AS? cname_literal)?
		;

	cname_literal
		: STRING
		;

	// I see the syntax diagram for the UNPIVOT function, but I don't see
	// a syntax diagram that shows where a SELECT statement would call an
	// UNPIVOT function, so I'm not sure this grammar rule is placed right.

//------------------------------------------------------------------------------
standard_order_by_clause 
		: ORDER BY standard_order_by_phrase (COMMA standard_order_by_phrase)*
		;

	standard_order_by_phrase 
		: standard_order_by_expression (ASC | DESC)? (NULLS FIRST | NULLS LAST)?;

	standard_order_by_expression
		: column_position
		| column_name
		| qualifiedName
		| column_name_alias
		| primaryExpression  
		;

	column_name_alias		// Looks like a standard column name
		: column_name;

	column_position	: INTEGER_VALUE;	// for example 1, 2, or 3

select_quantity	: (DISTINCT | ALL | normalize) ( (table_name DOT)? ASTERISK)?
		| TOP number PERCENT? (WITH TIES)?;
		
normalize	: NORMALIZE ((ON MEETS OR OVERLAPS) | (ON OVERLAPS) (OR MEETS)?)?;

relation	: v=relationPrimary
			{System.out.println("Parsed relationPrimary       : " + $v.text);}
			// NOTE: That text is searched by DREML
			unpivot?
		| left=relation
      			CROSS JOIN right=relationPrimary
			{System.out.println("Found join type              : CROSS JOIN");}
			// NOTE: That text is searched by DREML
		| left=relation
      			join_type? JOIN rightRelation=relation ON v2=boolean_condition
			{System.out.println("Parsed relational join       : ");
			 System.out.println("  ON search condition        : " + $v2.text);
			}
			// NOTE: That text is searched by DREML
		| table_function
		| table_operator (AS? identifier)?
    		;

	relationPrimary
    		: v1=qualifiedName 		(AS? v2=identifier column_list?)?
			{System.out.println("Found relation source        : " + $v1.text);
			 System.out.println("  relationPrimary alias      :   " + $v2.text);
			// NOTE: That text is searched by DREML
			}
    		| '(' set_operation ')' 	(AS? identifier column_list?)?
    		| '(' relation ')'		(AS? identifier column_list?)?
    		;

// global_database
//        : DATABASE database_name DELIMITER
//        ;

database_name	: identifier
		| DATABASE_NAME
			// This 2nd alternative is very similar to the IDENTIFIER
			// rule, plus the possible suffix for ${env.id.upper}
		;

table_name	: identifier
		| qualifiedName        	// Table names could have a DB qualifier.
		;

    table_alias : IDENTIFIER;

	join_type	
		: INNER
		| v1=LEFT OUTER?
			{System.out.println("Found join type              : LEFT OUTER");}
			// Note that text is used by DREML
		| RIGHT OUTER?
			{System.out.println("Found join type              : RIGHT OUTER");}
			// Note that text is used by DREML
		| FULL  OUTER?
		;

	table_operator	
		: IDENTIFIER
		| td_unpivot
		;		// Leaving this incomplete at this time.

	derived_table_name
		: IDENTIFIER;

	table_function	
		: TABLE LEFT_PAREN function_name LEFT_PAREN tf_expression_list RIGHT_PAREN
			table_returns_clause?
			table_by_clause?
			RIGHT_PAREN
			AS? derived_table_name 
			(LEFT_PAREN column_list RIGHT_PAREN)?;

	tf_expression_list	: primaryExpression (COMMA primaryExpression)*;

	function_name
		: IDENTIFIER;

	table_returns_clause
		: RETURNS returns_something;

	returns_something
		: qualifiedName
		| LEFT_PAREN column_name_datatype_list RIGHT_PAREN;

	column_name_datatype_list
		: column_name_datatype (COMMA column_name_datatype)*;

	column_name_datatype
		: column_name datatype datatype_attribute?;

	table_by_clause	
		: LOCAL ORDER BY local_order_by_column (COMMA local_order_by_column)*
		| HASH BY column_list;

	local_order_by_column
		: column_name (ASC | DESC)? ((NULLS FIRST) | (NULLS LAST))?;

group_by_clause	: GROUP BY group_by_something (COMMA group_by_something)*;

	group_by_something
		: ordinary_grouping_set
		| empty_grouping_set
		| rollup_list
		| cube_list
		| grouping_sets_specification;

	ordinary_grouping_set		: primaryExpression;	
			// Leaving this incomplete at this time.

	empty_grouping_set		: primaryExpression;	// Leaving this incomplete at this time.
	rollup_list			: primaryExpression;	// Leaving this incomplete at this time.
	cube_list			: primaryExpression;	// Leaving this incomplete at this time.
	grouping_sets_specification	: primaryExpression;	// Leaving this incomplete at this time.

aggregate_filter_clause	
		: HAVING  v1=boolean_condition
                     {System.out.println("    having clause            : " + $v1.text);}
		| QUALIFY boolean_condition
		;
 
with_clause	: WITH with_expression_1 	(COMMA with_expression_1)*
			(BY with_clause_by	(COMMA with_clause_by)* )?
		;

	with_clause_by	: with_expression_2 (ASC | DESC)?;

	with_expression_1
		: primaryExpression
		;		// I suppose.

	with_expression_2
		: primaryExpression;		// I suppose.

when_clause	: fraction_list
		| WHEN boolean_condition THEN fraction_list (ELSE fraction_list)? END;

	fraction_list	
		: (fraction_description | count_description) 
			(COMMA (fraction_description | count_description))*;

	fraction_description
		: identifier;		// Unaware what that is!

	count_description
		: identifier;		// Unaware what that is!

expand_on	: EXPAND ON expand_expression AS? expand_column_alias
			BY (interval_literal | ANCHOR PERIOD? anchor_name (AT time_literal))
			FOR period_expression;

	expand_expression
		: primaryExpression;	// I suppose.

	interval_literal
		: STRING;	// I suppose.

	expand_column_alias
		: column_name;

	anchor_name
		: IDENTIFIER;

	time_literal
		: STRING;	// I suppose.

	period_expression
		: primaryExpression;	// I suppose.

request_modifier	
		: request_modifier_explain
		| request_modifier_locking
		// | request_modifier_using 	// No test cases available for this.
		| request_modifier_with;

	request_modifier_explain
		: (STATIC | DYNAMIC)? EXPLAIN (IN XML NODDLTEXT?)?;

	request_modifier_locking
		: locking_clause locking_clause*;

	request_modifier_using
		: primaryExpression;	// I suppose.

	request_modifier_with
		: WITH with_something (COMMA with_something)*;

	with_something	
		: with_non_recursive 	
		| v2=with_recursive    
			{System.out.println("Parsing with_recursive " + $v2.text);}
		;

with_non_recursive
		//: query_name column_list? AS LEFT_PAREN select_expression RIGHT_PAREN
		: query_name column_list? AS LEFT_PAREN set_operation_in_view RIGHT_PAREN
		;

	query_name
		: IDENTIFIER;

	select_expression :		// This is a rather simplified query compared to the one above.
		(SELECT | SEL) 
		select_quantity?
		projection_list
		(FROM v1=relation (COMMA relation)*)?
		where_clause?
		group_by_clause?
		standard_order_by_clause?;

with_recursive	: RECURSIVE query_name column_list? AS LEFT_PAREN 
			seed_statement 
			(UNION ALL? (seed_statement | recursive_statement))*
			RIGHT_PAREN;

	seed_statement	
		: (SELECT | SEL) (DISTINCT | ALL)? 
			projection_list
			(FROM v1=relation (COMMA relation)*)?
			where_clause?
			group_by_clause?
			standard_order_by_clause?
		;

	recursive_statement
		: (SELECT | SEL) 
			projection_list
			(FROM relation (COMMA relation)*)?
			where_clause?
			group_by_clause?
		;

//=============================================================================
// Rules for the Show Column command

show_column			// TD14.10 SQL Quick Reference, p146
		: (HELP | SHOW) COLUMN show_column_variation
			DELIMITER
		;

	show_column_variation
		: show_column_variation_1 
		| show_column_variation_2
		| show_column_variation_3
		| show_column_variation_4
		| show_column_variation_5
		| show_column_variation_6
		| show_column_variation_7
		| show_column_variation_8
		;

	show_column_variation_1
		: column_name (COMMA column_name)*
			FROM qualifiedName (COMMA qualifiedName)*
		;

	show_column_variation_2
		: ASTERISK FROM qualifiedName
		;

	show_column_variation_3
		: qualifiedName DOT column_name
			(COMMA qualifiedName DOT column_name)*
		;
	show_column_variation_4
		: qualifiedName DOT ASTERISK
			(COMMA qualifiedName DOT ASTERISK)*
		;
	show_column_variation_5
		: primaryExpression
			(COMMA primaryExpression)*
		;
	show_column_variation_6
		: show_column_expression
			(COMMA show_column_expression)*
		;
	show_column_variation_7
		: FROM ERROR TABLE FOR qualifiedName
		;
	show_column_variation_8
		: column_name FROM qualifiedName
		;

	show_column_expression
		: primaryExpression qualifiedName DOT ASTERISK
		| primaryExpression qualifiedName DOT ASTERISK COMMA primaryExpression
		;
//=============================================================================
// Rules for the Show Function command

show_function	: show_function_undelimited DELIMITER
		;

	show_function_undelimited
		: (HELP | SHOW) SPECIFIC FUNCTION qualifiedName
		| (HELP | SHOW) FUNCTION qualifiedName
			(LEFT_PAREN datatype (COMMA datatype)* RIGHT_PAREN)?
		| (HELP | SHOW) FUNCTION SYSUDTLIB DOT IDENTIFIER
			(LEFT_PAREN datatype (COMMA datatype)* RIGHT_PAREN)?
		;
//=============================================================================
// Rules for the Show Statisics command

show_statistics	
		: show_statistics_optimizer_form	DELIMITER
		//  show_statistics_qcd_form  out of scope for now.
		;

	show_statistics_optimizer_form	// TD15.10 SQL Data Definition Language, p997
		: SHOW
			(IN XML)? SUMMARY? CURRENT? 
			(STATISTICS | STATS | STAT)
			(VALUES SEQUENCED?)?
			show_what?
			show_on_what
		;

	show_what	
		: UNIQUE? INDEX index_name
		| UNIQUE? INDEX index_name? ALL? column_list
			(ORDER BY (VALUES | HASH) column_list)?
		| COLUMN show_what_column
		;

	show_what_column
		: primaryExpression (COMMA primaryExpression)* AS statistics_name
		| (statistics_name | column_name | PARTITION | column_or_partition_list)
			(AS statistics_name)?
		;

	column_or_partition_list
		: LEFT_PAREN (column_name | PARTITION) (COMMA (column_name | PARTITION))* RIGHT_PAREN;

	show_on_what
		: ON TEMPORARY? qualifiedName;

//=============================================================================
// Rules for the Show table command

show_table	: (HELP | SHOW) TABLE qualifiedName
			DELIMITER
		;

//=============================================================================
// Rules for the Show Type command

show_type	: (HELP | SHOW) TYPE (SYSUDTLIB DOT)? IDENTIFIER
			(ATTRIBUTE | METHOD)?
			DELIMITER
		;

//=============================================================================

comparison_operator
    		: EQUALS | NEQ | NOT EQUALS | LT | LTE | GT | GTE | LIKE;

booleanValue 	: TRUE | FALSE;

interval 	: INTERVAL (PLUS_SIGN | MINUS_SIGN)? STRING intervalField (TO intervalField)?;

intervalField	: v=interval_type ( LEFT_PAREN precision (COMMA precision)? RIGHT_PAREN )?
			{System.out.println("Interval type                : " + $v.text);}
		;

interval_type 	: YEAR | MONTH | DAY | HOUR | MINUTE | SECOND;

qualifiedName
		: identifier
			// for example a table name, or a column name

		| identifier DOT identifier
			// for example, a DB.table_name, or a Table.column_name

		| identifier DOT identifier DOT identifier
			// for example a DB.table_name.column_name

		| 'SYS_CALENDAR.CALENDAR'	
			// Must avoid matching the CALENDAR keyword by itself.
			// Otherwise the lexer tokenizes the CALENDAR keyword,
			// which keeps it from being matched as a tablename.

		| SESSION
			// Is used in the CCW_LOAD_CTL table
		| RIGHT
			// Function name, takes the Right N chars of a string
		| LEFT
			// Function name, takes the Left N chars of a string
		;

identifier 	: IDENTIFIER                                
		| LEFT_BRACKET IDENTIFIER RIGHT_BRACKET
		| IDENTIFIER DOLLAR OPEN_CURLY IDENTIFIER CLOSE_CURLY
    		| quotedIdentifier                        
    		| BACKQUOTED_IDENTIFIER                  
    		| DIGIT_IDENTIFIER                      
		| LABEL
		// Adding the following for keywords used as column names
		| ERRORCODE
		| SQL
		| ATTR
		| SQLSTATE
		| CLIENT
		| NEXT
		| INDEX
		| STAT
		| CONDITION
		| LEVEL
		| PERIOD
		| STATS
		| TYPE
		| CONFIDENCE
		| MANUAL
		| ROLE
		| USER
		| QUERY
		| LOGMECH	
		// Adding the following for keywords used as a table_name
		| CALENDAR
		| DATA
		| FINAL
		// Adding the following for keywords used as a databasename
		| TD_SYSFNLIB
		// Adding the following for keywords used as a table alias
		| DD
		| RM
		// Adding the following used as function names
		| AVG
		| DATABASE_NAME	// which might include ${env.id.upper}
		;

quotedIdentifier 
		: QUOTED_IDENTIFIER ; 

number 		: DECIMAL_VALUE
		| INTEGER_VALUE
		| (PLUS_SIGN | MINUS_SIGN) number
		;

unicode_literal		// https://docs.teradata.com/r/~_sY_PYVxZzTnqKq45UXkQ/RlPPWWckOUD4LB5zFBgPag
		: 'U&' STRING UESCAPE STRING 
		;

INTEGER_VALUE 	: DIGIT+		// Why is INTEGER_VALUE capitalized?
    		;

DECIMAL_VALUE 	: DIGIT+ '.' DIGIT*	// Why is this rule capitalized?
    		| '.' DIGIT+
    		| DIGIT+ ('.' DIGIT*)? EXPONENT
    		| '.' DIGIT+ EXPONENT
    		;

//==============================================================================
// Keywords

// I am sorting these keywords alphabetically as I review the rules that use them.
// The unsorted list below may contain keywords not valid in Teradata, or not used yet.
ACCESS          : [Aa][Cc][Cc][Ee][Ss][Ss];
ACCOUNT         : [Aa][Cc][Cc][Oo][Uu][Nn][Tt];
ACTIVITYCO   	: [Aa][Cc][Tt][Ii][Vv][Ii][Tt][Yy][Cc][Oo];
ACTIVITYCOUNT   : [Aa][Cc][Tt][Ii][Vv][Ii][Tt][Yy][Cc][Oo][Uu][Nn][Tt];
ADD             : [Aa][Dd][Dd];
AFTER           : [Aa][Ff][Tt][Ee][Rr];
ALL             : [Aa][Ll][Ll];
ALLOCATION      : [Aa][Ll][Ll][Oo][Cc][Aa][Tt][Ii][Oo][Nn];
ALTER           : [Aa][Ll][Tt][Ee][Rr];
ALWAYS		: [Aa][Ll][Ww][Aa][Yy][Ss];
AMP             : [Aa][Mm][Pp];
ANCHOR          : [Aa][Nn][Cc][Hh][Oo][Rr];
AND             : [Aa][Nn][Dd];
ANSI            : [Aa][Nn][Ss][Ii];
ANSIDATE        : [Aa][Nn][Ss][Ii][Dd][Aa][Tt][Ee];
ANY             : [Aa][Nn][Yy];
APPROXIMATE     : [Aa][Pp][Pp][Rr][Oo][Xx][Ii][Mm][Aa][Tt][Ee];
ARRAY           : [Aa][Rr][Rr][Aa][Yy];
AS              : [Aa][Ss];
ASC             : [Aa][Ss][Cc];
AT              : [Aa][Tt];
ATTR		: [Aa][Tt][Tt][Rr];
ATTRIBUTE	: [Aa][Tt][Tt][Rr][Ii][Bb][Uu][Tt][Ee];
ATTRIBUTES	: [Aa][Tt][Tt][Rr][Ii][Bb][Uu][Tt][Ee][Ss];
ATTRS		: [Aa][Tt][Tt][Rr][Ss];
AUTO            : [Aa][Uu][Tt][Oo];
AUTO_COMPRESS   : [Aa][Uu][Tt][Oo][_][Cc][Oo][Mm][Pp][Rr][Ee][Ss][Ss];
AUTOCOMPRESS    : [Aa][Uu][Tt][Oo][Cc][Oo][Mm][Pp][Rr][Ee][Ss][Ss];     // 2nd usage form
AVG           	: [Aa][Vv][Gg];
BEGIN           : [Bb][Ee][Gg][Ii][Nn];
BEFORE          : [Bb][Ee][Ff][Oo][Rr][Ee];
BETWEEN         : [Bb][Ee][Tt][Ww][Ee][Ee][Nn];
BIGINT          : [Bb][Ii][Gg][Ii][Nn][Tt];
BINARY          : [Bb][Ii][Nn][Aa][Rr][Yy];
BLOB            : [Bb][Ll][Oo][Bb];
BLOCKCOMPRESSION: [Bb][Ll][Oo][Cc][Kk][Cc][Oo][Mm][Pp][Rr][Ee][Ss][Ss][Ii][Oo][Nn];
BOM		: [Bb][Oo][Mm];
BOTH		: [Bb][Oo][Tt][Hh];
BSON            : [Bb][Ss][Oo][Nn];
BT		: [Bb][Tt];
BTET            : [Bb][Tt][Ee][Tt];
BUT             : [Bb][Uu][Tt];
BY              : [Bb][Yy];
BYTE            : [Bb][Yy][Tt][Ee];
BYTEINT         : [Bb][Yy][Tt][Ee][Ii][Nn][Tt];
BYTES           : [Bb][Yy][Tt][Ee][Ss];
CALENDAR        : [Cc][Aa][Ll][Ee][Nn][Dd][Aa][Rr];
CALL            : [Cc][Aa][Ll][Ll];
CALLED          : [Cc][Aa][Ll][Ll][Ee][Dd];
CALLER          : [Cc][Aa][Ll][Ll][Ee][Rr];
CASE            : [Cc][Aa][Ss][Ee];
CASE_N          : [Cc][Aa][Ss][Ee][_][Nn];
CASESPECIFIC    : [Cc][Aa][Ss][Ee][Ss][Pp][Ee][Cc][Ii][Ff][Ii][Cc];
CAST            : [Cc][Aa][Ss][Tt];
CHAR            : [Cc][Hh][Aa][Rr];
CHARACTER       : [Cc][Hh][Aa][Rr][Aa][Cc][Tt][Ee][Rr];
CHARACTERISTICS : [Cc][Hh][Aa][Rr][Aa][Cc][Tt][Ee][Rr][Ii][Ss][Tt][Ii][Cc][Ss];
CHARSET         : [Cc][Hh][Aa][Rr][Ss][Ee][Tt];
CHECK           : [Cc][Hh][Ee][Cc][Kk];
CHECKSUM        : [Cc][Hh][Ee][Cc][Kk][Ss][Uu][Mm];
CLIENT		: [Cc][Ll][Ii][Ee][Nn][Tt];
CLOB            : [Cc][Ll][Oo][Bb];
CLOSE		: [Cc][Ll][Oo][Ss][Ee];
// OALESCE	: [x][Oo][Aa][Ll][Ee][Ss][Cc][Ee];
	// Leave Coalesce un-tokenized, so it will be parsed like any regular function
COLLATION       : [Cc][Oo][Ll][Ll][Aa][Tt][Ii][Oo][Nn];
COLLECT         : [Cc][Oo][Ll][Ll][Ee][Cc][Tt];
COLUMN          : [Cc][Oo][Ll][Uu][Mm][Nn];
COLUMN_ALIAS_LIST     : [Cc][Oo][Ll][Uu][Mm][Nn][_][Aa][Ll][Ii][Aa][Ss][_][Ll][Ii][Ss][Tt];
COLUMN_LIST     : [Cc][Oo][Ll][Uu][Mm][Nn][_][Ll][Ii][Ss][Tt];
COMMENT         : [Cc][Oo][Mm][Mm][Ee][Nn][Tt];
COMMIT          : [Cc][Oo][Mm][Mm][Ii][Tt];
COMMITTED       : [Cc][Oo][Mm][Mm][Ii][Tt][Tt][Ee][Dd];
COMPILE         : [Cc][Oo][Mm][Pp][Ii][Ll][Ee];
COMPRESS        : [Cc][Oo][Mm][Pp][Rr][Ee][Ss][Ss];
CONCURRENT      : [Cc][Oo][Nn][Cc][Uu][Rr][Rr][Ee][Nn][Tt];
CONDITION	: [Cc][Oo][Nn][Dd][Ii][Tt][Ii][Oo][Nn];
CONFIDENCE      : [Cc][Oo][Nn][Ff][Ii][Dd][Ee][Nn][Cc][Ee];
CONSTRAINT      : [Cc][Oo][Nn][Ss][Tt][Rr][Aa][Ii][Nn][Tt];
CONSTRUCTOR     : [Cc][Oo][Nn][Ss][Tt][Rr][Uu][Cc][Tt][Oo][Rr];
CONTENT		: [Cc][Oo][Nn][Tt][Ee][Nn][Tt];
CONTINUE	: [Cc][Oo][Nn][Tt][Ii][Nn][Uu][Ee];
CREATE          : [Cc][Rr][Ee][Aa][Tt][Ee];
CREATOR         : [Cc][Rr][Ee][Aa][Tt][Oo][Rr];
CROSS           : [Cc][Rr][Oo][Ss][Ss];
CS              : [Cc][Ss];
CT              : [Cc][Tt];
CURRENT         : [Cc][Uu][Rr][Rr][Ee][Nn][Tt];
CURRENT_DATE    : [Cc][Uu][Rr][Rr][Ee][Nn][Tt][_][Dd][Aa][Tt][Ee];
CURRENT_TIME    : [Cc][Uu][Rr][Rr][Ee][Nn][Tt][_][Tt][Ii][Mm][Ee];
CURRENT_TIMESTAMP: [Cc][Uu][Rr][Rr][Ee][Nn][Tt][_][Tt][Ii][Mm][Ee][Ss][Tt][Aa][Mm][Pp];
CURSOR		: [Cc][Uu][Rr][Ss][Oo][Rr];
CV              : [Cc][Vv];
CYCLE		: [Cc][Yy][Cc][Ll][Ee];
DATA            : [Dd][Aa][Tt][Aa];
DATABASE        : [Dd][Aa][Tt][Aa][Bb][Aa][Ss][Ee];
DATABLOCKSIZE   : [Dd][Aa][Tt][Aa][Bb][Ll][Oo][Cc][Kk][Ss][Ii][Zz][Ee];
DATALABELS 	: [Dd][Aa][Tt][Aa][Ll][Aa][Bb][Ee][Ll][Ss];
DATE            : [Dd][Aa][Tt][Ee];
DATEFORM        : [Dd][Aa][Tt][Ee][Ff][Oo][Rr][Mm];
DAY             : [Dd][Aa][Yy];
DAYS            : [Dd][Aa][Yy][Ss];
DD              : [Dd][Dd];
DDNAME          : [Dd][Dd][Nn][Aa][Mm][Ee];
DEBUG           : [Dd][Ee][Bb][Uu][Gg];
DEC             : [Dd][Ee][Cc];
DECIMAL         : [Dd][Ee][Cc][Ii][Mm][Aa][Ll];
DECLARE		: [Dd][Ee][Cc][Ll][Aa][Rr][Ee];
DECOMPRESS      : [Dd][Ee][Cc][Oo][Mm][Pp][Rr][Ee][Ss][Ss];
DEFAULT         : [Dd][Ee][Ff][Aa][Uu][Ll][Tt];
DEFINER		: [Dd][Ee][Ff][Ii][Nn][Ee][Rr];
DEL             : [Dd][Ee][Ll];
DELETE          : [Dd][Ee][Ll][Ee][Tt][Ee];
DELETED         : [Dd][Ee][Ll][Ee][Tt][Ee][Dd];
DENSE         	: [Dd][Ee][Nn][Ss][Ee];
DESC            : [Dd][Ee][Ss][Cc];
DETERMINISTIC   : [Dd][Ee][Tt][Ee][Rr][Mm][Ii][Nn][Ii][Ss][Tt][Ii][Cc];
DIAGNOSTICS	: [Dd][Ii][Aa][Gg][Nn][Oo][Ss][Tt][Ii][Cc][Ss];
DIF		: [Dd][Ii][Ff];
DISTINCT        : [Dd][Ii][Ss][Tt][Ii][Nn][Cc][Tt];
DO		: [Dd][Oo];
DOUBLE          : [Dd][Oo][Uu][Bb][Ll][Ee];
DOWN            : [Dd][Oo][Ww][Nn];
DROP            : [Dd][Rr][Oo][Pp];
DUAL            : [Dd][Uu][Aa][Ll];
DYNAMIC         : [Dd][Yy][Nn][Aa][Mm][Ii][Cc];
EACH            : [Ee][Aa][Cc][Hh];
ECHO            : [Ee][Cc][Hh][Oo];
ECHOREQ         : [Ee][Cc][Hh][Oo][Rr][Ee][Qq];
EJECT		: [Ee][Jj][Ee][Cc][Tt];
ELSE            : [Ee][Ll][Ss][Ee];
ELSEIF          : [Ee][Ll][Ss][Ee][Ii][Ff];
END             : [Ee][Nn][Dd];
ERRORCODE       : [Ee][Rr][Rr][Oo][Rr][Cc][Oo][Dd][Ee];
ERRORLEVEL      : [Ee][Rr][Rr][Oo][Rr][Ll][Ee][Vv][Ee][Ll];
ERRORONLY       : [Ee][Rr][Rr][Oo][Rr][Oo][Nn][Ll][Yy];
ERROR          	: [Ee][Rr][Rr][Oo][Rr];
ERROROUT       	: [Ee][Rr][Rr][Oo][Rr][Oo][Uu][Tt];
ERRORS          : [Ee][Rr][Rr][Oo][Rr][Ss];
ESCAPE          : [Ee][Ss][Cc][Aa][Pp][Ee];
ET		: [Ee][Tt];
EXCLUDE		: [Ee][Xx][Cc][Ll][Uu][Dd][Ee];
EXCLUSIVE       : [Ee][Xx][Cc][Ll][Uu][Ss][Ii][Vv][Ee];
EXCL            : [Ee][Xx][Cc][Ll];
EXCEPT          : [Ee][Xx][Cc][Ee][Pp][Tt];
EXCEPTION       : [Ee][Xx][Cc][Ee][Pp][Tt][Ii][Oo][Nn];
EXECUTE		: [Ee][Xx][Ee][Cc][Uu][Tt][Ee];
EXISTS          : [Ee][Xx][Ii][Ss][Tt][Ss];
EXIT		: [Ee][Xx][Ii][Tt];
EXPAND          : [Ee][Xx][Pp][Aa][Nn][Dd];
EXPLAIN         : [Ee][Xx][Pp][Ll][Aa][Ii][Nn];
EXPORT		: [Ee][Xx][Pp][Oo][Rr][Tt];
EXTRACT         : [Ee][Xx][Tt][Rr][Aa][Cc][Tt];
FALLBACK        : [Ff][Aa][Ll][Ll][Bb][Aa][Cc][Kk];
FALSE           : [Ff][Aa][Ll][Ss][Ee];
FETCH		: [Ff][Ee][Tt][Cc][Hh];
FILE            : [Ff][Ii][Ll][Ee];
FINAL           : [Ff][Ii][Nn][Aa][Ll];
FIRST           : [Ff][Ii][Rr][Ss][Tt];
FLOAT           : [Ff][Ll][Oo][Aa][Tt];
FOLDLINE        : [Ff][Oo][Ll][Dd][Ll][Ii][Nn][Ee];
FOLLOWING       : [Ff][Oo][Ll][Ll][Oo][Ww][Ii][Nn][Gg];
FOR             : [Ff][Oo][Rr];
FOREIGN         : [Ff][Oo][Rr][Ee][Ii][Gg][Nn];
FORMAT          : [Ff][Oo][Rr][Mm][Aa][Tt];
FOUND		: [Ff][Oo][Uu][Nn][Dd];
FREESPACE       : [Ff][Rr][Ee][Ee][Ss][Pp][Aa][Cc][Ee];
FROM            : [Ff][Rr][Oo][Mm];
FULL            : [Ff][Uu][Ll][Ll];
FUNCTION        : [Ff][Uu][Nn][Cc][Tt][Ii][Oo][Nn];
GENERATED	: [Gg][Ee][Nn][Ee][Rr][Aa][Tt][Ee][Dd];
GET		: [Gg][Ee][Tt];
GLOBAL          : [Gg][Ll][Oo][Bb][Aa][Ll];
GLOP            : [Gg][Ll][Oo][Pp];
GOTO            : [Gg][Oo][Tt][Oo];
GRANT           : [Gg][Rr][Aa][Nn][Tt];
GRAPHIC         : [Gg][Rr][Aa][Pp][Hh][Ii][Cc];
GROUP           : [Gg][Rr][Oo][Uu][Pp];
HANDLER		: [Hh][Aa][Nn][Dd][Ll][Ee][Rr];
HASH            : [Hh][Aa][Ss][Hh];
HAVING          : [Hh][Aa][Vv][Ii][Nn][Gg];
HELP            : [Hh][Ee][Ll][Pp];
HIGH          	: [Hh][Ii][Gg][Hh];
HOUR            : [Hh][Oo][Uu][Rr];
IDENTITY        : [Ii][Dd][Ee][Nn][Tt][Ii][Tt][Yy];
IF              : [Ii][Ff];
IGNORE          : [Ii][Gg][Nn][Oo][Rr][Ee];
IMMEDIATE	: [Ii][Mm][Mm][Ee][Dd][Ii][Aa][Tt][Ee];
IN              : [Ii][Nn];
INCLUDE		: [Ii][Nn][Cc][Ll][Uu][Dd][Ee];
INCLUDE_NULLS	: [Ii][Nn][Cc][Ll][Uu][Dd][Ee][_][Nn][Uu][Ll][Ll][Ss];
INCREMENT	: [Ii][Nn][Cc][Rr][Ee][Mm][Ee][Nn][Tt];
INDEX           : [Ii][Nn][Dd][Ee][Xx];
INDICDATA	: [Ii][Nn][Dd][Ii][Cc][Dd][Aa][Tt][Aa];
INNER           : [Ii][Nn][Nn][Ee][Rr];
INOUT		: [Ii][Nn][Oo][Uu][Tt];
INPUT           : [Ii][Nn][Pp][Uu][Tt];
INS             : [Ii][Nn][Ss];
INSERT          : [Ii][Nn][Ss][Ee][Rr][Tt];
INSTANCE        : [Ii][Nn][Ss][Tt][Aa][Nn][Cc][Ee];
INSTANTIABLE    : [Ii][Nn][Ss][Tt][Aa][Nn][Tt][Ii][Aa][Bb][Ll][Ee];
INT             : [Ii][Nn][Tt];
INTEGER         : [Ii][Nn][Tt][Ee][Gg][Ee][Rr];
INTEGERDATE     : [Ii][Nn][Tt][Ee][Gg][Ee][Rr][Dd][Aa][Tt][Ee];
INTERSECT       : [Ii][Nn][Tt][Ee][Rr][Ss][Ee][Cc][Tt];
INTERVAL        : [Ii][Nn][Tt][Ee][Rr][Vv][Aa][Ll];
INTO            : [Ii][Nn][Tt][Oo];
INVOKER		: [Ii][Nn][Vv][Oo][Kk][Ee][Rr];
IS              : [Ii][Ss];
ISOLATED        : [Ii][Ss][Oo][Ll][Aa][Tt][Ee][Dd];
ISOLATION       : [Ii][Ss][Oo][Ll][Aa][Tt][Ii][Oo][Nn];
JOIN            : [Jj][Oo][Ii][Nn];
JOURNAL         : [Jj][Oo][Uu][Rr][Nn][Aa][Ll];
JSON            : [Jj][Ss][Oo][Nn];
KBYTES          : [Kk][Bb][Yy][Tt][Ee][Ss];
KEY             : [Kk][Ee][Yy];
KILOBYTES       : [Kk][Ii][Ll][Oo][Bb][Yy][Tt][Ee][Ss];
LABEL           : [Ll][Aa][Bb][Ee][Ll];
LANGUAGE        : [Ll][Aa][Nn][Gg][Uu][Aa][Gg][Ee];
LARGE           : [Ll][Aa][Rr][Gg][Ee];
LAST            : [Ll][Aa][Ss][Tt];
LATIN           : [Ll][Aa][Tt][Ii][Nn];
LATIN_TO_UNICODE: LATIN [_][Tt][Oo][_] UNICODE;
LEADING		: [Ll][Ee][Aa][Dd][Ii][Nn][Gg];
LEAVE		: [Ll][Ee][Aa][Vv][Ee];
LEFT            : [Ll][Ee][Ff][Tt];
LEVEL           : [Ll][Ee][Vv][Ee][Ll];
LIKE            : [Ll][Ii][Kk][Ee];
LIMIT           : [Ll][Ii][Mm][Ii][Tt];
LOAD            : [Ll][Oo][Aa][Dd];
LOADING         : [Ll][Oo][Aa][Dd][Ii][Nn][Gg];
LOCAL           : [Ll][Oo][Cc][Aa][Ll];
LOCALTIME       : [Ll][Oo][Cc][Aa][Ll][Tt][Ii][Mm][Ee];
LOCALTIMESTAMP  : [Ll][Oo][Cc][Aa][Ll][Tt][Ii][Mm][Ee][Ss][Tt][Aa][Mm][Pp];
LOCATOR         : [Ll][Oo][Cc][Aa][Tt][Oo][Rr];
LOCK            : [Ll][Oo][Cc][Kk];
LOCKING         : [Ll][Oo][Cc][Kk][Ii][Nn][Gg];
LOG             : [Ll][Oo][Gg];
LOGMECH         : [Ll][Oo][Gg][Mm][Ee][Cc][Hh];
LOGOFF          : [Ll][Oo][Gg][Oo][Ff][Ff];
LOGON          	: [Ll][Oo][Gg][Oo][Nn];
LONG            : [Ll][Oo][Nn][Gg];
LOOP		: [Ll][Oo][Oo][Pp];
LOW           	: [Ll][Oo][Ww];
MACRO           : [Mm][Aa][Cc][Rr][Oo];
MANUAL          : [Mm][Aa][Nn][Uu][Aa][Ll];
MAP		: [Mm][Aa][Pp];
MATCHED		: [Mm][Aa][Tt][Cc][Hh][Ee][Dd];
MAXERROR        : [Mm][Aa][Xx][Ee][Rr][Rr][Oo][Rr];
MAXIMUM         : [Mm][Aa][Xx][Ii][Mm][Uu][Mm];
MAXINTERVALS    : [Mm][Aa][Xx][Ii][Nn][Tt][Ee][Rr][Vv][Aa][Ll][Ss];
MAXVALUE	: [Mm][Aa][Xx][Vv][Aa][Ll][Uu][Ee];
MAXVALUELENGTH  : [Mm][Aa][Xx][Vv][Aa][Ll][Uu][Ee][Ll][Ee][Nn][Gg][Tt][Hh];
MEETS           : [Mm][Ee][Ee][Tt][Ss];
MERGE		: [Mm][Ee][Rr][Gg][Ee];
MERGEBLOCKRATIO : [Mm][Ee][Rr][Gg][Ee][Bb][Ll][Oo][Cc][Kk][Rr][Aa][Tt][Ii][Oo];
METHOD          : [Mm][Ee][Tt][Hh][Oo][Dd];
MINIMUM         : [Mm][Ii][Nn][Ii][Mm][Uu][Mm];
MINVALUE	: [Mm][Ii][Nn][Vv][Aa][Ll][Uu][Ee];
MINUS           : [Mm][Ii][Nn][Uu][Ss];
MINUTE          : [Mm][Ii][Nn][Uu][Tt][Ee];
MOD             : [Mm][Oo][Dd];
MODE            : [Mm][Oo][Dd][Ee];
MODIFY          : [Mm][Oo][Dd][Ii][Ff][Yy];
MONTH           : [Mm][Oo][Nn][Tt][Hh];
MULTISET        : [Mm][Uu][Ll][Tt][Ii][Ss][Ee][Tt];
NAMED           : [Nn][Aa][Mm][Ee][Dd];
NEVER           : [Nn][Ee][Vv][Ee][Rr];
NEXT		: [Nn][Ee][Xx][Tt];
NO              : [Nn][Oo];
NOBOM		: [Nn][Oo][Bb][Oo][Mm];
NOEJECT		: [Nn][Oo][Ee][Jj][Ee][Cc][Tt];
NOSPL           : [Nn][Oo][Ss][Pp][Ll];
NOT             : [Nn][Oo][Tt];
NONE            : [Nn][Oo][Nn][Ee];
NOWAIT          : [Nn][Oo][Ww][Aa][Ii][Tt];
NODDLTEXT       : [Nn][Oo][Dd][Dd][Ll][Tt][Ee][Xx][Tt];
NORMALIZE       : [Nn][Oo][Rr][Mm][Aa][Ll][Ii][Zz][Ee];
NULL            : [Nn][Uu][Ll][Ll];
NULLS           : [Nn][Uu][Ll][Ll][Ss];
NUMBER          : [Nn][Uu][Mm][Bb][Ee][Rr];
NUMERIC         : [Nn][Uu][Mm][Ee][Rr][Ii][Cc];
OBJECT          : [Oo][Bb][Jj][Ee][Cc][Tt];
OFF             : [Oo][Ff][Ff];
ON              : [Oo][Nn];
ONLY		: [Oo][Nn][Ll][Yy];
OPEN		: [Oo][Pp][Ee][Nn];
OPTION          : [Oo][Pp][Tt][Ii][Oo][Nn];
OR              : [Oo][Rr];
ORDER           : [Oo][Rr][Dd][Ee][Rr];
OS		: [Oo][Ss];
OUT           	: [Oo][Uu][Tt];
OUTER           : [Oo][Uu][Tt][Ee][Rr];
OVER            : [Oo][Vv][Ee][Rr];
OVERLAPS        : [Oo][Vv][Ee][Rr][Ll][Aa][Pp][Ss];
OVERRIDE        : [Oo][Vv][Ee][Rr][Rr][Ii][Dd][Ee];
OWNER		: [Oo][Ww][Nn][Ee][Rr];
PAGELENGTH	: [Pp][Aa][Gg][Ee][Ll][Ee][Nn][Gg][Tt][Hh];
PARAMETER       : [Pp][Aa][Rr][Aa][Mm][Ee][Tt][Ee][Rr];
PARTITION       : [Pp][Aa][Rr][Tt][Ii][Tt][Ii][Oo][Nn];
PARTITIONED     : [Pp][Aa][Rr][Tt][Ii][Tt][Ii][Oo][Nn][Ee][Dd];
PERCENT         : [Pp][Ee][Rr][Cc][Ee][Nn][Tt];
PERCENTILE_CONT : [Pp][Ee][Rr][Cc][Ee][Nn][Tt][Ii][Ll][Ee][_][Cc][Oo][Nn][Tt];
PERCENTILE_DISC : [Pp][Ee][Rr][Cc][Ee][Nn][Tt][Ii][Ll][Ee][_][Dd][Ii][Ss][Cc];
PERIOD          : [Pp][Ee][Rr][Ii][Oo][Dd];
POSITION        : [Pp][Oo][Ss][Ii][Tt][Ii][Oo][Nn];
PRECEDING       : [Pp][Rr][Ee][Cc][Ee][Dd][Ii][Nn][Gg];
PRECISION       : [Pp][Rr][Ee][Cc][Ii][Ss][Ii][Oo][Nn];
PREPARE		: [Pp][Rr][Ee][Pp][Aa][Rr][Ee];
PRESERVE        : [Pp][Rr][Ee][Ss][Ee][Rr][Vv][Ee];
PROCEDURE       : [Pp][Rr][Oo][Cc][Ee][Dd][Uu][Rr][Ee];
PROFILE         : [Pp][Rr][Oo][Ff][Ii][Ll][Ee];
PROTECTION      : [Pp][Rr][Oo][Tt][Ee][Cc][Tt][Ii][Oo][Nn];
PRIMARY         : [Pp][Rr][Ii][Mm][Aa][Rr][Yy];
QUALIFY         : [Qq][Uu][Aa][Ll][Ii][Ff][Yy];
QUERY           : [Qq][Uu][Ee][Rr][Yy];
QUIT		: [Qq][Uu][Ii][Tt];
RANDOMIZED      : [Rr][Aa][Nn][Dd][Oo][Mm][Ii][Zz][Ee][Dd];
RANGE           : [Rr][Aa][Nn][Gg][Ee];
RANGE_N         : [Rr][Aa][Nn][Gg][Ee][_][Nn];
RANK          	: [Rr][Aa][Nn][Kk];
READ            : [Rr][Ee][Aa][Dd];
REAL            : [Rr][Ee][Aa][Ll];
RECURSIVE       : [Rr][Ee][Cc][Uu][Rr][Ss][Ii][Vv][Ee];
REFERENCES      : [Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss];
REMARK		: [Rr][Ee][Mm][Aa][Rr][Kk];
RENAME          : [Rr][Ee][Nn][Aa][Mm][Ee];
REPEAT		: [Rr][Ee][Pp][Ee][Aa][Tt];
REPLACE         : [Rr][Ee][Pp][Ll][Aa][Cc][Ee];
REPLACEMENT     : [Rr][Ee][Pp][Ll][Aa][Cc][Ee][Mm][Ee][Nn][Tt];
REPORT		: [Rr][Ee][Pp][Oo][Rr][Tt];
REQUEST         : [Rr][Ee][Qq][Uu][Ee][Ss][Tt];
RESET           : [Rr][Ee][Ss][Ee][Tt];
RESIGNAL	: [Rr][Ee][Ss][Ii][Gg][Nn][Aa][Ll];
RESULT          : [Rr][Ee][Ss][Uu][Ll][Tt];
RETURN          : [Rr][Ee][Tt][Uu][Rr][Nn];
RETURNING       : [Rr][Ee][Tt][Uu][Rr][Nn][Ii][Nn][Gg];
RETURNS         : [Rr][Ee][Tt][Uu][Rr][Nn][Ss];
RIGHT           : [Rr][Ii][Gg][Hh][Tt];
RM		: [Rr][Mm];
ROLE            : [Rr][Oo][Ll][Ee];
ROW             : [Rr][Oo][Ww];
ROWS            : [Rr][Oo][Ww][Ss];
RU              : [Rr][Uu];
RUN             : [Rr][Uu][Nn];
SAMPLE          : [Ss][Aa][Mm][Pp][Ll][Ee];
SCROLL		: [Ss][Cc][Rr][Oo][Ll][Ll];
SEARCHUIFDBPATH : [Ss][Ee][Aa][Rr][Cc][Hh][Uu][Ii][Ff][Dd][Bb][Pp][Aa][Tt][Hh];
SECOND          : [Ss][Ee][Cc][Oo][Nn][Dd];
SECURITY	: [Ss][Ee][Cc][Uu][Rr][Ii][Tt][Yy];
SEL             : [Ss][Ee][Ll];
SELF            : [Ss][Ee][Ll][Ff];
SELECT          : [Ss][Ee][Ll][Ee][Cc][Tt];
SEQUENCE        : [Ss][Ee][Qq][Uu][Ee][Nn][Cc][Ee];
SEQUENCED       : [Ss][Ee][Qq][Uu][Ee][Nn][Cc][Ee][Dd];
SERIALIZABLE    : [Ss][Ee][Rr][Ii][Aa][Ll][Ii][Zz][Aa][Bb][Ll][Ee];
SESSION         : [Ss][Ee][Ss][Ss][Ii][Oo][Nn];
SET             : [Ss][Ee][Tt];
SETS            : [Ss][Ee][Tt][Ss];
SEVERITY	: [Ss][Ee][Vv][Ee][Rr][Ii][Tt][Yy];
SHARE           : [Ss][Hh][Aa][Rr][Ee];
SHOW            : [Ss][Hh][Oo][Ww];
SIDETITLES      : [Ss][Ii][Dd][Ee][Tt][Ii][Tt][Ll][Ee][Ss];
SIGNAL		: [Ss][Ii][Gg][Nn][Aa][Ll];
SKIP_IT        	: [Ss][Kk][Ii][Pp];	// SKIP is an Antlr reserved word
SKIPLINE        : [Ss][Kk][Ii][Pp][Ll][Ii][Nn][Ee];
SMALLINT        : [Ss][Mm][Aa][Ll][Ll][Ii][Nn][Tt];
SOME            : [Ss][Oo][Mm][Ee];
SPECIFIC        : [Ss][Pp][Ee][Cc][Ii][Ff][Ii][Cc];
SPL             : [Ss][Pp][Ll];
SQL             : [Ss][Qq][Ll];
SQLEXCEPTION	: [Ss][Qq][Ll][Ee][Xx][Cc][Ee][Pp][Tt][Ii][Oo][Nn];
SQLSTATE        : [Ss][Qq][Ll][Ss][Tt][Aa][Tt][Ee];
SQLWARNING	: [Ss][Qq][Ll][Ww][Aa][Rr][Nn][Ii][Nn][Gg];
SR              : [Ss][Rr];
SS              : [Ss][Ss];
START		: [Ss][Tt][Aa][Rr][Tt];
STAT            : [Ss][Tt][Aa][Tt];
STATIC          : [Ss][Tt][Aa][Tt][Ii][Cc];
STATISTICS      : [Ss][Tt][Aa][Tt][Ii][Ss][Tt][Ii][Cc][Ss];
STATS           : [Ss][Tt][Aa][Tt][Ss];
STDERR		: [Ss][Tt][Dd][Ee][Rr][Rr];
STDOUT		: [Ss][Tt][Dd][Oo][Uu][Tt];
STORAGE         : [Ss][Tt][Oo][Rr][Aa][Gg][Ee];
STYLE           : [Ss][Tt][Yy][Ll][Ee];
SUBSTR          : [Ss][Uu][Bb][Ss][Tt][Rr];
SUBSTRING       : [Ss][Uu][Bb][Ss][Tt][Rr][Ii][Nn][Gg];
SUM		: [Ss][Uu][Mm];
SUMMARY         : [Ss][Uu][Mm][Mm][Aa][Rr][Yy];
SYSLIB          : [Ss][Yy][Ss][Ll][Ii][Bb];
SYSTEM          : [Ss][Yy][Ss][Tt][Ee][Mm];
SYSUDTLIB       : [Ss][Yy][Ss][Uu][Dd][Tt][Ll][Ii][Bb];
TABLE           : [Tt][Aa][Bb][Ll][Ee];
TD_GENERAL      : [Tt][Dd][_][Gg][Ee][Nn][Ee][Rr][Aa][Ll];
TD_SYSFNLIB	: [Tt][Dd][_][Ss][Yy][Ss][Ff][Nn][Ll][Ii][Bb];
TD_UNPIVOT      : [Tt][Dd][_][Uu][Nn][Pp][Ii][Vv][Oo][Tt];
TEMPORARY       : [Tt][Ee][Mm][Pp][Oo][Rr][Aa][Rr][Yy];
THEN            : [Tt][Hh][Ee][Nn];
THRESHOLD       : [Tt][Hh][Rr][Ee][Ss][Hh][Oo][Ll][Dd];
TIES            : [Tt][Ii][Ee][Ss];
TIME            : [Tt][Ii][Mm][Ee];
TIMEMSG         : [Tt][Ii][Mm][Ee][Mm][Ss][Gg];
TIMESTAMP       : [Tt][Ii][Mm][Ee][Ss][Tt][Aa][Mm][Pp];
TIMEDATEWZCONTROL : [Tt][Ii][Mm][Ee][Dd][Ee][Ww][Zz][Cc][Oo][Nn][Tt][Rr][Oo][Ll];
TIMEZONE_HOUR	: [Tt][Ii][Mm][Ee][Zz][Oo][Nn][Ee][_][Hh][Oo][Uu][Rr];
TIMEZONE_MINUTE	: [Tt][Ii][Mm][Ee][Zz][Oo][Nn][Ee][_][Mm][Ii][Nn][Uu][Tt][Ee];
TITLE           : [Tt][Ii][Tt][Ll][Ee];
TITLEDASHES     : [Tt][Ii][Tt][Ll][Ee][Dd][Aa][Ss][Hh][Ee][Ss];
TO              : [Tt][Oo];
TODO            : [Tt][Oo][Dd][Oo];
TOP             : [Tt][Oo][Pp];
TOUCH		: [Tt][Oo][Uu][Cc][Hh];
TRACE           : [Tt][Rr][Aa][Cc][Ee];
TRAILING	: [Tt][Rr][Aa][Ii][Ll][Ii][Nn][Gg];
TRANS           : [Tt][Rr][Aa][Nn][Ss];
TRANSACTION     : [Tt][Rr][Aa][Nn][Ss][Aa][Cc][Tt][Ii][Oo][Nn];
TRANSLATE	: [Tt][Rr][Aa][Nn][Ss][Ll][Aa][Tt][Ee];
TRANSLATE_CHK	: [Tt][Rr][Aa][Nn][Ss][Ll][Aa][Tt][Ee][_][Cc][Hh][Kk];
TRIGGER         : [Tt][Rr][Ii][Gg][Gg][Ee][Rr];
TRIM            : [Tt][Rr][Ii][Mm];
TRUE            : [Tt][Rr][Uu][Ee];
TRYCAST         : [Tt][Rr][Yy][Cc][Aa][Ss][Tt];
TYPE            : [Tt][Yy][Pp][Ee];
UBJSON          : [Uu][Bb][Jj][Ss][Oo][Nn];
UC              : [Uu][Cc];
UESCAPE		: [Uu][Ee][Ss][Cc][Aa][Pp][Ee];
UNBOUNDED       : [Uu][Nn][Bb][Oo][Uu][Nn][Dd][Ee][Dd];
UNCOMMITTED     : [Uu][Nn][Cc][Oo][Mm][Mm][Ii][Tt][Tt][Ee][Dd];
UNICODE         : [Uu][Nn][Ii][Cc][Oo][Dd][Ee];
UNIQUE          : [Uu][Nn][Ii][Qq][Uu][Ee];
UNION		: [Uu][Nn][Ii][Oo][Nn];
UNICODE_TO_LATIN: [Uu][Nn][Ii][Cc][Oo][Dd][Ee][_][Tt][Oo][_][Ll][Aa][Tt][Ii][Nn];
UNKNOWN         : [Uu][Nn][Kk][Nn][Oo][Ww][Nn];
UNPIVOT		: [Uu][Nn][Pp][Ii][Vv][Oo][Tt];
UNPIVOT_COLUMN	: [Uu][Nn][Pp][Ii][Vv][Oo][Tt][_][Cc][Oo][Ll][Uu][Mm][Nn];
UNTIL   	: [Uu][Nn][Tt][Ii][Ll];
UNTIL_CHANGED   : [Uu][Nn][Tt][Ii][Ll][_][Cc][Hh][Aa][Nn][Gg][Ee][Dd];
UNTIL_CLOSED    : [Uu][Nn][Tt][Ii][Ll][_][Cc][Ll][Oo][Ss][Ee][Dd];
UPD		: [Uu][Pp][Dd];
UPDATE          : [Uu][Pp][Dd][Aa][Tt][Ee];
UPPERCASE       : [Uu][Pp][Pp][Ee][Rr][Cc][Aa][Ss][Ee];
USER            : [Uu][Ss][Ee][Rr];
USING           : [Uu][Ss][Ii][Nn][Gg];
VALUE           : [Vv][Aa][Ll][Uu][Ee];
VALUES          : [Vv][Aa][Ll][Uu][Ee][Ss];
VALUE_COLUMNS   : [Vv][Aa][Ll][Uu][Ee][_][Cc][Oo][Ll][Uu][Mm][Nn][Ss];
VARBYTE         : [Vv][Aa][Rr][Bb][Yy][Tt][Ee];
VARCHAR         : [Vv][Aa][Rr][Cc][Hh][Aa][Rr];
VARGRAPHIC      : [Vv][Aa][Rr][Gr][Rr][Aa][Pp][Hh][Ii][Cc];
VARYING         : [Vv][Aa][Rr][Yy][Ii][Nn][Gg];
VIEW            : [Vv][Ii][Ee][Ww];
VOLATILE        : [Vv][Oo][Ll][Aa][Tt][Ii][Ll][Ee];
WHEN            : [Ww][Hh][Ee][Nn];
WHERE           : [Ww][Hh][Ee][Rr][Ee];
WHILE		: [Ww][Hh][Ii][Ll][Ee];
WIDTH           : [Ww][Ii][Dd][Tt][Hh];
WITH            : [Ww][Ii][Tt][Hh];
WITHIN          : [Ww][Ii][Tt][Hh][Ii][Nn];
WITHOUT         : [Ww][Ii][Tt][Hh][Oo][Uu][Tt];
WRITE           : [Ww][Rr][Ii][Tt][Ee];
XML             : [Xx][Mm][Ll];
XMLAGG          : [Xx][Mm][Ll][Aa][Gg][Gg];
XMLTYPE         : [Xx][Mm][Ll][Tt][Yy][Pp][Ee];
YEAR            : [Yy][Ee][Aa][Rr];
ZONE            : [Zz][Oo][Nn][Ee];



// AT: [Aa][Tt];
// DESCRIBE: [Dd][Ee][Ss][Cc][Rr][Ii][Bb][Ee];
// TYPE: [Tt][Yy][Pp][Ee];
// TEXT: [Tt][Ee][Xx][Tt];
// GRAPHVIZ: [Gg][Rr][Aa][Pp][Hh][Vv][Ii][Zz];
// LOGICAL: [Ll][Oo][Gg][Ii][Cc][Aa][Ll];
// DISTRIBUTED: [Dd][Ii][Ss][Tt][Rr][Ii][Bb][Uu][Tt][Ee][Dd];
// TABLES: [Tt][Aa][Bb][Ll][Ee][Ss];
// SCHEMAS: [Ss][Cc][Hh][Ee][Mm][Aa][Ss];
// CATALOGS: [Cc][Aa][Tt][Aa][Ll][Oo][Gg][Ss];
// COLUMNS: [Cc][Oo][Ll][Uu][Mm][Nn][Ss];
// USE: [Uu][Ss][Ee];
// PARTITIONS: [Pp][Aa][Rr][Tt][Ii][Tt][Ii][Oo][Nn][Ss];
// FUNCTIONS: [Ff][Uu][Nn][Cc][Tt][Ii][Oo][Nn][Ss];
// BERNOULLI: [Bb][Ee][Rr][Nn][Oo][Uu][Ll][Ll][Ii];
// POISSONIZED: [Pp][Oo][Ii][Ss][Ss][Oo][Nn][Ii][Zz][Ee][Dd];
// RESCALED: [Rr][Ee][Ss][Cc][Aa][Ll][Ee][Dd];
// STRATIFY: [Ss][Tt][Rr][Aa][Tt][Ii][Ff][Yy];
// UNNEST: [Uu][Nn][Nn][Ee][Ss][Tt];
// ORDINALITY: [Oo][Rr][Dd][Ii][Nn][Aa][Ll][Ii][Tt][Yy];
// MAP: [Mm][Aa][Pp];
// MAX: [Mm][Aa][Xx];
// MIN: [Mm][Ii][Nn];
// LENGTH: [Ll][Ee][Nn][Gg][Tt][Hh];


EQUALS 			: '=' ;
NEQ 			: '<>' | '!=' | '^=';
LT  			: '<' ;
LTE 			: '<=';
GT  			: '>' ;
GTE 			: '>=';
DOUBLE_RIGHT_ANGLE	: '>>';
PLUS_SIGN		: '+' ;
MINUS_SIGN		: '-' ;
ASTERISK		: '*' ;
SLASH			: '/' ;
PERCENT_SIGN		: '%' ;
CONCAT			: '||';
COMMA			: ',' ;
LEFT_BRACKET 		: '[' ;
RIGHT_BRACKET 		: ']' ;
OPEN_CURLY		: '\\{' ;
CLOSE_CURLY		: '\\}' ;
LEFT_PAREN		: '(' ;
RIGHT_PAREN		: ')' ;
DOT			: '.' ;
HASH_SIGN		: '#' ;
COLON			: ':' ;
DOLLAR			: '$' ;

math_operator	: PLUS_SIGN
		| MINUS_SIGN
		| ASTERISK
		| SLASH
		| MOD
		;

STRING 		: '\'' ( ~'\'' | '\'\'' )* '\'' ;

HEX_CONSTANT	: 'x\'' ('0'..'9'|'a'..'f'|'A'..'F') ('0'..'9'|'a'..'f'|'A'..'F') '\'' ;

IDENTIFIER 	: (LETTER | '_') (LETTER | DIGIT | '_' | '@' )* ;

DATABASE_NAME 	: (LETTER | '_') (LETTER | DIGIT | '_' | '@' )* '${env.id.upper}';

DIGIT_IDENTIFIER: DIGIT+
    ;
QUOTED_IDENTIFIER
    : '"' ( ~'"' | '""' )* '"'
    ;
BACKQUOTED_IDENTIFIER
    : '`' ( ~'`' | '``' )* '`'
    ;
TIME_WITH_TIME_ZONE
    : 'TIME' WS 'WITH' WS 'TIME' WS 'ZONE'
    ;
TIMESTAMP_WITH_TIME_ZONE
    	: 'TIMESTAMP' WS 'WITH' WS 'TIME' WS 'ZONE'
	;
EXPONENT
    : 'E' ( '+' | '-' | ' ')? DIGIT+
    ;
fragment DIGIT : [0-9];

fragment LETTER 	: [a-zA-Z] ;

DELIMITER		: ';';

SIMPLE_COMMENT 		: '--' ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN) ;

BRACKETED_COMMENT 	: '/*' .*? '*/' -> channel(HIDDEN) ;

LINE_CONTINUATION_1	: '-\r'		-> skip ;
LINE_CONTINUATION_2	: '-\n'		-> skip ;

WS			: [ \r\n\t]+ 	-> skip ;


