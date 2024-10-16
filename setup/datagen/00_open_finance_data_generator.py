# Databricks notebook source
# MAGIC %md
# MAGIC # Step 1: Initialization Cells

# COMMAND ----------

!pip install -qqq faker
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ../config

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 2: Run Open Finance data generated

# COMMAND ----------

import pandas as pd
from faker import Faker
import random
import uuid
from pyspark.sql import DataFrame

fake = Faker()

# UDFs for generating data
fake_bank_name = lambda: fake.random_element(elements=("Itaú Unibanco", "Banco do Brasil", "Caixa Econômica Federal", "Bradesco", "Santander Brasil", "Banco Safra", "Sicoob", "Nubank", "PicPay"))
fake_address = lambda: fake.address()
fake_city = lambda: fake.random_element(elements=("São Paulo", "Brasilia", "Belo Horizonte", "Rio de Janeiro"))
fake_data_transaction = lambda: fake.date_this_month().strftime("%Y-%m-%d")
fake_category = lambda: fake.random_element(elements=("Salary", "Household bills", "Benefits", "Leisure", "Withdrawals", "Reimbursement", "Loan", "Personal care", "Family", "Education", "Travel", "Bonus", "TV, phone and internet", "Domestic employees", "Bank fees", "Other income", "Undefined expense", "Work expenses", "Taxes", "Income", "Transportation", "Gifts and donations", "Housing", "Rent", "Pets", "Services", "Bars and restaurants", "Health", "Grocery", "Shopping"))
fake_operation = lambda: fake.random_element(elements=("CREDIT", "DEBIT"))
fake_type = lambda: fake.random_element(elements=("CHECK ACCOUNT", "SAVINGS ACCOUNT", "CREDIT CARD", "DEBIT CARD"))
fake_card_type = lambda: fake.random_element(elements=("GOLD", "PLATINUM"))
fake_network = lambda: fake.random_element(elements=("VISA", "MASTERCARD"))
fake_value = lambda: round(random.uniform(0.0, 10000.0), 2)
fake_loan_id = lambda: str(uuid.uuid4())
fake_loan_date = lambda: fake.date_this_month().strftime("%Y-%m-%d")
fake_loan_amount = lambda: round(random.uniform(0.0, 100000.0), 2)
fake_interest_rate = lambda: round(random.uniform(0.0, 20.0), 2)
fake_loan_term = lambda: random.randint(1, 100)
fake_loan_value = lambda: round(random.uniform(1000.0, 100000.0), 2)
fake_installment_amount = lambda: round(random.uniform(0.0, 10000.0), 2)
fake_financing_id = lambda: str(uuid.uuid4())
fake_financing_date = lambda: fake.date_this_month().strftime("%Y-%m-%d")
fake_financing_amount = lambda: round(random.uniform(0.0, 100000.0), 2)
fake_financing_term = lambda: random.randint(1, 100)
fake_financing_value = lambda: round(random.uniform(1000.0, 100000.0), 2)
fake_personal_id = lambda: str(uuid.uuid4())
fake_name = lambda: fake.name()
fake_birth_date = lambda: fake.date()
fake_sex = lambda: fake.random_element(elements=("M", "F"))
fake_ssn = lambda: fake.ssn()
fake_email = lambda: fake.email()
fake_initial_balance = lambda: round(random.uniform(0.0, 10000.0), 2)
fake_current_balance = lambda: round(random.uniform(0.0, 10000.0), 2)

# Function to create DataFrame for Bank Dataset
def create_bank_df(size):
    df = pd.DataFrame({
        "bank_name": [fake_bank_name() for _ in range(size)],
        "address": [fake_address() for _ in range(size)],
        "city": [fake_city() for _ in range(size)]
    })
    return df

# Function to create DataFrame for Transactions Dataset
def create_transactions_df(size, personal_ids, bank_names):
    df = pd.DataFrame({
        "personal_id": [random.choice(personal_ids) for _ in range(size)],
        "data_transaction": [fake_data_transaction() for _ in range(size)],
        "category": [fake_category() for _ in range(size)],
        "operation": [fake_operation() for _ in range(size)],
        "type": [fake_type() for _ in range(size)],
        "bank_name": [random.choice(bank_names) for _ in range(size)],
        "card_type": [fake_card_type() for _ in range(size)],
        "network": [fake_network() for _ in range(size)],
        "value": [fake_value() for _ in range(size)]
    })
    return df

# Function to create DataFrame for Loan Dataset
def create_loan_df(size, personal_ids, bank_names):
    df = pd.DataFrame({
        "loan_id": [fake_loan_id() for _ in range(size)],
        "personal_id": [random.choice(personal_ids) for _ in range(size)],
        "loan_date": [fake_loan_date() for _ in range(size)],
        "loan_value": [fake_loan_value() for _ in range(size)],
        "loan_term": [fake_loan_term() for _ in range(size)],
        "interest_rate": [fake_interest_rate() for _ in range(size)],
        "bank_name": [random.choice(bank_names) for _ in range(size)]
    })
    return df

# Function to create DataFrame for Financing Dataset
def create_financing_df(size, personal_ids, bank_names):
    df = pd.DataFrame({
        "financing_id": [fake_financing_id() for _ in range(size)],
        "personal_id": [random.choice(personal_ids) for _ in range(size)],
        "financing_date": [fake_financing_date() for _ in range(size)],
        "financing_value": [fake_financing_value() for _ in range(size)],
        "financing_term": [fake_financing_term() for _ in range(size)],
        "interest_rate": [fake_interest_rate() for _ in range(size)],
        "bank_name": [random.choice(bank_names) for _ in range(size)]
    })
    return df

# Function to create DataFrame for Personal Dataset
def create_account_df(size, personal_ids, bank_names):
    df = pd.DataFrame({
        "account_id": [fake_financing_id() for _ in range(size)],
        "personal_id": [random.choice(personal_ids) for _ in range(size)],
        "bank_name": [random.choice(bank_names) for _ in range(size)],
        "initial_balance": [fake_initial_balance() for _ in range(size)],
        "current_balance": [fake_current_balance() for _ in range(size)]
    })
    return df

# Function to create DataFrame for Personal Dataset
def create_personal_df(size, bank_names):
    personal_ids = [fake_personal_id() for _ in range(size)]
    df = pd.DataFrame({
        "personal_id": personal_ids,
        "name": [fake_name() for _ in range(size)],
        "birth_date": [fake_birth_date() for _ in range(size)],
        "sex": [fake_sex() for _ in range(size)],
        "ssn": [fake_ssn() for _ in range(size)],
        "address": [fake_address() for _ in range(size)],
        "email": [fake_email() for _ in range(size)],
        "bank_id": [random.choice(bank_names) for _ in range(size)],

    })
    return df, personal_ids

# Example usage
bank_df = create_bank_df(5)
bank_names = bank_df["bank_name"].tolist()
personal_df, personal_ids = create_personal_df(2, bank_names)
transactions_df = create_transactions_df(10000, personal_ids, bank_names)
loan_df = create_loan_df(5, personal_ids, bank_names)
financing_df = create_financing_df(5, personal_ids, bank_names)
accounts_df = create_account_df(20, personal_ids, bank_names)


# creating dataframes spark
bank_sdf = spark.createDataFrame(bank_df)
personal_sdf = spark.createDataFrame(personal_df)
transactions_sdf = spark.createDataFrame(transactions_df)
loan_sdf = spark.createDataFrame(loan_df)
financing_sdf = spark.createDataFrame(financing_df)
accounts_sdf = spark.createDataFrame(accounts_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 3: Creating all tables

# COMMAND ----------

def create_table_from_ctas(table_name):
    qryCtas = f"""CREATE TABLE IF NOT EXISTS {catalog_name}.{schema_name}.{table_name}
                    TBLPROPERTIES (delta.autoOptimize.optimizeWrite = true, delta.autoOptimize.autoCompact = 'auto')
                    AS
                    SELECT * FROM sourceDataView"""
    spark.sql(qryCtas)  

# COMMAND ----------

bank_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_bank')

personal_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_personal')

transactions_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_transaction')

loan_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_loan')

financing_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_financing')

accounts_sdf.createOrReplaceTempView("sourceDataView")
create_table_from_ctas('tb_accounts')