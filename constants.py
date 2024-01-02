import configparser
import os
from handler.document_extraction import pdf_extraction, txt_extraction, word_docs_extraction

config = configparser.ConfigParser()
config.read('settings.conf')

api_base_service_url = "/fastapi/template"

LOG_LEVEL = config.get('LOG', 'log_level')
LOG_BASEPATH = config.get('LOG', 'base_path')
LOG_FILE_NAME = LOG_BASEPATH + config.get('LOG', 'file_name')
LOG_HANDLERS = config.get('LOG', 'handlers')
LOGGER_NAME = config.get('LOG', 'logger_name')


pwd = os.getcwd()

list_file_types={"pdf":pdf_extraction, "txt":txt_extraction, "docx":word_docs_extraction, "doc":word_docs_extraction}