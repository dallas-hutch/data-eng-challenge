from utils import load_transaction_data, clean_and_enrich_transactions, insert_clean_data_into_db, detect_near_duplicates

df = load_transaction_data("data/transactions.csv")
df_clean = clean_and_enrich_transactions(df)
insert_clean_data_into_db(df_clean)
dupes = detect_near_duplicates(df_clean)
print(df.dtypes)

print(f"Found {len(dupes)} potential duplicates")
for idx in list(dupes)[:5]:
    print(df_clean.iloc[idx][["transaction_id", "processed_timestamp"]])