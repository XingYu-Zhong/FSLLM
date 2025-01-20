import os
from dotenv import load_dotenv

class ConfigJson:
    def __init__(self):
        load_dotenv()
        self.tushare_token = None
        self.mjs_token = None

    def get_account(self):
        self.tushare_token = os.getenv('TUSHARE_TOKEN')
        self.mjs_token = os.getenv('MJS_TOKEN')
        
        if not self.tushare_token or not self.mjs_token:
            raise ValueError("TUSHARE_TOKEN or MJS_TOKEN not found in environment variables") 