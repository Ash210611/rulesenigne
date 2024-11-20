from un_re.run_pg_statement import run_pg_statement


# ===============================================================================
def get_cfg_table_comment(schema_name, table_name):
    '''
    Retrieve the table comment for the cfg table.
    '''

    sql = f"select obj_description('{schema_name}.{table_name}'::regclass, 'pg_class');"

    rows = run_pg_statement(sql)

    return rows
