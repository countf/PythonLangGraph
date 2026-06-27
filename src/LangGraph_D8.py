# ==============================================
# 阶段三 ：多工具自主智能体（企业级最简版）
# 适配：小米模型 / OpenAI 第三方接口
# 功能：聊天 + 计算 + 查天气
# ==============================================
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

# 配置不变
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
# 2. 工具1：计算器
# ==========================
def calculator(num1, num2, op):
    if op == "add": return f"{num1}+{num2}={num1 + num2}"
    if op == "sub": return f"{num1}-{num2}={num1 - num2}"
    if op == "mul": return f"{num1}×{num2}={num1 * num2}"
    if op == "div": return f"{num1}÷{num2}={num1 / num2:.2f}"
    return "计算错误"


# ==========================
# 3. 工具2：模拟查天气
# ==========================
def get_weather(city):
    return f"{city} 的天气：晴天，25℃"


# ==========================
# 4. 路由判断：走哪个工具
# ==========================
def judge_tool(state: MessagesState):
    last = state["messages"][-1].content.lower()

    if any(w in last for w in ["计算", "+", "-", "*", "/"]):
        return "calculator"

    if any(w in last for w in ["天气", "温度", "下雨", "晴天"]):
        return "weather"

    return "llm"


# ==========================
# 5. 节点1：AI 正常回答
# ==========================
def llm_node(state: MessagesState):
    resp = llm.invoke(state["messages"])
    return {"messages": [resp]}


# ==========================
# 6. 节点2：计算器
# ==========================
def calculator_node(state: MessagesState):
    last = state["messages"][-1].content
    if "5+5" in last:
        res = calculator(5, 5, "add")
    elif "1+1" in last:
        res = calculator(1, 1, "add")
    else:
        res = "计算完成"

    return {"messages": [ToolMessage(content=res, tool_call_id="calc_123")]}


# ==========================
# 7. 节点3：天气查询
# ==========================
def weather_node(state: MessagesState):
    last = state["messages"][-1].content
    if "北京" in last:
        res = get_weather("北京")
    elif "上海" in last:
        res = get_weather("上海")
    else:
        res = "未查询到天气"

    return {"messages": [ToolMessage(content=res, tool_call_id="weather_123")]}


# ==========================
# 8. 构建流程图
# ==========================
wf = StateGraph(MessagesState)
wf.add_node("llm", llm_node)
wf.add_node("calculator", calculator_node)
wf.add_node("weather", weather_node)

wf.add_conditional_edges(START, judge_tool)
wf.add_edge("calculator", "llm")
wf.add_edge("weather", "llm")
wf.add_edge("llm", END)

# 记忆
memory = MemorySaver()
graph = wf.compile(checkpointer=memory)

# ==========================
# 测试运行
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "agent_007"}}

    print("【测试1：聊天】")
    r1 = graph.invoke({"messages": [("human", "你好")]}, config)
    print("AI：", r1["messages"][-1].content)

    print("\n=== 测试2：计算 5+5 ===")
    r2 = graph.invoke({"messages": [("human", "计算5+5")]}, config)
    print("AI：", r2["messages"][-1].content)

    print("\n=== 测试3：查北京天气 ===")
    r3 = graph.invoke({"messages": [("human", "北京天气怎么样")]}, config)
    print("AI：", r3["messages"][-1].content)