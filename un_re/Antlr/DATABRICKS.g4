//
// This is an Antlr Parser grammar for DATABRICKS.
//
// You can find the master online documentation here:
// 	https://docs.databricks.com/sql/index.html
//
// I don't find a PDF version of the documentation.
//
//=============================================================================
grammar DATABRICKS;

import	DATABRICKS_Lexer;

//==============================================================================
root
        	: v1=single_statement* EOF
        	;

single_statement
                : v1=databricks_statement
                        {System.out.println();
                         System.out.println("Parsed single_statement      : ");
                         System.out.println($v1.text);
                         System.out.println("End of parsed single stmt    : ");
                         System.out.println("========= ========= ========= ========= ========= ========= =====");}
                ;

databricks_statement	
		: specific_databricks_statement SEMI_COLON?
		;
		
specific_databricks_statement
		: create_table
		| select_statement
		| set_statement
		| alter_table
		| grant
		| insert
		| create_view
		| describe
		| show
		| revoke
		| alter_schema
		| use
		| create_schema
		| update
		| delete
		| merge_into
		| alter_provider
		| create_share
		| create_catalog
		| create_function
		| vacuum
		| drop_function
		// create_database	// Is only an alias for create_schema
		| drop_table
		| truncate
		| restore
		| convert_to_delta
		| analyze
		| optimize
		| create_index
		| apply_changes
		| comment_on
		| cache_select
		;

//==============================================================================
expression	// https://docs.databricks.com/sql/language-manual/sql-ref-expression.html
		// Tested
		: literal
		| column_name
		// | field_reference	// A reference to a field in a STRUCT type.
		// | parameter_reference
		| cast_expression
		| case_expression

		| expression operator expression
		| expression boolean_binary_operator expression

		| operator expression
		| expression L_BRACKET expression R_BRACKET
					// A reference to an array element or a map key.
		| function_call

		| L_PAREN expression R_PAREN
		// | expression_list_wrapped
		| scalar_subquery

		| lambda

		// The following is used by an example for create function
		| expression DOUBLE_COLON datatype

		;

	literal
		: UNSIGNED_INTEGER
		| SINGLE_QUOTED_STRING
		| DOUBLE_QUOTED_STRING
		| DECIMAL_VALUE
		| NULL
		| interval_literal
		| DEFAULT
		| special_floating_point_value
		| boolean_literal
		// Many more
		;

	boolean_literal
		: TRUE
		| FALSE
		;

	//----------------------------------------------------------------------
	scalar_subquery
		// A scalar subquery is a subquery that should only return a 
		// single, scalar value
		: subquery
		;

	//----------------------------------------------------------------------
	interval_literal
		// https://docs.databricks.com/sql/language-manual/data-types/interval-type.html
		// Tested
		: INTERVAL (PLUS_SIGN | MINUS_SIGN)?
			SINGLE_QUOTED_STRING
			(yearMonthIntervalQualifier | dayTimeIntervalQualifier)
		;

	//----------------------------------------------------------------------
	operator
		// https://docs.databricks.com/sql/language-manual/sql-ref-functions-builtin.html#operators-and-predicates
		// No examples to test
                : DOUBLE_ASTERISK
                | ASTERISK
                | SLASH
                | PERCENT_SIGN
                | DOUBLE_PIPE
                | PLUS_SIGN
                | MINUS_SIGN
                | AMPERSAND
                | PIPE
                | CARET_SIGN
		| EQUALS
		| NOT_EQUALS

		| TODO
		// Many more
                ;

expression_list_wrapped
		: L_PAREN expression_list R_PAREN
		;

expression_list
		: expression (COMMA expression)*
		;

//==============================================================================
apply_changes	// https://docs.databricks.com/en/delta-live-tables/sql-ref.html
		// https://docs.databricks.com/en/delta-live-tables/cdc.html#language-sql
		: APPLY CHANGES INTO
                        (v1=LIVE DOT) v2=table_name
                        {
                        System.out.println ("Statement Type               : ALTER TABLE");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }

			FROM streaming_table_name
			KEYS keys
			where_clause?
			apply_options_1*
			SEQUENCE BY orderByColumn
			apply_options_2*
		;

	streaming_table_name
		: STREAM L_PAREN (schema_name DOT)? table_name R_PAREN
		;

	keys	: column_name_list_wrapped
		;

	apply_options_1	// should come before the Sequence By clause
		: IGNORE NULL UPDATES
		| APPLY AS DELETE WHEN condition
		| APPLY AS TRUNCATE WHEN condition
		;

	apply_options_2	// Should come after the Sequence By clause
		: COLUMNS (column_name_list_wrapped | ASTERISK EXCEPT column_name_list_wrapped)
		| STORED AS SCD TYPE UNSIGNED_INTEGER
		| TRACK HISTORY ON (column_name_list_wrapped | ASTERISK EXCEPT column_name_list_wrapped)
		;

	condition
		: boolean_expression
		;

	orderByColumn
		: column_name
		;

//==============================================================================
boolean_expression                                // Boolean condition
        	: boolean_atom
        	| boolean_expression boolean_logical_operator boolean_expression
        	| L_PAREN boolean_expression R_PAREN
        	| NOT boolean_expression
        	;

	boolean_logical_operator
		: AND
		| OR
		;

	boolean_atom
		: boolean_unary
		| boolean_binary
		| expression
		;

	boolean_unary
      		: expression IS NOT? NULL
    		| expression BETWEEN expression AND expression
    		| NOT? EXISTS L_PAREN query R_PAREN
    		| boolean_single_in
    		| boolean_multi_in
    		;

	boolean_single_in
        	: expression NOT? IN L_PAREN ((expression (COMMA expression)*) | query) R_PAREN
                	// example> VAR IN ('PREF','BSC','BSCL')
        	| expression NOT? IN expression
                	// example> VAR IN ${hivevar:MED_MGMNT_PLAN_CD}
        	;

	boolean_multi_in 
		: L_PAREN expression (COMMA expression)* R_PAREN NOT? IN L_PAREN query R_PAREN
    		;

	boolean_binary 
		: expression boolean_binary_operator expression
		| expression_list_wrapped EQUALS expression_list_wrapped
     		;

	boolean_binary_operator 
		: DOUBLE_EQUALS
		| EQUALS
     		| LTGT
     		| LT
     		| LE
     		| GT
     		| GE
     		| NOT? LIKE
     		;

//==============================================================================
cast_expression	// https://docs.databricks.com/sql/language-manual/functions/cast.html
		// Tested
		: CAST L_PAREN expression AS datatype R_PAREN

		// The following are not documented
		// This seems like a good place to put them.
		| DATE      expression
		| TIMESTAMP expression
		| ARRAY     expression_list_wrapped
		| MAP       expression_list_wrapped
		| STRUCT    expression_list_wrapped
		;

//==============================================================================
function_call
		: function_name argument_list_wrapped
			filter_clause?
		| filter_function
		| window_function
		| extract_function
		| trim_function
		;

	argument_list_wrapped
		: L_PAREN argument_list? R_PAREN
		;

	argument_list
		: argument (COMMA argument)*
		;

	argument
		: DISTINCT? expression
		| ASTERISK
		;

	filter_clause
		// Apparently aggregate functions can have a filter clause
		: FILTER L_PAREN where_clause R_PAREN
		;

	filter_function
		// https://docs.databricks.com/sql/language-manual/functions/filter.html
		// Tested
		: FILTER L_PAREN expression COMMA lambda R_PAREN
		;

//==============================================================================
trim_function	// https://docs.databricks.com/sql/language-manual/functions/trim.html
		: TRIM L_PAREN expression R_PAREN
		| TRIM L_PAREN (LEADING | TRAILING | BOTH) expression 
			FROM expression R_PAREN
		;

//==============================================================================
extract_function
		// https://docs.databricks.com/sql/language-manual/functions/extract.html
		// Tested
		: EXTRACT L_PAREN column_name FROM expression R_PAREN
		;

//==============================================================================
lambda		// https://docs.databricks.com/sql/language-manual/sql-ref-lambda-functions.html
		// Tested
		: param ARROW lambda_target
		| param_list_wrapped ARROW lambda_target
		;

	lambda_target
		: expression
		| boolean_expression
		;

	param_list_wrapped
		: L_PAREN param_list R_PAREN
		;

	param_list
		: param (COMMA param)*
		;

	param	: identifier ;

//==============================================================================
case_expression	// https://docs.databricks.com/sql/language-manual/functions/case.html
		// Tested
                : CASE (searched_when_clause | simple_when_clause )
                        (ELSE (expression | NULL))?
                        END
                ;

	searched_when_clause                    
                : searched_when_item+
                ;

        searched_when_item
                : WHEN boolean_expression THEN (expression | NULL)
                ;

	simple_when_clause                      
                : expression simple_when_item+
                ;

        simple_when_item
                : WHEN expression THEN (expression | NULL)
                ;

//==============================================================================
datatype	// https://docs.databricks.com/sql/language-manual/sql-ref-datatypes.html
		// No tests documented
		: simple_datatype
		| complex_datatype
		;

	complex_datatype
		: array_datatype
		| map_datatype
		| struct_datatype
		;

	simple_datatype
		: BIGINT
		| BINARY
		| BOOLEAN
		| DATE
		| decimal precision_and_scale?
		| DOUBLE
		| FLOAT
		| INT
		| INTERVAL intervalQualifier
		| VOID
		| SMALLINT
		| STRING
		| TIMESTAMP	datatype_size?
		| TINYINT

		// The following datatypes are not documented.
                | VARCHAR       datatype_size?
                | CHAR          datatype_size?
                | CHARACTER     datatype_size?
		| LONG
		| INTEGER
		;

	datatype_size
		: L_PAREN UNSIGNED_INTEGER R_PAREN
		;

	decimal
		: DECIMAL
		| DEC
		| NUMERIC
		;

	precision_and_scale
		: L_PAREN UNSIGNED_INTEGER (COMMA UNSIGNED_INTEGER)? R_PAREN
		;

	intervalQualifier
		: yearMonthIntervalQualifier
		| dayTimeIntervalQualifier
		;

	yearMonthIntervalQualifier
		: YEAR (TO MONTH)? 
		| MONTH
		;

	dayTimeIntervalQualifier
		: DAY    (TO (HOUR | MINUTE | SECOND))? 
		| HOUR   (TO (MINUTE | SECOND))?
		| MINUTE (TO SECOND)?
		| SECOND

		| DAYS		// Not documented, but used by an example
		;

	//----------------------------------------------------------------------
	array_datatype
		// https://docs.databricks.com/sql/language-manual/data-types/array-type.html
		// Tested.
		: ARRAY elementType_list_wrapped
		;
	
	elementType_list_wrapped
		: LT elementType_list GT
		| LT complex_datatype GT	// nested
		;

	elementType_list
		: elementType (COMMA elementType)*
		;

	elementType
		: simple_datatype
		| expression
		;

	//----------------------------------------------------------------------
	map_datatype
		// https://docs.databricks.com/sql/language-manual/data-types/map-type.html
		// Tested.
		: MAP LT keyType COMMA valueType GT
		;

	keyType
		: simple_datatype
		| complex_datatype
		;

	valueType
		: simple_datatype
		;

	//----------------------------------------------------------------------
	struct_datatype
		// https://docs.databricks.com/sql/language-manual/data-types/struct-type.html
		// Tested
		: STRUCT LT struct_element_list? GT
		;

	struct_element_list
		: struct_element (COMMA struct_element)*
		;

	struct_element
		: column_name COLON? datatype (NOT NULL)? 
			comment_clause? 
		;

//==============================================================================
special_floating_point_value
		// https://docs.databricks.com/sql/language-manual/data-types/special-floating-point-values.html
		// Tested
		: DOUBLE L_PAREN SINGLE_QUOTED_STRING R_PAREN
		| FLOAT  L_PAREN SINGLE_QUOTED_STRING R_PAREN
		// Others??
		;

//==============================================================================
alter_provider	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-provider.html
		// Tested.
		: ALTER PROVIDER provider_name
			{
			System.out.println ("Statement Type               : ALTER PROVIDER");
			}
			alter_provider_option
		;

	alter_provider_option
		: RENAME TO provider_name 
		| SET? OWNER TO principal
		;

//==============================================================================
alter_table	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-table.html
		// Tested
		: ALTER TABLE (v1=schema_name DOT)? v2=table_name alter_table_constraint
			{
			System.out.println ("Statement Type               : ALTER TABLE CONSTRAINT");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }

		| ALTER TABLE (v1=schema_name DOT)? v2=table_name 
			{
			System.out.println ("Statement Type               : COMMENT ON COLUMN");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			alter_table_alter_column_comment

		| ALTER TABLE (v1=schema_name DOT)? v2=table_name alter_table_column
			{
			System.out.println ("Statement Type               : ALTER TABLE COLUMN");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
		| ALTER TABLE (v1=schema_name DOT)? v2=table_name alter_table_action
			{
			System.out.println ("Statement Type               : ALTER TABLE");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
		| ALTER TABLE (v1=schema_name DOT)? v2=table_name alter_table_other
			{
			System.out.println ("Statement Type               : ALTER TABLE OTHER");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
		;

	alter_table_constraint
		: alter_table_add_constraint
		| alter_table_drop_constraint // Kept separate for classification
		; 

	alter_table_other
		: alter_table_rename
		| alter_table_rename_partition
		| alter_table_add_partition
		| alter_table_drop_partition
		| set_location_clause
     		| alter_table_set_serde 	// The detailed syntax is not documented
		| set_tblproperties
		| unset_tblproperties
		;

	alter_table_column
		: alter_table_add_column
		| alter_table_alter_column
		| alter_table_rename_column
		;

	alter_table_alter_column_comment
		: (ALTER | CHANGE) COLUMN? v1=column_name
			v2=comment_clause
			{System.out.println("Found comment-on object      : COLUMN");
			 System.out.println("Found comment-on column name : " + $v1.text);
                         System.out.println("Found comment-on string      : " + $v2.text);}
		; 

	alter_table_action
		: alter_table_drop_column
		| RECOVER PARTITIONS
		| set_owner_clause
		| table_cluster_by_clause
		;

	//----------------------------------------------------------------------
	alter_table_rename
		: RENAME TO table_name
		;

	//----------------------------------------------------------------------
	alter_table_add_column
		: ADD (COLUMN | COLUMNS) alter_table_column_list_wrapped
		;

	alter_table_column_list_wrapped
		: L_PAREN alter_table_column_list R_PAREN
		;

	alter_table_column_list
		: alter_table_column_item (COMMA alter_table_column_item)*
		;

	alter_table_column_item
		: column_name datatype
      			(DEFAULT expression)? 
			comment_clause? 
			((FIRST | AFTER) identifier)?
		;

	//----------------------------------------------------------------------
	alter_table_alter_column
		: (ALTER | CHANGE) COLUMN? column_name
			alter_table_alter_column_option*
		;

	alter_table_alter_column_option
		: comment_clause
    		| (FIRST | AFTER) column_name 
		| (SET | DROP) NOT NULL 
		| SET DEFAULT expression 
		| DROP DEFAULT 
		| SYNC IDENTITY
		;

	//----------------------------------------------------------------------
	alter_table_drop_column
		: DROP (COLUMN | COLUMNS) (IF EXISTS) column_name_list_wrapped
		;

	//----------------------------------------------------------------------
	alter_table_rename_column
		: RENAME COLUMN column_name TO column_name
		;

	//----------------------------------------------------------------------
	alter_table_add_partition
		: ADD (IF NOT EXISTS)? alter_table_add_partition_list+
		;

	alter_table_add_partition_list
		: partition_clause (LOCATION path)?
		;

	alter_table_partition_item
		: PARTITION partition_value_list_wrapped (LOCATION path)?
		;

	//----------------------------------------------------------------------
	alter_table_drop_partition
		: DROP (IF EXISTS)? partition_clause
			PURGE?
		;

	//----------------------------------------------------------------------
	alter_table_rename_partition
		: partition_clause 
			RENAME TO partition_clause
		;

	//----------------------------------------------------------------------
	set_tblproperties
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-tblproperties.html#tblproperties
		// Tested
		: SET TBLPROPERTIES property_key_value_list_wrapped
		;

	//----------------------------------------------------------------------
	unset_tblproperties
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-tblproperties.html#unset-tblproperties
		// Tested
		: UNSET TBLPROPERTIES (IF EXISTS)? property_key_list_wrapped
		;

	//----------------------------------------------------------------------
	alter_table_set_serde
		: SET SERDE SINGLE_QUOTED_STRING
			(WITH SERDEPROPERTIES property_key_value_list_wrapped)?
		;

	//----------------------------------------------------------------------
	set_location_clause
		: partition_clause?
			SET LOCATION path
		;

	//----------------------------------------------------------------------
	set_owner_clause
		: SET? OWNER TO principal
		;

//==============================================================================
principal	// https://docs.databricks.com/sql/language-manual/sql-ref-principal.html
		// Tested
		: group_name
		| ACCOUNT? USERS
		| SINGLE_QUOTED_STRING
			// Actually principals need to be inside backticks.  But
			// Antlr cannot handle backticks because of their 
			// special meaning to Unix, so the caller needs to
			// replace backticks with single quotes.
		;

//==============================================================================
alter_table_add_constraint
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-table-add-constraint.html
		// Tested
		: ADD (check_constraint | table_constraint)
		;

	check_constraint
    		: CONSTRAINT constraint_name CHECK L_PAREN boolean_expression R_PAREN ENFORCED?
		;

//==============================================================================
alter_table_drop_constraint
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-table-drop-constraint.html
		// Tested
		: DROP alter_table_drop_constraint_option
		;

	alter_table_drop_constraint_option
		: PRIMARY KEY (IF EXISTS)? (RESTRICT | CASCADE)? 
		| FOREIGN KEY (IF EXISTS)? column_name_list_wrapped
		| CONSTRAINT  (IF EXISTS)? column_name (RESTRICT | CASCADE)?
		;

//==============================================================================
alter_schema	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-alter-schema.html
		: ALTER (SCHEMA | DATABASE) schema_name
			alter_schema_type
			{
			System.out.println ("Statement Type               : ALTER SCHEMA");
			}
		;

	alter_schema_type
		: SET DBPROPERTIES property_key_value_list_wrapped
		| SET? OWNER TO principal
		;

//==============================================================================
analyze		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-analyze-table.html
		// Tested
		: ANALYZE
			{
			System.out.println ("Statement Type               : COLLECT STATISTICS");
			}
			analyze_what
		;

	analyze_what
		: analyze_table
		| analyze_tables
		;

	analyze_table
		: TABLE table_name partition_clause?
    			COMPUTE STATISTICS 
			( NOSCAN | FOR COLUMNS column_name_list | FOR ALL COLUMNS )?
		;

	analyze_tables
		: TABLES 
			( (FROM | IN)? schema_name )? 
			COMPUTE STATISTICS NOSCAN?
		;

//==============================================================================
comment_on	// https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-comment.html
		: COMMENT ON
			comment_on_what
			IS
			v1=comment_text
				{
	                        System.out.println ("Found comment-on string      : " + $v1.text);
				}
			;

	comment_on_what
		: comment_on_what_else
			{
			System.out.println ("Statement Type               : COMMENT ON");
			}
		| TABLE v1=table_name
			{
			System.out.println ("Statement Type               : COMMENT ON TABLE");
			System.out.println ("Found table name             : " + $v1.text);
			System.out.println ("Found comment-on object      : TABLE");
			}
		;

	comment_on_what_else
		: CATALOG catalog_name
		| CONNECTION connection_name
		| PROVIDER provider_name
		| RECIPIENT recipient_name
		| (SCHEMA | DATABASE) schema_name
		| SHARE share_name
		| VOLUME volume_name
		;

	comment_text
		: SINGLE_QUOTED_STRING
		| DOUBLE_QUOTED_STRING
		| NULL
		;

//==============================================================================
convert_to_delta
		// https://docs.databricks.com/sql/language-manual/delta-convert-to-delta.html
		// Tested
		: CONVERT TO DELTA table_name 
			{
			System.out.println ("Statement Type               : CONVERT TO DELTA");
			}
			(NO STATISTICS)? 
			partitioned_by_clause?
		;

//==============================================================================
create_catalog	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-catalog.html
		// Tested.
		: CREATE CATALOG (IF NOT EXISTS)? catalog_name
			{
			System.out.println ("Statement Type               : CREATE CATALOG");
			}
			create_catalog_option*
		;

	create_catalog_option
		: USING SHARE? provider_name DOT share_name
			// The documentation says that SHARE is required
			// but it has an example
		| MANAGED LOCATION path
		| comment_clause
		;

//==============================================================================
create_database	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-database.html
		// No test cases
		: create_schema
		;

//==============================================================================
create_function	: create_function_type
			{
			System.out.println ("Statement Type               : CREATE FUNCTION");
			}
		;

	create_function_type
		: create_function_sql
		| create_function_external
		;

	create_function_sql
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-sql-function.html
		// Tested
		: CREATE (OR REPLACE)? TEMPORARY? FUNCTION (IF NOT EXISTS)?  function_name 
			function_parameter_spec_list_wrapped
    			RETURNS function_return_clause
    			characteristic*
    			RETURN (expression | query )
		;

	function_parameter_spec_list_wrapped
		: L_PAREN function_parameter_spec_list? R_PAREN
		;

	function_parameter_spec_list
		: function_parameter_spec (COMMA function_parameter_spec)*
		;

	function_parameter_spec
    		: parameter_name datatype (DEFAULT expression)? comment_clause?
		;

	function_return_clause
		: datatype 
		| TABLE function_return_column_spec_list_wrapped
		;

	function_return_column_spec_list_wrapped
		: L_PAREN function_return_column_spec_list R_PAREN
		;

	function_return_column_spec_list
		: function_return_column_spec (COMMA function_return_column_spec)*
		;

	function_return_column_spec
		: column_name datatype comment_clause?
		;

	characteristic
		: LANGUAGE SQL 
		| NOT? DETERMINISTIC 
		| comment_clause
		| CONTAINS SQL 
		| READS SQL DATA
		| SQL SECURITY DEFINER
		;

	// ---------------------------------------------------------------------
	create_function_external
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-function.html
		// Tested
		: CREATE (OR REPLACE)? TEMPORARY? FUNCTION (IF NOT EXISTS)?
    			function_name AS class_name resource_locations?
		;

	resource_locations
		: USING resource_location (COMMA resource_location)*
		;

	resource_location
		:  (JAR | FILE | ARCHIVE) resource_uri
		;

	resource_uri
		: identifier	// Right?
		;

//==============================================================================
create_index	
		: create_bloomfilter_index
		;

	create_bloomfilter_index
		// https://docs.databricks.com/sql/language-manual/delta-create-bloomfilter-index.html
		: CREATE BLOOMFILTER INDEX
			ON TABLE? table_name
			FOR COLUMNS index_column_options_list_wrapped
			options_clause?
			{
			System.out.println ("Statement Type               : CREATE INDEX");
			}
		;

	index_column_options_list_wrapped
		: L_PAREN index_column_options_list R_PAREN
		;

	index_column_options_list
		: index_column (COMMA index_column)*
		;

	index_column
		: column_name options_clause?
		;

//==============================================================================
create_schema	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-schema.html
		// Tested.
		: CREATE SCHEMA (IF NOT EXISTS)? schema_name
			{
			System.out.println ("Statement Type               : CREATE SCHEMA");
			}
			comment_clause?
			(MANAGED? LOCATION path)?
			(WITH DBPROPERTIES property_key_value_list_wrapped)?
		;

//==============================================================================
create_share	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-share.html
		// Tested.
		: CREATE SHARE (IF NOT EXISTS)? share_name
			{
			System.out.println ("Statement Type               : CREATE SHARE");
			}
    			comment_clause?
		;

//==============================================================================
create_table	
		: create_table_regular
		| create_table_as_select
		| create_table_like
		| create_live_table
		| create_auto_loader_table
		;

	create_table_regular
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-table-using.html
		// Tested
		: (create_table_method_1 | create_table_method_2)
			(v1=schema_name DOT)? v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			table_specification?
			using_data_source?
			table_clauses*
		;

		create_table_method_1
			: (CREATE OR)? REPLACE TABLE
			;

		create_table_method_2
			: CREATE EXTERNAL? TABLE (IF NOT EXISTS)?
			;

	create_table_as_select
		// This is given a separate rule so it can be assigned a 
		// different statement type, so the rules engine can check it
		// differently than a regular create table type.
		: (create_table_method_1 | create_table_method_2)
			(v1=schema_name DOT)? v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE AS SELECT");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			table_specification?
			using_data_source?
			table_clauses*
			AS query
		;

	table_specification
		: L_PAREN column_specification_list
			table_constraints*
			R_PAREN
		;

	column_specification_list
		: column_specification (COMMA column_specification)*
		;

	column_specification
		: v1=column_name 
			{
                        System.out.println("Found column name            : " + $v1.text);
                        }

		  v2=datatype 
			{
                        if ($v2.text != null) {
                                System.out.println("  datatype                   : " + $v2.text);
                                }
                        }
		  column_options*
		;

	column_options
		: NOT NULL
		| GENERATED ALWAYS AS L_PAREN expression R_PAREN
		| GENERATED (ALWAYS | BY DEFAULT) AS v1=IDENTITY identity_attributes_wrapped?
			{
                        System.out.println("datatype_attribute.identity  : Found " + $v1.text);
                        }
		| DEFAULT expression
		| v2=comment_clause
			{System.out.println("Found comment-on object      : COLUMN");
                         System.out.println("Found comment-on string      : " + $v2.text);
			}
		| column_constraint
		;

	identity_attributes_wrapped
		: L_PAREN identity_attributes* R_PAREN
		;

	identity_attributes
		: START WITH UNSIGNED_INTEGER
		| INCREMENT BY UNSIGNED_INTEGER
		;
		
	column_constraint
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint.html
		// Tested
                : (CONSTRAINT constraint_name)?
                        column_constraint_type
                        constraint_options*
		;

	column_constraint_type
		: PRIMARY KEY constraint_options*
                        {System.out.println("Found primary key            : ");}
		| (FOREIGN KEY)? REFERENCES table_name (L_PAREN column_name R_PAREN)?
		;
		
	table_constraints
		: COMMA table_constraint
		;

	table_constraint
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint.html
		// Tested
                : (CONSTRAINT constraint_name)?
                        table_constraint_type
                        constraint_options*
                ;

        table_constraint_type
                : UNIQUE column_name_list_wrapped
                | PRIMARY KEY v1=column_name_list_wrapped
                        {System.out.println("Found primary key            : " + $v1.text);}
                | (FOREIGN KEY)? column_name_list_wrapped REFERENCES table_name column_name_list_wrapped?
                ;

	pk_column_name_list_wrapped
		: L_PAREN pk_column_name_list R_PAREN
		;

	pk_column_name_list
		: pk_column_name_item (COMMA pk_column_name_item)*
		;

	pk_column_name_item
		: column_name TIMESERIES?
		;

	constraint_options
		: NOT ENFORCED 
		| DEFERRABLE 
		| INITIALLY DEFERRED 
		| NORELY
		| MATCH FULL 
		| ON UPDATE NO ACTION 
		| ON DELETE NO ACTION 
		;

	using_data_source	// The syntax for this is not well documented
		: USING data_source_type
		;

	data_source_type
		: TEXT
		| AVRO
		| BINARYFILE
		| CSV
		| JSON
		| PARQUET
		| ORC
		| DELTA
		| JDBC
		| LIBSVM
		// | fully_qualified_class_name // Like what??
		;

	fully_qualified_class_name
		: identifier (DOT identifier)*
		;

	table_clauses
		: options_clause
		| partitioned_by_clause
		| clustered_by_clause
		| location_clause
		| v1=comment_clause
			{System.out.println("Found comment-on object      : TABLE");
                         System.out.println("Found comment-on string      : " + $v1.text);}
		| tblproperties_clause
		| table_cluster_by_clause	
		;

	clustered_by_clause
		: CLUSTERED BY column_name_list_wrapped
			sorted_by_list_wrapped?
    			INTO UNSIGNED_INTEGER BUCKETS
		;

	table_cluster_by_clause
		// Used for Liquid Clustering, described here:
		// https://learn.microsoft.com/en-us/azure/databricks/delta/clustering
		// This is different than the query cluster_by_clause
		: CLUSTER BY (column_name_list_wrapped | NONE)
		;

	sorted_by_list_wrapped
		: L_PAREN sort_by_list R_PAREN
		;

	sort_by_list
		: sort_by_item (COMMA sort_by_item)*
		;

	sort_by_item
		: column_name (ASC | DESC)
		;

	location_clause
		: LOCATION path 
			(WITH ( CREDENTIAL credential_name ) )?
		;

	path
		: SINGLE_QUOTED_STRING	// Right?
		| DOUBLE_QUOTED_STRING
		;

	create_table_like
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-table-like.html
		: CREATE TABLE (IF NOT EXISTS)? 
			(v1=schema_name DOT)? v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE AS SELECT");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			LIKE (schema_name DOT)? table_name
			create_table_like_clauses*
			;

	create_table_like_clauses
		: using_data_source
		| LOCATION path
		| tblproperties_clause
		| ROW FORMAT row_format
		| STORED AS file_format
		;

	row_format
		: row_format_serde
		| row_format_delimited
		;

	row_format_serde
		: SERDE serde_class ( WITH SERDEPROPERTIES property_key_value_list_wrapped)?
		;

	row_format_delimited
		: DELIMITED ( FIELDS TERMINATED BY fields_terminated_char ( ESCAPED BY escaped_char )? )?
			row_format_delimited_options*
		;

	row_format_delimited_options
		: COLLECTION ITEMS TERMINATED BY collection_items_terminated_char
       		| MAP KEYS TERMINATED BY map_key_terminated_char
       		| LINES TERMINATED BY row_terminated_char
       		| NULL DEFINED AS null_char
		;

	file_format
		: TEXTFILE
		| SEQUENCEFILE
		| RCFILE
		| ORC
		| PARQUET
		| AVRO
		; 

//==============================================================================
create_live_table
		// https://docs.databricks.com/en/delta-live-tables/sql-ref.html
		: create_live_table_alone
		| create_live_table_as
		;

	create_live_table_alone
		: CREATE OR REFRESH TEMPORARY? 
			v1=live_kind TABLE
		 	v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			live_table_specification?
			create_live_table_clauses*
			// (AS query)?  // No AS query when alone
			;

	create_live_table_as
		: CREATE OR REFRESH TEMPORARY? 
			v1=live_kind TABLE
		 	v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE AS SELECT");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			live_table_specification?
			create_live_table_clauses*
			(AS query)?
			;

	live_kind
		: LIVE
		| STREAMING
		;

	create_live_table_clauses
		: USING DELTA
		| PARTITIONED BY column_name_list_wrapped
		| LOCATION path
		| v1=comment_clause
			{System.out.println("Found comment-on object      : TABLE");
                         System.out.println("Found comment-on string      : " + $v1.text);}
		| tblproperties_clause
		;

	live_table_specification
		: L_PAREN live_column_specification_list?
			live_table_constraint_list?
			R_PAREN
		;

	live_column_specification_list
		: live_column_specification (COMMA live_column_specification)*
		;

	live_column_specification
		: v1=column_name 
			{
                        System.out.println("Found column name            : " + $v1.text);
                        }

		  v2=datatype 
			{
                        if ($v2.text != null) {
                                System.out.println("  datatype                   : " + $v2.text);
                                }
                        }
		  live_column_options*
		;

	live_column_options
		: v1=comment_clause
			{System.out.println("Found comment-on object      : COLUMN");
                         System.out.println("Found comment-on string      : " + $v1.text);}

		| NOT NULL		// Not documented for LIVE tables
		| DEFAULT expression	// Not documented for LIVE tables
		| GENERATED ALWAYS AS L_PAREN expression R_PAREN
		| GENERATED (ALWAYS | BY DEFAULT) AS v2=IDENTITY identity_attributes_wrapped?
			{
                        System.out.println("datatype_attribute.identity  : Found " + $v2.text);
                        }
		;

	live_table_constraint_list
		: COMMA? live_table_constraint_item (COMMA live_table_constraint_item)*
		;

	live_table_constraint_item
		: CONSTRAINT expectation_name 
			EXPECT L_PAREN boolean_expression R_PAREN
			live_table_constraint_option*
		;

	live_table_constraint_option
		: ON VIOLATION ((FAIL UPDATE) | (DROP ROW))
		;

	expectation_name
		: identifier
		;

//==============================================================================
create_auto_loader_table
		// https://docs.databricks.com/en/delta-live-tables/sql-ref.html
		: CREATE OR REFRESH STREAMING TABLE
			(v1=schema_name DOT)? v2=table_name
			{
			System.out.println ("Statement Type               : CREATE TABLE");

                        if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			AS SELECT ASTERISK
			FROM CLOUD_FILES L_PAREN
				DOUBLE_QUOTED_STRING COMMA	// file-path
				DOUBLE_QUOTED_STRING COMMA	// file-format
				MAP expression_list_wrapped
				R_PAREN
			;

//==============================================================================
tblproperties_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-tblproperties.html#tblproperties
		// Tested
		: TBLPROPERTIES property_key_value_list_wrapped
		;

//==============================================================================
options_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-tblproperties.html#options
		// Tested
		: OPTIONS property_key_value_list_wrapped
		;

	property_key_value_list_wrapped
		: L_PAREN property_key_value_list R_PAREN
		;

	property_key_value_list
		: property_key_value_pair (COMMA property_key_value_pair)*
		;

	property_key_value_pair
		: property_key EQUALS? property_val
		;

	property_val
		: literal
		;

	property_key_list_wrapped
		: L_PAREN property_key_list R_PAREN
		;

	property_key_list	// Without the value
		: property_key (COMMA property_key)*
		;

//==============================================================================
create_view	
		: create_regular_view
		| create_live_view
		;

	create_regular_view
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-view.html
		// Tested.
		: CREATE (OR REPLACE)? (TEMP | TEMPORARY)? VIEW (IF NOT EXISTS)? (v1=schema_name DOT)? v2=view_name
			{
			System.out.println ("Statement Type               : CREATE VIEW");
			if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
			System.out.println("Found view name              : " + $v2.text);
                        }
			view_column_list_wrapped?
			comment_clause?
			tblproperties_clause?
			AS
			query
		;

	view_column_list_wrapped
		: L_PAREN view_column_list R_PAREN
		;

	view_column_list
		: view_column_item (COMMA view_column_item)*
		;

	view_column_item
		: column_name comment_clause?
		;	

	create_live_view
		// https://docs.databricks.com/en/delta-live-tables/sql-ref.html
		: CREATE TEMPORARY STREAMING? LIVE VIEW 
			(v1=schema_name DOT)? v2=view_name
			{
			System.out.println ("Statement Type               : CREATE VIEW");
			if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
			System.out.println("Found view name              : " + $v2.text);
                        }
			view_column_list_wrapped?
			comment_clause?
			AS query
		;

//==============================================================================
delete		// https://docs.databricks.com/sql/language-manual/delta-delete-from.html
		// Tested
		: DELETE FROM table_name table_alias? 
			{
			System.out.println ("Statement Type               : DELETE");
                        }
			where_clause?
		;

//==============================================================================
describe	
		: (DESC | DESCRIBE) describe_alternative
			{
			System.out.println ("Statement Type               : DESCRIBE");
                        }
		;

	describe_alternative
		: describe_query
		| describe_function
		| describe_table
		| describe_schema
		| describe_history
		;
	
	describe_function
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-describe-function.html
		// Tested
		: FUNCTION EXTENDED? function_name
		;

	describe_query
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-describe-query.html
		// Tested
		: QUERY? (query | values_clause)
		;

	describe_schema
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-describe-schema.html
		// Tested
		: SCHEMA EXTENDED? schema_name
		;

	describe_table
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-describe-table.html
		: TABLE? (EXTENDED | FORMATTED)? table_name 
			partition_clause?
			column_name?
		;

	describe_history
		// https://docs.databricks.com/en/sql/language-manual/delta-describe-history.html
		: HISTORY table_name
		;

//==============================================================================
drop_function	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-drop-function.html
		// Tested
		: DROP TEMPORARY? FUNCTION (IF EXISTS)? function_name
			{
			System.out.println ("Statement Type               : DROP FUNCTION");
                        }
		;

//==============================================================================
drop_table	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-drop-table.html
		// Tested
		: DROP TABLE (IF EXISTS)? table_name
			{
			System.out.println ("Statement Type               : DROP TABLE");
                        }
		;

//==============================================================================
grant		// https://docs.databricks.com/sql/language-manual/security-grant.html
		// Tested
		: GRANT privilege_types ON securable_object TO principal
			{
			System.out.println ("Statement Type               : GRANT");
                        }
		;

	privilege_types
		: ALL PRIVILEGES 
		| privilege_type_list
		;

	privilege_type_list
		: privilege_type (COMMA privilege_type)*
		;

//==============================================================================
privilege_type	// https://docs.databricks.com/sql/language-manual/sql-ref-privileges.html#privilege-types
		// Tested with grant
		: CREATE CATALOG
		| CREATE EXTERNAL LOCATION
		| CREATE SHARE
		| CREATE RECIPIENT
		| CREATE PROVIDER
		| USE CATALOG
		| CREATE SCHEMA
		| USE SCHEMA
		| CREATE TABLE
		| CREATE VIEW
		| CREATE FUNCTION
		| SELECT
		| MODIFY
		| CREATE EXTERNAL TABLE
		| READ FILES
		| WRITE FILES
		| CREATE MANAGED STORAGE
		| EXECUTE
		| CREATE	// CREATE by itself has an example, 
				// but is not documented
		; 

//==============================================================================
securable_object	
		// https://docs.databricks.com/sql/language-manual/sql-ref-privileges.html#securable-objects
		// Tested with grant
  		: CATALOG catalog_name?
		| (SCHEMA | DATABASE) schema_name 
		| EXTERNAL LOCATION location_name 
		| FUNCTION function_name 
		| METASTORE 
		| SHARE share_name 
		| STORAGE CREDENTIAL credential_name 
		| TABLE? table_name 
		| VIEW view_name
		;

//==============================================================================
partition_clause// https://docs.databricks.com/sql/language-manual/sql-ref-partition.html#partition
		// tested with partitioned_by
		: PARTITION partition_value_list_wrapped
		;

	partition_value_list_wrapped
		: L_PAREN partition_value_list R_PAREN
		;

	partition_value_list
		: partition_value_item (COMMA partition_value_item)*
		;

	partition_value_item
		: partition_column (EQUALS (expression | (LIKE pattern)))?
		;

//==============================================================================
partitioned_by_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-partition.html#partitioned-by
		// Tested
		: PARTITIONED BY partitioned_column_list_wrapped
		;

	partitioned_column_list_wrapped
		: L_PAREN partitioned_column_list R_PAREN
		;

	partitioned_column_list
		: partitioned_column_item (COMMA partitioned_column_item)*
		;

	partitioned_column_item
		: column_name datatype?
		;

//==============================================================================
insert		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-dml-insert-into.html
		// Tested
		: insert_alternative
			{
			System.out.println ("Statement Type               : INSERT");
                        }
		;

	insert_alternative
		: insert_into
		| insert_replace
		;
		
	insert_into
		: INSERT (OVERWRITE | INTO) TABLE? table_name
			partition_clause?
			column_name_list_wrapped?
    			query
		;

	insert_replace
		: INSERT INTO TABLE? table_name
			REPLACE where_clause
    			query
		;

//==============================================================================
merge_into	// https://docs.databricks.com/sql/language-manual/delta-merge-into.html
		// Tested
		: MERGE INTO table_name target_alias?
			{
			System.out.println ("Statement Type               : MERGE");
                        }
   			USING source_table_reference source_alias?
   			ON merge_condition
			merge_when_clauses+
		;

	merge_when_clauses
		: WHEN MATCHED (AND matched_condition)? THEN matched_action 
		| WHEN NOT MATCHED (BY TARGET)? (AND not_matched_condition)? THEN not_matched_action 
		| WHEN NOT MATCHED BY SOURCE (AND not_matched_by_source_condition)? THEN not_matched_by_source_action
		;

	matched_action
		: DELETE 
		| UPDATE SET ASTERISK	// ASTERISK means set target.colN = source.coln, for all N
		| UPDATE SET update_column_list
		;

	not_matched_action
		: INSERT ASTERISK
		| INSERT column_name_list_wrapped VALUES expression_list_wrapped
		;

	not_matched_by_source_action
		: DELETE 
		| UPDATE SET update_column_list
		;

	source_table_reference
		: table_reference
		;

	source_alias
		: table_alias
		;

	target_alias
		: table_alias
		;

	merge_condition
		: boolean_expression	// Right?
		;

	matched_condition
		: boolean_expression	// Right?
		;

	not_matched_condition
		: boolean_expression	// Right?
		;

	not_matched_by_source_condition
		: boolean_expression	// Right?
		;

//==============================================================================
select_statement
		: query
			{
			System.out.println ("Statement Type               : SELECT");
                        }
		;

cache_select	// https://docs.databricks.com/en/sql/language-manual/delta-cache.html
		: CACHE select_statement
		;

//==============================================================================
query		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-query.html
		// No general tests
		: with_common_table_expression?
			(subquery | set_operation)
			query_clauses*
		;

	query_clauses
		: order_by_clause 
		| distribute_by_clause
		| cluster_by_clause 
  		| window_clause 
  		| limit_clause
  		| offset_clause
		| sort_by_clause
		;

	query_wrapped
		: L_PAREN query R_PAREN
		;

	subquery
		: select_from_where
		| values_clause
		| L_PAREN query R_PAREN
		| TABLE table_name
		;

//==============================================================================
set_operation	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-setops.html
		// Tested.
		: subquery
			(set_operator subquery)*
		;

	set_operator
		: UNION 	set_size?
		| INTERSECT	set_size?
		| EXCEPT	set_size?

		// The documentation says MINUS is an alias for EXCEPT
		| MINUS		set_size?
		;

	set_size
		: ALL
		| DISTINCT
		;

//==============================================================================
offset_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-offset.html
		// Tested
		: OFFSET UNSIGNED_INTEGER
		| OFFSET expression
		;

//==============================================================================
having_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-having.html
		// Tested
		: HAVING boolean_expression
		;

//==============================================================================
select_from_where
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select.html
		// Tested
		: SELECT hints? (ALL | DISTINCT)? 
			select_item_list
			select_from_clause?
				// The documentation requires a from clause
				// But there are lots of examples without one.
			lateral_view_clause*
			where_clause?
			group_by_clause?
			having_clause?
			qualify_clause?
		;

	select_item_list
		: select_item (COMMA select_item)*
		;

	select_item
		: named_expression
		| star_clause
		| L_PAREN select_item_list R_PAREN
		;

	named_expression
		: expression column_alias?
		;

	column_alias
		: AS? (identifier | expression_list_wrapped)
		;

	star_clause
		: (table_name DOT)? ASTERISK except_clause?
		;

	except_clause
		: EXCEPT column_name_list_wrapped
		;

	select_from_clause
		: FROM table_reference_list
		;

	table_reference_list
		: table_reference_as_of (COMMA table_reference_as_of)*
		;

	table_reference_as_of
		: table_reference       as_of?
		;

//==============================================================================
table_reference	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-table-reference.html
		// Tested

		: table_name tablesample_clause? table_alias?
		| view_name table_alias?

		// join_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-join.html
				// Tested
		| table_reference join_type? JOIN table_reference join_criteria?

		// pivot_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-pivot.html
				// Tested
		| table_reference PIVOT 
			L_PAREN pivot_item_list 
				FOR pivot_column
				IN aliased_column_list_wrapped
			R_PAREN

		// unpivot_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-unpivot.html
					// Tested
		| table_reference UNPIVOT ((INCLUDE NULLS) | (EXCLUDE NULLS))?
  			(single_value | multi_value)
			table_alias?

		| LATERAL? table_valued_function table_alias?
		| values_clause 
		| LATERAL? L_PAREN query R_PAREN tablesample_clause? table_alias?

		| CLOUD_FILES argument_list_wrapped
		| streaming_table_name table_alias?

		| L_PAREN table_reference R_PAREN
		;

	table_valued_function
		: function_call
		;

	join_type
		: INNER 
		| LEFT OUTER? 
		| LEFT? SEMI
		| RIGHT OUTER? 
		| FULL OUTER? 
		| LEFT? ANTI 
		| CROSS 
		| NATURAL join_type
		;

	join_criteria
		: ON boolean_expression
		| USING column_name_list_wrapped
		;

	pivot_item_list
		: pivot_item (COMMA pivot_item)*
		;

	pivot_item
		: expression (AS? column_name)?
		;

	pivot_column
		: column_name
		| column_name_list_wrapped
		;

	single_value
		: L_PAREN value_column FOR unpivot_column IN aliased_column_list_wrapped R_PAREN
		;

	multi_value
		: L_PAREN value_column_list_wrapped FOR unpivot_column IN aliased_column_list_wrapped R_PAREN
		;

	value_column_list_wrapped
		: L_PAREN value_column_list R_PAREN
		;

	value_column_list
		: value_column (COMMA value_column)*
		;

	value_column
		: column_name
		;

	unpivot_column
		: column_name
		;

	aliased_column_list_wrapped
		: L_PAREN aliased_column_list R_PAREN
		;

	aliased_column_list
		: aliased_column_item (COMMA aliased_column_item)*
		;

	aliased_column_item
		: expression 			column_alias?
		| expression_list_wrapped 	column_alias?
		;

	as_of
		: TIMESTAMP AS OF timestamp_expression
		| VERSION AS OF version
		| AT_SIGN (timestamp_expression | identifier)
			// Technically, the identifier should start with letter 'v'
		;

	timestamp_expression
		: expression
		;

//==============================================================================
values_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-values.html
		// Tested
		: VALUES values_list table_alias? column_name_list_wrapped?
		;

	values_list
		: value_item (COMMA value_item)*
		;

	value_item
		: expression 
		| expression_list_wrapped
		;

//==============================================================================
table_alias	// https://docs.databricks.com/sql/language-manual/sql-ref-names.html#table-alias
		// Tested
		: AS? table_identifier column_name_list_wrapped?
		;

//==============================================================================
tablesample_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-sampling.html
		// Tested
		: TABLESAMPLE L_PAREN tablesample_size R_PAREN
			(REPEATABLE L_PAREN seed R_PAREN)?
		;

	tablesample_size
		: UNSIGNED_INTEGER PERCENT
		| UNSIGNED_INTEGER ROWS
		| BUCKET fraction OUT OF total
		;

	seed	: UNSIGNED_INTEGER
		;

	fraction: UNSIGNED_INTEGER
		;

	total	: UNSIGNED_INTEGER
		;

//==============================================================================
hints 		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-hints.html
		// Does not need testing.
		: BLOCK_COMMENT
		;

//==============================================================================
lateral_view_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-lateral-view.html
		// Tested
		: LATERAL VIEW OUTER? 
			generator_function expression_list_wrapped table_identifier? 
			AS column_name_list
		;

	generator_function
		: function_name
		;

//==============================================================================
where_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-where.html
		// Tested
		: WHERE boolean_expression
		;

//==============================================================================
group_by_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-groupby.html
		// Tested
		: GROUP BY group_by_alternative
		;

	group_by_alternative
		: group_expression_list (WITH (ROLLUP | CUBE))?
		| (group_expression | ROLLUP | CUBE | GROUPING SETS)
			grouping_set_list_wrapped
		| ALL
		;

	group_expression_list
		: group_expression (COMMA group_expression)*
		;

	group_expression
		: expression
		;

	grouping_set_list_wrapped
		: L_PAREN grouping_set_list R_PAREN
		;

	grouping_set_list
		: grouping_set (COMMA grouping_set)*
		;

	grouping_set
		: expression
		| expression_list_wrapped
		| L_PAREN R_PAREN
		;

//==============================================================================
qualify_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-qualify.html
		// Tested
		: QUALIFY boolean_expression
		;

//==============================================================================
with_common_table_expression
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-cte.html
		// Tested
		: WITH common_table_expression_list
		;

	common_table_expression_list
		: common_table_expression (COMMA common_table_expression)*
		;

	common_table_expression
		: view_identifier column_name_list_wrapped?
			AS? query_wrapped
		;

//==============================================================================
order_by_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-orderby.html
		// Tested
        	: ORDER BY order_by_column_list
		| ORDER BY order_by_all
        	;

	order_by_all
		: ALL sort_direction? nulls_sort_order?
		;

	order_by_column_list
		: order_by_column_item (COMMA order_by_column_item)*
		;

	order_by_column_item
		: expression sort_direction? nulls_sort_order?
		;

	sort_direction
		: ASC
		| DESC
		;

	nulls_sort_order
		: NULLS (FIRST | LAST)
		;

//==============================================================================
distribute_by_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-distributeby.html
		// Tested
		: DISTRIBUTE BY expression_list
		;

//==============================================================================
sort_by_clause 	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-sortby.html
		// Tested
		: SORT BY order_by_column_list
		;

//==============================================================================
cluster_by_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-clusterby.html
		// Tested
		: CLUSTER BY expression_list
		;

//==============================================================================
limit_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-limit.html
		// Tested
		: LIMIT (ALL | expression)
		;

//==============================================================================
optimize	// https://docs.databricks.com/sql/language-manual/delta-optimize.html
		: OPTIMIZE 
			{
			System.out.println ("Statement Type               : OPTIMIZE");
			}
			(v1=schema_name DOT)? v2=table_name 
			{
			if ($v1.text != null) {
                                System.out.println("Found database identifier    : " + $v1.text);
                                }
                        System.out.println("Found table name             : " + $v2.text);
                        }
			where_clause?
			zorder_clause?
		;

	zorder_clause
		: ZORDER BY zorder_column_name_list_wrapped
		;

	zorder_column_name_list_wrapped
		: L_PAREN zorder_column_name_list R_PAREN
		;

	zorder_column_name_list
		: zorder_column_name (COMMA zorder_column_name)*
		;

	zorder_column_name
		: v1=column_name
			{
                        System.out.println("Found column name            : " + $v1.text);
                        }
		;

//==============================================================================
restore		// https://docs.databricks.com/sql/language-manual/delta-restore.html
		: RESTORE TABLE? table_name TO? time_travel_version
			{
			System.out.println ("Statement Type               : RESTORE");
                        }
		;

	time_travel_version
		: TIMESTAMP AS OF timestamp_expression 
		| VERSION AS OF version
		;

//==============================================================================
revoke		// https://docs.databricks.com/sql/language-manual/security-revoke.html
		// Tested
		: REVOKE privilege_types ON securable_object FROM principal
			{
			System.out.println ("Statement Type               : REVOKE");
                        }
		;

//==============================================================================
set_statement	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-conf-mgmt-set.html
		// Tested
		: SET set_regular_option?
			{
			System.out.println ("Statement Type               : SET");
                        }
		;

	set_regular_option
		: MINUS_SIGN LETTER_V
		| property_key (EQUALS property_val)?
		;

//==============================================================================
show		
		: show_alternative
			{
			System.out.println ("Statement Type               : SHOW");
                        }
		;

	show_alternative
		// show_databases	// Is only an alias for SHOW SCHEMAS
		: show_functions
		| show_partitions
		| show_schemas
		| show_shares
		| show_tblproperties
		| TODO
		// Many more.
		;

	show_functions
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-show-functions.html
		// Tested
		: SHOW function_kind? FUNCTIONS 
			( (FROM | IN) schema_name )?
       			( LIKE? (function_name | regex_pattern) )?
		;

	function_kind
		: USER 
		| SYSTEM 
		| ALL
		;

	show_partitions
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-show-partitions.html
		// Tested.
		: SHOW PARTITIONS table_name partition_clause?
		;

	show_schemas
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-show-schemas.html
		// Tested
		: SHOW SCHEMAS (LIKE regex_pattern)?
		;

	show_shares
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-show-shares.html
		// Tested
		: SHOW SHARES show_share_option?
		;

	show_share_option
		: LIKE regex_pattern
		| IN PROVIDER provider_name	// This option is not documented
		;

	show_tblproperties
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-aux-show-tblproperties.html
		// Tested
		: SHOW TBLPROPERTIES table_name
			property_key_list_wrapped?
		;

//==============================================================================
truncate	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-truncate-table.html
		// Tested
		: TRUNCATE TABLE table_name partition_clause?
                	{
			System.out.println ("Statement Type               : TRUNCATE");
			}
		;

//==============================================================================
update		// https://docs.databricks.com/sql/language-manual/delta-update.html
		// Tested
		: UPDATE table_name table_alias?
                	{
			System.out.println ("Statement Type               : UPDATE");
			}
   			SET update_column_list
			where_clause?
		;

	update_column_list
		: update_column_item (COMMA update_column_item)*
		;

	update_column_item
		: column_name EQUALS expression
		;

//==============================================================================
use		: use_option
		;

	use_option
		: use_database
		| use_catalog
		| use_schema
		;

	use_database
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-usedb.html
		// No test cases documented
		: USE DATABASE? v1=expression
                	{
                	System.out.println ("Statement Type               : DEFAULT DATABASE");
			System.out.println ("Found database identifier    : " + $v1.text);
			}
        	;

	use_catalog
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-use-catalog.html
		// Tested
		: (USE | SET) CATALOG v1=catalog_name
                	{
                	System.out.println ("Statement Type               : DEFAULT DATABASE");
			System.out.println ("Found database identifier    : " + $v1.text);
			}
		// It seems redundant to print the Statement Type 3 times, but
		// this option allows both USE or SET, while the others only USE
		;
	
	use_schema
		: USE SCHEMA? v1=expression
                	{
                	System.out.println ("Statement Type               : DEFAULT DATABASE");
			System.out.println ("Found database identifier    : " + $v1.text);
			}
        	;

//==============================================================================
vacuum		// https://docs.databricks.com/sql/language-manual/delta-vacuum.html
		// Tested.
		: VACUUM table_name 
                	{
			System.out.println ("Statement Type               : VACUUM");
			}
			(RETAIN UNSIGNED_INTEGER HOURS)?
			(DRY RUN)?
		;

//==============================================================================
window_clause	// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-named-window.html
		// Tested
		: WINDOW window_clause_list
		;

	window_clause_list
		: window_clause_item (COMMA window_clause_item)*
		;

	window_clause_item
		: window_name AS window_spec
		;

	
//==============================================================================
window_frame_clause
		// https://docs.databricks.com/sql/language-manual/sql-ref-syntax-window-functions-frame.html
		// No examples documented
		: frame_mode frame_start
		| frame_mode BETWEEN frame_start AND frame_end
		;

	frame_mode
		: RANGE
		| ROWS
		;

	frame_start
		: UNBOUNDED PRECEDING 
		| offset_start PRECEDING 
		| CURRENT ROW 
		| offset_start FOLLOWING
		;

	frame_end
		: offset_stop PRECEDING 
		| CURRENT ROW 
		| offset_stop FOLLOWING 
		| UNBOUNDED FOLLOWING
		;

	offset_start
		: UNSIGNED_INTEGER
		;

	offset_stop
		: UNSIGNED_INTEGER
		;

	offset_end
		: UNSIGNED_INTEGER
		;

//==============================================================================
window_function	// https://docs.databricks.com/sql/language-manual/sql-ref-window-functions.html#syntax
		// Tested
		: windowing_function (OVER window_over_what)?
		;

	window_over_what
		: window_name
		| L_PAREN window_name R_PAREN
		| window_spec
		;

	windowing_function
		: ranking_function
		| analytic_function
		| aggregate_function
		;

	// ---------------------------------------------------------------------
	ranking_function	// We don't need to get specific yet.
		// https://docs.databricks.com/sql/language-manual/sql-ref-functions-builtin.html#ranking-window-functions
		// Tested
		: DENSE_RANK	L_PAREN R_PAREN
		| NTILE		L_PAREN expression? R_PAREN
		| PERCENT_RANK	L_PAREN expression? R_PAREN
					// The documentation says it takes no arguments.
		| RANK		L_PAREN R_PAREN
		| ROW_NUMBER	L_PAREN R_PAREN
		;

	// ---------------------------------------------------------------------
	analytic_function
		// https://docs.databricks.com/sql/language-manual/sql-ref-functions-builtin.html#analytic-window-functions
		// No specific test cases as a group
		: CUME_DIST 	L_PAREN R_PAREN
		| LAG 		argument_list_wrapped
		| LEAD 		argument_list_wrapped
		| NTH_VALUE 	argument_list_wrapped
		;

	// ---------------------------------------------------------------------
	aggregate_function
		: function_name L_PAREN argument_list? R_PAREN
		| aggregate_function_first
		| aggregate_function_last
		;

	// ---------------------------------------------------------------------
	aggregate_function_first
		// https://docs.databricks.com/sql/language-manual/functions/first.html
		// Tested.
		: FIRST L_PAREN expression (COMMA boolean_literal)? R_PAREN filter_clause? 
		| FIRST L_PAREN expression (IGNORE NULLS)? R_PAREN filter_clause?
			// Not documented, but used in an example for Group By
		;

	// ---------------------------------------------------------------------
	aggregate_function_last
		// https://docs.databricks.com/sql/language-manual/functions/last.html
		// Tested
		: LAST L_PAREN expression (COMMA boolean_literal)? R_PAREN filter_clause?  (IGNORE NULLS | RESPECT NULLS)?
		;

	window_spec
		: L_PAREN
			partition_by_clause?
			order_by_clause?
			window_frame_clause?
			R_PAREN
		;

	partition_by_clause
		: PARTITION BY partition_by_list
		;

	partition_by_list
		: partition_by_list_item (COMMA partition_by_list_item)*
		;

	partition_by_list_item
		: partition_name
		| expression
		;

//==============================================================================
identifier		
		// https://docs.databricks.com/sql/language-manual/sql-ref-identifiers.html
		// Tested
		: REGULAR_ID
		| special_words_used_as_identifiers
		| SINGLE_QUOTED_STRING	// A string
		| DOUBLE_QUOTED_STRING	
		| DOLLAR_SIGN L_CURLY REGULAR_ID R_CURLY 	// An interpolated string
								// Such as: ${srcDate}
		;

	special_words_used_as_identifiers
		: TABLE
		| IS
		| DATE			// Used as a column name
		| DELTA			// Used as a schema name
		| YEAR			// Used as a column name
		| DEFAULT		// Used as a schema name
		| RANK			// Used as a column alias
		| DENSE_RANK		// Used as a column alias
		| CUME_DIST		// Used as a column alias
		| LAG			// Used as a column alias
		| LEAD			// Used as a column alias
		| WHERE			// Used as a table_name
		| SELECT		// Used as a boolean literal
		| NULL			// Used as a column name
		| KEY			// Used as an identifier
		| BY			// Used as an identifier
		| TARGET		// Used as a table name
		| SOURCE		// Used as a table name
		| RANGE			// Used as a function name
		| SQL			// Used as part of a property name
		| DATA			// Used as a table name
		| START			// Used as a function parameter
		| END			// Used as a function parameter
		| DAY			// Used as a return parameter
		| DAYS			// Used as a function parameter
		| LETTER_E		// Used as a table alias
		| PARQUET		// Used as a schema name
		| PARTITIONS		// Used as part of a property name
		| LETTER_V		// Used as a table_alias
		| LETTER_D		// Used as a table_alias
		| TABLES		// Used as a data dictionary view name
		| USER			// Used as part of a property name
		| LOCATION		// Used as a column name
		| PRIMARY		// Used as a column alias
		| JSON			// Used as a schema name
		| LIVE			// Used as a schema name
		| USERS			// Used as a table_name
		| SEQUENCE		// Used as a function name
		| TRIM			// Used as a function name
		| TIMESTAMP		// Used as a column name
		| FILTER		// Used as a column alias
		;

	reserved_words	
		// https://docs.databricks.com/sql/language-manual/sql-ref-reserved-words.html
		// None of the following tokens should be in the list
		// of special_words_used_as_identifiers
		: ANTI
		| CROSS
		| EXCEPT
		| FULL
		| INNER
		| INTERSECT
		| JOIN
		| LATERAL
		| LEFT
		| MINUS
		| NATURAL
		| ON
		| RIGHT
		| SEMI
		| UNION
		| USING

		// The following are not officially reserved words.
		// But Antlr won't parse SQL correctly if they are used as
		// regular identifiers, so they need to be reserved as far
		// as Antlr is concerned
		| FROM			// Used as a table_name
		;

identifier_list
		: identifier (COMMA identifier)*
		;

identifier_list_wrapped
		: L_PAREN identifier_list R_PAREN
		;

//==============================================================================
catalog_name	: identifier 
		| SINGLE_QUOTED_STRING ;

class_name	: identifier ;

collection_items_terminated_char
		: SINGLE_QUOTED_STRING
		;

column_name	: (schema_name DOT)? (table_name DOT)? identifier ;
		
column_name_list: column_name (COMMA column_name)* ;

column_name_list_wrapped
		: L_PAREN column_name_list R_PAREN
		;

comment_clause	: COMMENT (SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING);

connection_name	: identifier ;

constraint_name	: identifier ;

credential_name	: identifier ;

escaped_char	: SINGLE_QUOTED_STRING ;

fields_terminated_char
		: SINGLE_QUOTED_STRING ;

function_name	: identifier 
		| ARRAY 
		| MAP 
		| STRUCT ;

group_name	: identifier ;

location_name	: identifier ;

map_key_terminated_char
		: SINGLE_QUOTED_STRING ;

null_char	: SINGLE_QUOTED_STRING ;

parameter_name	: identifier ;

partition_column: identifier ;

partition_name	: (schema_name DOT)? identifier ;

pattern		: SINGLE_QUOTED_STRING ;

provider_name	: identifier ;

principal_name	: identifier ;

property_key 	: identifier (DOT identifier)* ;

recipient_name	: identifier ;

regex_pattern	: SINGLE_QUOTED_STRING ;

row_terminated_char
		: SINGLE_QUOTED_STRING ;

schema_name	: identifier ;

serde_class	: identifier ;

share_name	: identifier ;

table_identifier: identifier ;

table_name	: (catalog_name DOT)? (schema_name DOT)? identifier ;

version		: UNSIGNED_INTEGER ;

view_identifier	: identifier ;

view_name	: identifier;

volume_name	: identifier ;

window_name	: identifier ;
