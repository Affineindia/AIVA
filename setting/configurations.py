from azure.core.credentials import AzureKeyCredential 
from azure.search.documents import SearchClient  
from azure.ai.contentsafety import ContentSafetyClient
from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine
from openai import AzureOpenAI  
import os
import urllib
from dotenv import load_dotenv

PATH = os.getcwd() +r'\.env'
load_dotenv()

class Config():
    def __init__(self):
        # APP AUTH

        self.token = os.getenv("TOKEN")
        
        # CONTENT SAFETY CONFIGURATION

        SAFETY_API_ENDPOINT = os.getenv("SAFETY_API_ENDPOINT")
        SAFETY_API_KEY = os.getenv("SAFETY_API_KEY")
        
        self.safety_client = ContentSafetyClient(endpoint=SAFETY_API_ENDPOINT, credential=AzureKeyCredential(SAFETY_API_KEY))

        # SEARCH CONFIGURATION

        SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
        SEARCH_KEY = os.getenv("SEARCH_KEY")
        SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")
        azure_search_credential = AzureKeyCredential(SEARCH_KEY)
        self.search_client = SearchClient(endpoint=SEARCH_ENDPOINT,
                                        index_name=SEARCH_INDEX_NAME,
                                        credential=azure_search_credential
                                        )
        self.text_embedding_model = "ada-text-embeddings-002"

        # VISION CONFIGUARATIONS

        VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")
        VISION_KEY = os.getenv("VISION_KEY")
        self.vision_url = f"{VISION_ENDPOINT}/computervision/retrieval:vectorizeImage?api-version=2024-02-01&model-version=2023-04-15"
        self.vision_headers = {
            "Ocp-Apim-Subscription-Key": VISION_KEY,
            "Content-Type": "application/octet-stream"
        }

        # BLOB CONFIGURATION

        BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
        self.BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
        self.BLOB_UPLOAD_CONTAINER_NAME = os.getenv("BLOB_UPLOAD_CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

        # OPENAI CONFIGURATION

        OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
        OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
        OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_VERSION = os.getenv("OPENAI_VERSION")

        self.llm_config = {
            "config_list":[
            {
                "model": OPENAI_DEPLOYMENT_NAME,
                "api_type": OPENAI_API_TYPE,
                "base_url": OPENAI_API_ENDPOINT,
                "api_key": OPENAI_API_KEY,
                "api_version": OPENAI_VERSION,
            }
        ]
        ,
            # "seed": 43,
            "temperature": 0.1,
            # "max_tokens": -1,
            # "request_timeout": 6000
        }

        self.client = AzureOpenAI(
                api_key=OPENAI_API_KEY,
                api_version=OPENAI_VERSION,
                azure_endpoint=OPENAI_API_ENDPOINT
            )
        
        # SQL CONFIGURATION
        SQL_SERVER = os.getenv("SQL_SERVER")
        SQL_DATABASE = os.getenv("SQL_DATABASE")
        SQL_USERNAME = os.getenv("SQL_USERNAME")
        SQL_PASSWORD = os.getenv("SQL_PASSWORD")
        SQL_DRIVER = os.getenv("SQL_DRIVER")
        SQL_ENCODING = os.getenv("SQL_ENCODING")
        SQL_CATEGORY_NAME = os.getenv("SQL_CATEGORY_NAME")
        CONNECTION_STRING = f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(f"DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}")}'
        
        self.engine = create_engine(CONNECTION_STRING)

        # GENERAL
        self.sender_details = "replier name : AIVA (Affine Intelligent Virtual Assistant), Position : Your Intelligent Affine Support Agent"
        self.domain = "Orders, inventory, invoices, distributors, suppliers, contact details, payments, products, purchases, product features, Transactions, shipping, delivery, supply chain, inventory, policies, support, refund, pricing, anything related to business"

        