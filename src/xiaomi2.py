import os
from openai import OpenAI
from config import API_KEY, MODEL_URL, MODEL_NAME
client = OpenAI(
    api_key=API_KEY,  # 你的MIMO密钥
    base_url=MODEL_URL  # 第三方接口地址
)

completion = client.chat.completions.create(
    model="mimo-v2.5-pro",
    messages=[
        {
            "role": "system",
            "content": "你是MiMo（中文名称也是MiMo），是小米公司研发的AI智能助手。今天的日期：{date} {week}，你的知识截止日期是2024年12月。"
        },
        {
            "role": "user",
            "content": "你是谁？"
        }
    ],
    max_completion_tokens=1024,
    temperature=1.0,
    top_p=0.95,
    stream=False,
    stop=None,
    frequency_penalty=0,
    presence_penalty=0,
    extra_body={
        "thinking": {"type": "disabled"}
    }
)

print(completion.choices[0].message.content)

