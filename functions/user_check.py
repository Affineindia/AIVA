def user_check(config, email_id):
    try:
        import pandas as pd
        # Execute the query and fetch the result into a DataFrame
        query = f"SELECT * FROM User_Details WHERE Email_Id='{email_id}'"
        df = pd.read_sql(query, config.engine)
        if len(df)>0:
            check = True
        else:
            check = False
        return check
    except Exception as e:
        return f"An error occurred while execusting the query:{e}"
    