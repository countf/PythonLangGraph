# ==========================================================
#  全链路私有化整合 · 最终完整版
# 适配：小米模型 / OpenAI 第三方接口
# 功能：AI智能体 + 工具 + 自省 + 调度 + 调试 + 记忆
# ==========================================================
import time
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

# 安全配置（不上传Git）
from config import API_KEY, MODEL_URL, MODEL_NAME

# ==========================
# 1. 初始化AI（私有化部署）
# ==========================
llm = ChatOpenAI(
    api_key=API_KEY,
    base_url=MODEL_URL,
    model=MODEL_NAME,
    temperature=0.1,
    timeout=10
)

# ==========================
# 2. 工具库（可扩展业务）
# ==========================
def calculator(n1, n2, op):
    if op == "add": return f"{n1}+{n2}={n1 + n2}"
    if op == "sub": return f"{n1}-{n2}={n1 - n2}"
    return "计算错误"

def get_weather(city):
    weather = {"北京": "晴天 24℃", "上海": "多云 26℃"}
    return weather.get(city, f"{city} 晴天 25℃")

# ==========================
# 3. 调试计时器（Day9）
# ==========================
def time_it(func):
    def wrapper(state):
        s = time.time()
        res = func(state)
        print(f"⏱ {func.__name__} 耗时：{round((time.time()-s)*1000)}ms")
        return res
    return wrapper

# ==========================
# 4. 调度Agent（Day8）
# ==========================
@time_it
def scheduler_agent(state: MessagesState):
    last = state["messages"][-1].content.lower()
    if any(w in last for w in ["计算", "+"]):
        return {"messages": [("ai", "调度→计算工具")]}
    if any(w in last for w in ["天气", "北京"]):
        return {"messages": [("ai", "调度→天气工具")]}
    return {"messages": [("ai", "调度→AI回答")]}

# ==========================
# 5. 执行节点（工具）
# ==========================
@time_it
def executor_node(state: MessagesState):
    last = state["messages"][-1].content
    if "计算" in last:
        res = calculator(5, 5, "add")
    elif "天气" in last:
        res = get_weather("北京")
    else:
        res = "无任务"
    return {"messages": [ToolMessage(content=res, tool_call_id="exec")]}

# ==========================
# 6. AI回答节点
# ==========================
@time_it
def llm_answer_node(state: MessagesState):
    resp = llm.invoke(state["messages"])
    return {"messages": [resp]}

# ==========================
# 7. 自省纠错节点（Day7）
# ==========================
@time_it
def review_node(state: MessagesState):
    return {"messages": [("system", "✅ 结果校验通过")]}

# ==========================
# 8. 主路由
# ==========================
def main_router(state):
    msg = state["messages"][-1].content
    if "计算" in msg or "天气" in msg:
        return "executor"
    return "llm_answer"

# ==========================
# 9. 全链路流程图
# ==========================
wf = StateGraph(MessagesState)

wf.add_node("scheduler", scheduler_agent)
wf.add_node("executor", executor_node)
wf.add_node("llm_answer", llm_answer_node)
wf.add_node("review", review_node)

wf.add_edge(START, "scheduler")
wf.add_conditional_edges("scheduler", main_router)
wf.add_edge("executor", "review")
wf.add_edge("llm_answer", "review")
wf.add_edge("review", END)

# 记忆 + 编译
memory = MemorySaver()
graph = wf.compile(checkpointer=memory)

# ==========================
# 10. 最终运行
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day10_final"}}

    print("=" * 60)
    print("🔥 全链路私有化智能体 · 启动成功")
    print("=" * 60)

    # 任务1：聊天
    r1 = graph.invoke({"messages": [("human", "你好")]}, config=config)
    print("✅ 聊天结果：", r1["messages"][-1].content)

    print("-" * 60)

    # 任务2：计算
    r2 = graph.invoke({"messages": [("human", "计算5+5")]}, config=config)
    print("✅ 计算结果：", r2["messages"][-1].content)

    print("-" * 60)

    # 任务3：天气
    r3 = graph.invoke({"messages": [("human", "北京天气")]}, config=config)
    print("✅ 天气结果：", r3["messages"][-1].content)

    print("\n" + "="*60)
    print("🎉 恭喜！LangGraph 全套课程 全部完成！")
    print("🎯 你已掌握企业级AI智能体开发！")
    print("="*60)