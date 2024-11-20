//
// Antrl grammar for Teradata v15.10 COMMENT ON commands
// 
//==============================================================================

grammar TD15_comment_on;

root 
		: single_statement+ EOF
		;

single_statement
		: v1=statement
			{System.out.println();
			 System.out.println("Parsed single_statement      : " + $v1.text);
			 System.out.println("========= ========= ========= ========= ========= =====");}
			// NOTE: That text is searched by DREML
    		;

statement 	: comment_on
		;

//=============================================================================
// Rules for the Comment On command
// In the Comment On Column command, the columnName identifier must include at
// least one dot, to identify the table name.
// In the Comment on Table command, the tableName identifier may or may not 
// include a dot.  It might, if it includes the databaseName.   Or the 
// databaseName might come from the default databaseName.

comment_on	  			// TD15.10 SQL Data Definition Language, p1061
	: COMMENT ON?
            	COLUMN
			{System.out.println ("Statement Type               : COMMENT ON COLUMN");}
		v1=comment_column_name
		((AS | IS)? v2=STRING)?
		DELIMITER
			{System.out.println("Found comment-on object      : " + $v1.text);
		 	System.out.println("Found comment-on string      : " + $v2.text);}
			// NOTE: That text is used by DAMODRE
	| COMMENT ON?
            	TABLE
			{System.out.println ("Statement Type               : COMMENT ON TABLE");}
		v3=qualifiedName
		((AS | IS)? v4=STRING)?
		DELIMITER
			{System.out.println("Found comment-on object      : " + $v3.text);
		 	System.out.println("Found comment-on string      : " + $v4.text);}
			// NOTE: That text is used by DAMODRE
		;

	comment_column_name
		: qualifiedName (DOT identifier)+
		;

//=============================================================================
qualifiedName
		: identifier
			// for example a table name, or a column name

		| identifier DOT identifier
			// for example, a DB.table_name, or a Table.column_name

		| identifier DOT identifier DOT identifier
			// for example a DB.table_name.column_name

		// | 'SYS_CALENDAR.CALENDAR'	
			// Must avoid matching the CALENDAR keyword by itself.
			// Otherwise the lexer tokenizes the CALENDAR keyword,
			// which keeps it from being matched as a tablename.

		//| SESSION
			// Is used in the CCW_LOAD_CTL table
		;

identifier 	: IDENTIFIER                                
		| LEFT_BRACKET IDENTIFIER RIGHT_BRACKET
		| IDENTIFIER DOLLAR OPEN_CURLY IDENTIFIER CLOSE_CURLY
		| QUOTED_IDENTIFIER
    		| BACKQUOTED_IDENTIFIER                  
		// Adding the following for keywords used as column names
		| LABEL
		| ERRORCODE
		| SQL
		| ATTR
		// | SQLSTATE
		| CLIENT
		// | NEXT
		// | INDEX
		| STAT
		| CONDITION
		| LEVEL
		| PERIOD
		| STATS
		// | TYPE
		// Adding the following for keywords used a databasename
		// | TD_SYSFNLIB
		;

//==============================================================================
// Lexer rules below.

AS              : [Aa][Ss];
ATTR		: [Aa][Tt][Tt][Rr];
CLIENT		: [Cc][Ll][Ii][Ee][Nn][Tt];
COLUMN          : [Cc][Oo][Ll][Uu][Mm][Nn];
COMMENT         : [Cc][Oo][Mm][Mm][Ee][Nn][Tt];
CONDITION	: [Cc][Oo][Nn][Dd][Ii][Tt][Ii][Oo][Nn];
// DATABASE        : [Dd][Aa][Tt][Aa][Bb][Aa][Ss][Ee];
ERRORCODE       : [Ee][Rr][Rr][Oo][Rr][Cc][Oo][Dd][Ee];
FILE            : [Ff][Ii][Ll][Ee];
FUNCTION        : [Ff][Uu][Nn][Cc][Tt][Ii][Oo][Nn];
// GLOP            : [Gg][Ll][Oo][Pp];
// INDEX           : [Ii][Nn][Dd][Ee][Xx];
IS              : [Ii][Ss];
LABEL           : [Ll][Aa][Bb][Ee][Ll];
LEVEL           : [Ll][Ee][Vv][Ee][Ll];
MACRO           : [Mm][Aa][Cc][Rr][Oo];
// METHOD          : [Mm][Ee][Tt][Hh][Oo][Dd];
// NEXT            : [Nn][Ee][Xx][Tt];
ON              : [Oo][Nn];
PERIOD          : [Pp][Ee][Rr][Ii][Oo][Dd];
// PROCEDURE       : [Pp][Rr][Oo][Cc][Ee][Dd][Uu][Rr][Ee];
// PROFILE         : [Pp][Rr][Oo][Ff][Ii][Ll][Ee];
// ROLE            : [Rr][Oo][Ll][Ee];
// SESSION         : [Ss][Ee][Ss][Ss][Ii][Oo][Nn];
SET             : [Ss][Ee][Tt];
SQL             : [Ss][Qq][Ll];
// SQLSTATE        : [Ss][Qq][Ll][Ss][Tt][Aa][Tt][Ee];
STAT            : [Ss][Tt][Aa][Tt];
STATS           : [Ss][Tt][Aa][Tt][Ss];
TABLE           : [Tt][Aa][Bb][Ll][Ee];
// TD_SYSFNLIB	: [Tt][Dd][_][Ss][Yy][Ss][Ff][Nn][Ll][Ii][Bb];
// TRIGGER         : [Tt][Rr][Ii][Gg][Gg][Ee][Rr];
// TYPE            : [Tt][Yy][Pp][Ee];
USER            : [Uu][Ss][Ee][Rr];
VIEW            : [Vv][Ii][Ee][Ww];

DOLLAR		: '$' ;
DOT		: '.' ;
LEFT_BRACKET 	: '[' ;
RIGHT_BRACKET 	: ']' ;
OPEN_CURLY	: '\\{' ;
CLOSE_CURLY	: '\\}' ;

BACKQUOTED_IDENTIFIER
    		: '`' ( ~'`' | '``' )* '`'
    		;
IDENTIFIER 	: (LETTER | '_') (LETTER | DIGIT | '_' | '@' )* ;
STRING 		: '\'' ( ~'\'' | '\'\'' )* '\'' ;

QUOTED_IDENTIFIER
    : '"' ( ~'"' | '""' )* '"'
    ;

DELIMITER		: ';';

SIMPLE_COMMENT 		: '--' ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN) ;

BRACKETED_COMMENT 	: '/*' .*? '*/' -> channel(HIDDEN) ;

LINE_CONTINUATION_1	: '-\r'		-> skip ;
LINE_CONTINUATION_2	: '-\n'		-> skip ;

WS			: [ \r\n\t]+ 	-> skip ;

fragment LETTER	: [a-zA-Z] ;
fragment DIGIT 	: [0-9];

