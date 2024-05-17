

def update_balance(key, pdfs_iter, state: GroupState):

    # Handle transactions for unloaded wallet IDs
    if state.exists:
        (current_balance,) = state.get
    else:
        current_balance = 0

    currency = None

    for df in pdfs_iter:

        if currency is None:
            currency = df['currency'].iloc[0]

        df['amount'] = df['amount'].astype(float)
        df.loc[df['type'].isin(['credit', 'cancelDebit']), 'amount'] *= 1
        df.loc[df['type'].isin(['debit', 'cancelCredit']), 'amount'] *= -1
        total_amount = df['amount'].sum()
        current_balance += total_amount

    state.update((current_balance,))
    yield pd.DataFrame({"wallet_id": [key[0]], "balance": [str(current_balance)], 'currency': [currency]})


def update_avg_debit(key, pdfs_iter, state: GroupState):
    wallet_id = str(key[0])

    # Handle transactions for unloaded wallet IDs
    if state.exists:
        (total_debit, debit_days, last_transaction_date)= state.get
    else:
        total_debit = 0.0
        debit_days = 0
        last_transaction_date = None

    batch_debit = 0
    date_list = []

    for df in pdfs_iter:

        if df is None:
            continue

        df['amount'] = df['amount'].astype(int)
        batch_debit += df.loc[df['type']=='debit']['amount'].sum()
        date_list.append(pd.to_datetime(df['timestamp']).max().to_pydatetime())


    new_total_debit = batch_debit + total_debit
    batch_max_date = max(date_list)

    if last_transaction_date is not None and batch_max_date > last_transaction_date:
        days_delta = (batch_max_date - last_transaction_date).days
        new_total_days = days_delta + debit_days
        last_transaction_date = batch_max_date
    elif last_transaction_date is None:
        last_transaction_date = batch_max_date
        new_total_days = 1
    else:
        new_total_days = debit_days

    state.update((new_total_debit,new_total_days, last_transaction_date))
    yield pd.DataFrame({"wallet_id": [wallet_id], "avg_debit": [round(new_total_debit/new_total_days,2)]})



def update_top5_credits(key, pdfs_iter, state: GroupState):

    # Handle transactions for unloaded wallet IDs
    if state.exists:
        current_top_credits_json = state.get[0]
        current_top_credits = json.loads(current_top_credits_json)
        current_top_credits_df = pd.DataFrame(current_top_credits)
    else:
        current_top_credits_df = None

    combined_df = current_top_credits_df
    for df in pdfs_iter:
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # filter in only credit transactions, then sort in descending order and get the top 5 records.
    live_top_5_credits_df = combined_df.loc[(combined_df['type']=='credit')]\
                                    .sort_values(by='amount', ascending=False)\
                                    .head(5)

    live_top_5_credits_str = live_top_5_credits_df.to_json(orient='records')
    state.update((live_top_5_credits_str,))
    yield pd.DataFrame({"product_id": [key[0]], "top_5_credits": live_top_5_credits_str})
