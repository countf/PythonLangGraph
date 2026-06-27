from openai import OpenAI
from config import API_KEY, MODEL_URL, MODEL_NAME
# 初始化客户端，只需要加 base_url
client = OpenAI(
    api_key=API_KEY,  # 你的MIMO密钥
    base_url=MODEL_URL  # 第三方接口地址
)

# 调用方式和官方完全一致
completion = client.chat.completions.create(
    model="mimo-v2.5-pro",  # 第三方平台的模型名
    messages=[
        {"role": "system", "content": "You are MiMo, an AI assistant developed by Xiaomi."},
        {"role": "user", "content": "你好，介绍一下你自己"}
    ]
)

print(completion.choices[0].message.content)