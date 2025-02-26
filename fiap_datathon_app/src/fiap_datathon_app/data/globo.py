import requests
import json

import logging
import duckdb

import pandas as pd

from datetime import datetime, timedelta, timezone


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

        first_news_df = self.prepare_first_news(prep_treino_df)
        first_news_df.to_parquet(f'{self.output_folder}/first_news.parquet')


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
    
    def prepare_first_news(self, prep_treino_df):
        query = f"""
            WITH dense_table AS (
                SELECT 
                    history_list[1] AS first_news,
                    timestampHistory_list[1] AS first_news_timestamp,
                    DENSE_RANK() OVER (PARTITION BY history_list ORDER BY timestampHistory_list[1] desc) AS dense_rank
                FROM 
                    prep_treino_df
                ORDER BY 
                    first_news desc, dense_rank asc
            )
            SELECT
            first_news
            ,first_news_timestamp
            FROM dense_table
            WHERE dense_rank=1
        """
        first_news = self.conn.execute(query).fetchdf()
        logging.info(f"First news generated")
        return first_news


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
    
    def add_news_from_dataframe(self, input_file: str, url: str, api_key: str, news_per_request = 10):
        """
        Envia notícias para a API em lotes de 10 a partir de um DataFrame.

        Args:
            input_file (str): Caminho para o arquivo parquet com os dados das notícias.
            url (str): URL da API para enviar as notícias.
            api_key (str): Chave de API para autenticação.
        """

        try:
            input_df = pd.read_parquet(input_file)
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em '{input_file}'")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        for i in range(0, len(input_df), news_per_request):
            batch_df = input_df[i:i + news_per_request]
            news_list = []

            for _, row in batch_df.iterrows():
                # Convert timestamp to string in the required format
                issued_str = row["issued"].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                news_item = {
                    "page": row["page"],
                    "issued": issued_str,
                    "body": row["body"],
                }
                news_list.append(news_item)

            data = {"news_list": news_list}

            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                print(json.dumps(response.json()))
            except requests.exceptions.RequestException as e:
                print(f"Erro ao enviar lote de notícias: {e}")
            except json.JSONDecodeError:
                print("Resposta da API não é um JSON válido.")
                print(response.text)

    def add_first_news_from_dataframe(self, input_file: str, url: str, api_key: str, news_per_request = 10):
        """
        Envia notícias para a API em lotes de 10 a partir de um DataFrame.

        Args:
            input_file (str): Caminho para o arquivo parquet com os dados das notícias.
            url (str): URL da API para enviar as notícias.
            api_key (str): Chave de API para autenticação.
        """

        try:
            input_df = pd.read_parquet(input_file)
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em '{input_file}'")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        for i in range(0, len(input_df), news_per_request):
            batch_df = input_df[i:i + news_per_request]
            news_list = []

            for _, row in batch_df.iterrows():
                # Convert timestamp to string in the required format
                timestamp_s = int(row["first_news_timestamp"]) / 1000.0  # Convert milliseconds to seconds
                dt_object = datetime.fromtimestamp(timestamp_s, timezone.utc)
                
                viewed_str = dt_object.strftime('%Y-%m-%dT%H:%M:%S.000Z')                

                news_item = {
                    "page": row["first_news"],
                    "viewed": viewed_str
                }
                news_list.append(news_item)

            data = {"first_news_list": news_list}

            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                print(json.dumps(response.json()))
            except requests.exceptions.RequestException as e:
                print(f"Erro ao enviar lote de notícias: {e}")
            except json.JSONDecodeError:
                print("Resposta da API não é um JSON válido.")
                print(response.text)


    def call_inference_api(self
                        , viewed_news: list[str]
                        , init_time: str
                        , end_time: str
                        , top_n=2
                        , news_text=False
                        , url='http://127.0.0.1:8000/recommendation/'
                        , api_key='dsafadsflkfjgoirvklvfdiodrjfodflk'
        ) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "viewed_news": viewed_news
            #"init_time": "2020-12-31T00:00:00Z",
            #"end_time": "2026-12-31T00:00:00Z"
            ,"init_time": init_time
            ,"end_time": end_time           
            ,"top_n": top_n
            ,"news_text": news_text
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            return response.json()
        except requests.exceptions.RequestException as e:
            logging.info(f"An error occurred: {e}")
            return None
        except json.JSONDecodeError:
            logging.info("Response is not valid JSON")
            logging.info(response.text) 
            return None

    def massive_inference_tests(self
            , opt_input_file:str = None
            , init_index = 0
            , end_index = 100
            , url='http://127.0.0.1:8000/recommendation/'
            , api_key='dsafadsflkfjgoirvklvfdiodrjfodflk'
            , number_of_days_before = 45
            , number_of_days_after = 1
            , top_n = 2
            , news_text = False
            , max_news_to_infer = 5
            
            ):
        """
        Envia notícias para a API em lotes de 10 a partir de um DataFrame.

        Args:
            input_file (str): Caminho para o arquivo parquet com os dados das notícias.
            url (str): URL da API para enviar as notícias.
            api_key (str): Chave de API para autenticação.
        """

        if (opt_input_file is None):
            input_file = f'{self.output_folder}/treino.parquet'
        else: 
            input_file = opt_input_file

        try:
            input_df = pd.read_parquet(input_file).iloc[init_index:end_index]
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em '{input_file}'")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

        with open(f'{self.output_folder}/inferences.json', 'w') as out_file:
            for _, row in input_df.iterrows():
                try:

                    #un_history = row['un_history']
                    view_ts = float(row['test_timestamp_list'][0])
                    reference_date = datetime.fromtimestamp(view_ts / 1000.0, tz=timezone.utc)

                    logging.info(f'Processing user row... reference date: {reference_date}')

                    # Example: 10-day window behind, 1-day window ahead
                    start_date = (reference_date - timedelta(days=number_of_days_before)).strftime('%Y-%m-%dT%H:%M:%SZ')
                    end_date = (reference_date + timedelta(days=number_of_days_after)).strftime('%Y-%m-%dT%H:%M:%SZ')  

                    logging.info(f'Init Date: {start_date}')
                    logging.info(f'End Date: {end_date}')

                    test_list = row['history_train_list'].tolist()[-max_news_to_infer:-1]
                    inference_dict = self.call_inference_api(
                        viewed_news = test_list
                        , init_time = start_date
                        , end_time = end_date
                        , top_n=top_n
                        , news_text=news_text
                        , url=url
                        , api_key=api_key
                    )

                    #logging.info(f'Inference: {inference_dict}')
                    inference_json = json.dumps(inference_dict)
                    out_file.write(inference_json + '\n')
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao enviar lote de notícias: {e}")
                except json.JSONDecodeError:
                    print("Resposta da API não é um JSON válido.")                           