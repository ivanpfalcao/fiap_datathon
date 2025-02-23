import pandas as pd
import numpy as np

import logging
import duckdb


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

class GloboData():
    def __init__(self
            ,output_folder
        ):
        self.conn = duckdb.connect()
        self.output_folder = output_folder

    def prep_reduced_itens(self):

        query=f""" 
            with history_list as (
                SELECT
                    unnest(history_list) as hist
                FROM read_parquet('{self.output_folder}/unnested_treino.parquet')
            ),
            teste_list as (
                SELECT
                    un_history as hist
                FROM read_parquet('{self.output_folder}/unnested_treino.parquet')
            ),    
            hist_n_test as (
                SELECT
                    hist
                FROM history_list

                UNION

                SELECT
                    hist
                FROM teste_list
            ),
            distinct_hist_ids as (

                SELECT
                    DISTINCT hist
                FROM hist_n_test
            ),
            enriched_items as (
                SELECT
                    *
                FROM read_parquet('{self.output_folder}/itens.parquet')
            )    
            SELECT
                *
            --FROM enriched_items  
            FROM distinct_hist_ids
            INNER JOIN enriched_items ON hist = page
        """  

        unnested_treino_df = self.conn.execute(query).fetchdf()
        logging.info(f"Reduced items generated")
        unnested_treino_df.to_parquet(f'{self.output_folder}/reduced_itens.parquet')     


    def prepare_itens(self, items_files):
        self.load_itens(
            items_files
        )
        df = self.items_data_prep()

        df.to_parquet(f'{self.output_folder}/itens.parquet')     


    def prepare_treino(self, treino_files):
        self.load_treino(
            treino_files
        )
        prep_treino_df = self.get_train_test_data()

        prep_treino_df.to_parquet(f'{self.output_folder}/treino.parquet')     

        unnest_treino_df = self.prepare_unnested_treino(prep_treino_df)
        unnest_treino_df.to_parquet(f'{self.output_folder}/unnested_treino.parquet')     


    def prepare_unnested_treino(self, prep_treino_df):
        query = f"""
            SELECT 
                *
                ,unnest(history_list) as un_history
                ,unnest(timestampHistory_list) as un_ts_history
                ,LIST_CONTAINS(history_test_list, unnest(history_list)) as is_test                 
            FROM prep_treino_df
        """
        unnested_treino_df = self.conn.execute(query).fetchdf()
        logging.info(f"Unnested treino generated")
        return unnested_treino_df
    
    def load_itens(self, itens_file_path):
        logging.info(f"Loading csv from {itens_file_path}")
        query = f"""
            CREATE TABLE items AS (
                SELECT 
                    * 
                FROM read_csv_auto('{itens_file_path}')
            )
        """
        self.conn.execute(query)

    def load_treino(self, treino_file_path, limit=1000):
        logging.info(f"Loading csv from {treino_file_path}")
        query = f"""
            CREATE TABLE treino AS (
                SELECT 
                    * 
                FROM read_csv_auto('{treino_file_path}')
                LIMIT {limit}
            )
        """
        self.conn.execute(query)
        logging.info(f"Loaded csv from {treino_file_path}")

    def items_data_prep(self):
        logging.info("Getting news data")
        query = """
            SELECT 
                trim(page) as page,
                url,
                issued,
                modified,
                title,
                caption,
                body
            FROM
                items
        """
        result = self.conn.execute(query).fetchdf()
        return result

    def get_train_test_data(self):
        logging.info("Getting train data")
        query = """
            SELECT
                trim(userId) as userId,
                userType,
                historySize,
                history,
                timestampHistory,
                string_split(
                    replace(replace(replace(replace(history, '''', ''), ']', ''), '[', ''), ' ', ''),
                    ','
                ) as history_list,
                string_split(
                    replace(replace(replace(replace(history, '''', ''), ']', ''), '[', ''), ' ', ''),
                    ','
                )[0 : (floor(historySize / 2))] AS history_train_list,
                string_split(
                    replace(replace(replace(replace(history, '''', ''), ']', ''), '[', ''), ' ', ''),
                    ','
                )[(floor(historySize / 2) + 1) : (historySize)] AS history_test_list,

                string_split(
                    replace(replace(replace(replace(timestampHistory, '''', ''), ']', ''), '[', ''), ' ', ''),
                    ','
                ) AS timestampHistory_list,
                string_split(
                    replace(replace(replace(replace(timestampHistory, '''', ''), ']', ''), '[', ''), ' ', ''),
                    ','
                )[(floor(historySize / 2) + 1) : (historySize)] AS test_timestamp_list                
            FROM treino
        """
        result = self.conn.execute(query).fetchdf()
        return result