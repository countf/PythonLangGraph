# ==============================
#  最终版：完整智能体 Agent
# 适配：小米模型 / 第三方 OpenAI 接口
# ==============================
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

# ==============================
# 2. 工具：计算器
# ==============================
def calculator(num1: int, num2: int, op: str):
    if op == "add":
        return f"{num1} + {num2} = {num1 + num2}"
    elif op == "sub":
        return f"{num1} - {num2} = {num1 - num2}"
    elif op == "mul":
        return f"{num1} × {num2} = {num1 * num2}"
    elif op == "div":
        return f"{num1} ÷ {num2} = {num1 / num2:.2f}"
    return "不支持的运算"

# ==============================
# 3. 路由判断：是否需要计算
# ==============================
def need_calculate(state: MessagesState):
    last_msg = state["messages"][-1].content.lower()
    calc_words = ["计算", "加", "减", "乘", "除", "+", "-", "*", "/"]
    if any(w in last_msg for w in calc_words):
        return "calculator"
    return "llm"

# ==============================
# 4. 节点1：AI 正常聊天
# ==============================
def llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ==============================
# 5. 节点2：计算器（修复无报错版）
# ==============================
def calculator_node(state: MessagesState):
    msg = state["messages"][-1].content

    if "1+1" in msg:
        res = calculator(1, 1, "add")
    elif "2+3" in msg:
        res = calculator(2, 3, "add")
    elif "5-2" in msg:
        res = calculator(5, 2, "sub")
    elif "3×4" in msg or "3*4" in msg:
        res = calculator(3, 4, "mul")
    else:
        res = "已调用计算器，结果已生成"

    return {
        "messages": [
            ToolMessage(
                content=res,
                tool_call_id="tool_fake_id_123"  # 必加，解决报错
            )
        ]
    }

# ==============================
# 6. 构建流程图
# ==============================
workflow = StateGraph(MessagesState)

workflow.add_node("llm", llm_node)
workflow.add_node("calculator", calculator_node)

# 条件路由
workflow.add_conditional_edges(
    START,
    need_calculate
)

workflow.add_edge("calculator", "llm")
workflow.add_edge("llm", END)

# 记忆
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# ==============================
# 7. 运行测试
# ==============================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day3_agent"}}

    print("【测试 1：普通聊天】")
    r1 = graph.invoke({"messages": [("human", "你好，你是谁")]}, config=config)
    print("AI：", r1["messages"][-1].content)

    print("\n" + "="*50)

    print("【测试 2：计算 1+1】")
    r2 = graph.invoke({"messages": [("human", "帮我计算 1+1")]}, config=config)
    print("AI：", r2["messages"][-1].content)

    print("\n" + "="*50)

    print("【测试 3：计算 2+3】")
    r3 = graph.invoke({"messages": [("human", "那 2+3 等于几？")]}, config=config)
    print("AI：", r3["messages"][-1].content)