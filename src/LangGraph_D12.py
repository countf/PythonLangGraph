# ==============================================
#  Agent可观测性调试
# 功能：打印思维链路 + 统计节点耗时 + 调试定位
# ==============================================
import time
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

# 计算器
def calculator(n1, n2, op):
    if op == "add":
        return f"{n1} + {n2} = {n1 + n2}"
    return "计算错误"

# ------------------------------
# 🔍 调试：节点耗时统计
# ------------------------------
def time_it(func):
    def wrapper(state):
        start = time.time()
        result = func(state)
        cost = round((time.time() - start) * 1000, 2)
        print(f"⏱ 【{func.__name__}】耗时：{cost} ms")
        return result
    return wrapper

# ------------------------------
# 🌱 节点1：AI回答
# ------------------------------
@time_it
def llm_node(state: MessagesState):
    print("🧠 思考：开始回答用户问题")
    resp = llm.invoke(state["messages"])
    return {"messages": [resp]}

# ------------------------------
# 🛠 节点2：工具执行
# ------------------------------
@time_it
def calc_node(state: MessagesState):
    print("⚙️ 执行：调用计算器")
    last = state["messages"][-1].content
    res = calculator(5,5,"add") if "5+5" in last else "计算完成"
    return {"messages": [ToolMessage(content=res, tool_call_id="t9")]}

# ------------------------------
# 🧐 节点3：自检
# ------------------------------
@time_it
def check_node(state: MessagesState):
    print("🔍 校验：检查结果是否正确")
    return {"messages": [("system", "结果正确")]}

# ------------------------------
# 🚦 路由
# ------------------------------
def router(state):
    last = state["messages"][-1].content.lower()
    if any(k in last for k in ["计算","+","-","*","/"]):
        return "calc_node"
    return "llm_node"

# ------------------------------
# 流程图
# ------------------------------
wf = StateGraph(MessagesState)
wf.add_node("llm_node", llm_node)
wf.add_node("calc_node", calc_node)
wf.add_node("check_node", check_node)

wf.add_conditional_edges(START, router)
wf.add_edge("calc_node", "check_node")
wf.add_edge("llm_node", "check_node")
wf.add_edge("check_node", END)

memory = MemorySaver()
graph = wf.compile(checkpointer=memory)

# ------------------------------
# 运行调试
# ------------------------------
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day9_debug"}}

    print("="*60)
    print("【调试模式启动】")
    result = graph.invoke({
        "messages": [("human", "计算 5+5")]
    }, config=config)

    print("\n✅ 最终结果：", result["messages"][-1].content)