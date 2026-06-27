# ========================
# LangGraph 阶段一  最终版
# 功能：多轮对话记忆 + 状态保存 + 条件路由
# 阶段一完美收官！
# ========================

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # 记忆核心！

# ========================
# 1. 定义状态（带记忆）
# ========================
class GraphState(TypedDict):
    # 多轮聊天记录（所有对话都存在这里）
    messages: list
    # 是否需要工具
    need_tool: bool

# ========================
# 2. 节点1：AI 聊天节点（带记忆）
# ========================
def chat_node(state: GraphState):
    messages = state["messages"]
    user_msg = messages[-1]  # 取最后一条用户消息

    # 简单判断是否需要计算
    need_tool = any(key in user_msg for key in ["计算", "加", "减", "乘"])

    if need_tool:
        print(f"🧠 AI 判断：需要调用计算器")
        reply = "好的，我调用计算器帮你算"
    else:
        print(f"💬 AI 聊天：直接回答")
        reply = f"你说：{user_msg} → 我记住啦！"

    # 把回答加入历史记录
    messages.append(reply)
    return {"messages": messages, "need_tool": need_tool}

# ========================
# 3. 节点2：计算器工具节点
# ========================
def calculator_node(state: GraphState):
    messages = state["messages"]
    user_msg = messages[-2]  # 取用户问题

    if "1+1" in user_msg:
        res = "1+1=2"
    elif "2+3" in user_msg:
        res = "2+3=5"
    else:
        res = "计算器已完成计算"

    messages.append(f"🧮 工具结果：{res}")
    print(f"✅ 工具执行：{res}")
    return {"messages": messages}

# ========================
# 4. 路由判断
# ========================
def router(state: GraphState):
    return "calculator" if state["need_tool"] else END

# ========================
# 5. 构建流程图
# ========================
workflow = StateGraph(GraphState)

# 添加节点
workflow.add_node("chat", chat_node)
workflow.add_node("calculator", calculator_node)

# 连线
workflow.add_edge(START, "chat")
workflow.add_conditional_edges("chat", router)
workflow.add_edge("calculator", END)

# ========================
# 6. 开启记忆功能（Day3 核心）
# ========================
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)  # 记忆挂载！

# ========================
# 7. 运行：多轮对话
# ========================
if __name__ == "__main__":
    # 会话ID → 同一个ID共享记忆
    config = {"configurable": {"thread_id": "user_123"}}

    # 第一轮对话
    print("="*50)
    app.invoke({"messages": ["你好"], "need_tool": False}, config=config)

    # 第二轮对话（带记忆）
    print("="*50)
    app.invoke({"messages": ["帮我计算1+1"], "need_tool": False}, config=config)

    # 查看全部记忆
    print("\n📜 全部聊天记录：")
    final_state = app.get_state(config).values
    for idx, msg in enumerate(final_state["messages"]):
        print(f"{idx+1}. {msg}")