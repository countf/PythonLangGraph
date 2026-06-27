# ==============================================
# 多Agent协作架构
# 角色：调度Agent + 执行Agent + 复盘Agent
# 功能：任务分发 → 执行计算 → 校验结果
# ==============================================
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

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
# 工具（计算器）
# ==========================
def calculator(n1, n2, op):
    if op == "add": return f"{n1} + {n2} = {n1 + n2}"
    if op == "sub": return f"{n1} - {n2} = {n1 - n2}"
    return "计算错误"

# ==========================
# 【Agent1：调度Agent】→ 分配任务
# ==========================
def scheduler_agent(state: MessagesState):
    last = state["messages"][-1].content
    if any(k in last for k in ["计算", "+", "-", "×", "÷"]):
        return {"messages": [("ai", "调度：交给执行Agent处理")]}
    return {"messages": [("ai", "调度：交给普通回答处理")]}

# ==========================
# 【Agent2：执行Agent】→ 干活
# ==========================
def executor_agent(state: MessagesState):
    last = state["messages"][-1].content
    if "5+5" in last:
        res = calculator(5, 5, "add")
    elif "9+1" in last:
        res = calculator(9, 1, "add")
    else:
        res = "执行完成：无计算"
    return {"messages": [ToolMessage(content=res, tool_call_id="exec_1")]}

# ==========================
# 【Agent3：复盘Agent】→ 校验结果
# ==========================
def reviewer_agent(state: MessagesState):
    res = llm.invoke([
        ("system", "你是复盘专家，只返回：正确 / 错误，不要多余字"),
    ] + state["messages"])
    return {"messages": [("ai", f"复盘结果：{res.content}")]}

# ==========================
# 路由：多Agent调度
# ==========================
def router(state: MessagesState):
    last = state["messages"][-1].content
    if "调度：交给执行Agent" in last:
        return "executor"
    return "reviewer"

# ==========================
# 多Agent流程图
# ==========================
wf = StateGraph(MessagesState)

wf.add_node("scheduler", scheduler_agent)
wf.add_node("executor", executor_agent)
wf.add_node("reviewer", reviewer_agent)

wf.add_edge(START, "scheduler")
wf.add_conditional_edges("scheduler", router)
wf.add_edge("executor", "reviewer")
wf.add_edge("reviewer", END)

memory = MemorySaver()
graph = wf.compile(checkpointer=memory)

# ==========================
# 运行多Agent系统
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day8_multi_agent"}}

    print("【多Agent协作：计算 5+5】")
    result = graph.invoke({
        "messages": [("human", "帮我计算 5+5")]
    }, config=config)

    print("\n=== 执行流程 ===")
    for i, msg in enumerate(result["messages"]):
        print(f"{i+1}. {msg.content}")