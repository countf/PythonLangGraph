import os
from dotenv import load_dotenv

# 自动加载项目根目录.env
load_dotenv()

# 从系统环境变量取值，全程代码无明文密钥
API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "mimo-v2.5-pro")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MODEL_URL = os.getenv("MODEL_URL")
MODEL_Video = os.getenv("MODEL_VIDEO")
