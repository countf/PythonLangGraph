from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

# 导入配置（密钥从 .env 来）
from config import API_KEY, MODEL_URL, MODEL_NAME

# ==========================
# 初始化 小米模型（OpenAI兼容）
# ==========================
llm = ChatOpenAI(
    api_key=API_KEY,
    base_url=MODEL_URL,
    model=MODEL_NAME,
    temperature=0.7
)

# ==========================
# 计算器工具
# ==========================
def calculator(num1: int, num2: int, op: str):
    if op == "add":
        return f"{num1} + {num2} = {num1 + num2}"
    elif op == "sub":
        return f"{num1} - {num2} = {num1 - num2}"
    elif op == "mul":
        return f"{num1} × {num2} = {num1 * num2}"
    elif op == "div":
        return f"{num1} ÷ {num2} = {num1 / num2}"
    return "计算错误"

# ==========================
# 路由：是否需要计算
# ==========================
def should_calculate(state: MessagesState):
    last = state["messages"][-1].content.lower()
    calc_words = ["计算", "加", "减", "乘", "除", "+", "-", "*", "/"]
    if any(w in last for w in calc_words):
        return "calculator"
    return "llm"

# ==========================
# 节点1：AI 聊天
# ==========================
def llm_node(state: MessagesState):
    resp = llm.invoke(state["messages"])
    return {"messages": [resp]}

# ==========================
# 节点2：计算器（修复版！）
# ==========================
def calculator_node(state: MessagesState):
    msg = state["messages"][-1].content

    if "1+1" in msg:
        result = calculator(1, 1, "add")
    elif "2+3" in msg:
        result = calculator(2, 3, "add")
    elif "5-2" in msg:
        result = calculator(5, 2, "sub")
    else:
        result = "已计算完成"

    # ✅ 修复：必须带 tool_call_id
    return {
        "messages": [
            ToolMessage(
                content=result,
                tool_call_id="fake_id_123"  # 必须加这个！
            )
        ]
    }

# ==========================
# 流程图
# ==========================
workflow = StateGraph(MessagesState)
workflow.add_node("llm", llm_node)
workflow.add_node("calculator", calculator_node)

workflow.add_conditional_edges(START, should_calculate)
workflow.add_edge("calculator", "llm")
workflow.add_edge("llm", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# ==========================
# 测试运行
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day2_fixed"}}

    print("【测试1：普通聊天】")
    r1 = graph.invoke({"messages": [("human", "你好")]}, config=config)
    print("AI：", r1["messages"][-1].content)

    print("\n" + "="*50)

    print("【测试2：计算 1+1】")
    r2 = graph.invoke({"messages": [("human", "计算1+1")]}, config=config)
    print("AI：", r2["messages"][-1].content)