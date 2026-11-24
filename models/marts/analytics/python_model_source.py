def model(dbt, session):

    my_sql_model_df = dbt.source('eth', 'contracts')

    return my_sql_model_df