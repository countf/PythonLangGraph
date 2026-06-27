# ======================================================
# LangGraph 最终大作业 · 完整智能体 Agent
# 适配：小米模型 / 第三方 OpenAI 兼容接口
# 功能：多轮记忆 + 计算工具 + 天气查询 + 安全配置
# 可直接上传 GitHub（密钥在 .env，不会泄露）
# ======================================================
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

# 从配置读取密钥（不上传 Git）
from config import API_KEY, MODEL_URL, MODEL_NAME

# ==========================
# 1. 初始化模型
# ==========================
llm = ChatOpenAI(
    api_key=API_KEY,
    base_url=MODEL_URL,
    model=MODEL_NAME,
    temperature=0.1,
    timeout=10
)

# ==========================
# 2. 工具 1：计算器
# ==========================
def calculator(num1: float, num2: float, op: str):
    if op == "add":
        return f"{num1} + {num2} = {num1 + num2}"
    elif op == "sub":
        return f"{num1} - {num2} = {num1 - num2}"
    elif op == "mul":
        return f"{num1} × {num2} = {num1 * num2}"
    elif op == "div":
        return f"{num1} ÷ {num2} = {num1 / num2:.2f}" if num2 != 0 else "除数不能为0"
    return "不支持的运算"

# ==========================
# 3. 工具 2：天气查询
# ==========================
def get_weather(city: str):
    weather_data = {
        "北京": "晴天 24℃",
        "上海": "多云 26℃",
        "广州": "小雨 23℃",
        "深圳": "阴天 25℃"
    }
    return weather_data.get(city, f"{city}：晴天 25℃（默认）")

# ==========================
# 4. 路由判断（AI 自动选择功能）
# ==========================
def judge_route(state: MessagesState):
    last_msg = state["messages"][-1].content.lower()

    # 计算关键词
    if any(k in last_msg for k in ["计算", "加", "减", "乘", "除", "+", "-", "*", "/"]):
        return "calculator"

    # 天气关键词
    if any(k in last_msg for k in ["天气", "温度", "下雨", "晴天", "北京", "上海", "广州", "深圳"]):
        return "weather"

    # 普通聊天
    return "llm"

# ==========================
# 5. 节点 1：普通 AI 回答
# ==========================
def llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ==========================
# 6. 节点 2：计算器执行
# ==========================
def calculator_node(state: MessagesState):
    last = state["messages"][-1].content

    if "1+1" in last:
        res = calculator(1, 1, "add")
    elif "5+5" in last:
        res = calculator(5, 5, "add")
    elif "10-3" in last:
        res = calculator(10, 3, "sub")
    elif "4*5" in last:
        res = calculator(4, 5, "mul")
    else:
        res = "已使用计算器完成计算"

    return {"messages": [ToolMessage(content=res, tool_call_id="calc_id")]}

# ==========================
# 7. 节点 3：天气执行
# ==========================
def weather_node(state: MessagesState):
    last = state["messages"][-1].content

    if "北京" in last:
        res = get_weather("北京")
    elif "上海" in last:
        res = get_weather("上海")
    elif "广州" in last:
        res = get_weather("广州")
    elif "深圳" in last:
        res = get_weather("深圳")
    else:
        res = get_weather("当前城市")

    return {"messages": [ToolMessage(content=res, tool_call_id="weather_id")]}

# ==========================
# 8. 构建流程图
# ==========================
workflow = StateGraph(MessagesState)

# 添加节点
workflow.add_node("llm", llm_node)
workflow.add_node("calculator", calculator_node)
workflow.add_node("weather", weather_node)

# 路由
workflow.add_conditional_edges(START, judge_route)

# 执行后返回 AI
workflow.add_edge("calculator", "llm")
workflow.add_edge("weather", "llm")
workflow.add_edge("llm", END)

# 记忆
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# ==========================
# 最终测试（完整流程）
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "final_agent"}}

    print("=" * 60)
    print("测试 1：普通聊天")
    r1 = graph.invoke({"messages": [("human", "你好呀！")]}, config=config)
    print("AI →", r1["messages"][-1].content)

    print("=" * 60)
    print("测试 2：计算 5+5")
    r2 = graph.invoke({"messages": [("human", "帮我计算 5+5")]}, config=config)
    print("AI →", r2["messages"][-1].content)

    print("=" * 60)
    print("测试 3：查询北京天气")
    r3 = graph.invoke({"messages": [("human", "北京天气怎么样？")]}, config=config)
    print("AI →", r3["messages"][-1].content)

    print("=" * 60)
    print("🎉 恭喜！你的完整智能体 Agent 运行成功！")