from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),  # 你的MIMO密钥
    base_url=os.getenv("MODEL_URL"),  # 第三方接口地址
    timeout=30.0
)

# 系统提示词（全局生效）
SYSTEM_PROMPT = """
你是小米开发的AI助手MiMo，全程只用中文回答，语气亲切自然。
当前日期：{date} {week}，知识截止到2024年12月。
"""

print("="*50)
print("小米MiMo AI 聊天助手已启动")
print("输入你的问题开始聊天，输入 exit 退出程序")
print("="*50)

# 无限循环，实现一问一答
while True:
    # 获取用户输入
    user_input = input("\n")
    
    # 退出条件
    if user_input.lower() in ["exit", "quit", "退出"]:
        print("\nMiMo：再见！")
        break
    
    # 跳过空输入
    if not user_input.strip():
        continue
    
    # 调用接口，流式输出
    print("\nMiMo：", end="", flush=True)
    try:
        stream = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_completion_tokens=1024,
            temperature=1.0,
            top_p=0.95,
            stream=True,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        # 逐字打印
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
    
    except Exception as e:
        print("")
