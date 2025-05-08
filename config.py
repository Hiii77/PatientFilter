from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# API配置
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

