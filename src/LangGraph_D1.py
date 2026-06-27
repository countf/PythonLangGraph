# 1. 导入需要的包
from typing import TypedDict  # 定义状态用
from langgraph.graph import StateGraph, START, END  # 画图核心


# 2. 定义【状态 State】→ 整个图共享的数据
class GraphState(TypedDict):
    # 存放用户问题 + AI 回答
    question: str
    answer: str


# 3. 定义【节点 Node】→ 一个Python函数就是一个节点
def ai_answer_node(state: GraphState):
    # 从状态里拿到用户问题
    user_question = state["question"]

    # AI 模拟回答
    ai_reply = f"我收到了你的问题：{user_question}，我是 LangGraph AI！"

    # 返回新状态 → 更新 answer
    return {"answer": ai_reply}


# ========================
# 4. 开始画图！核心四步
# ========================

# ① 创建图
workflow = StateGraph(GraphState)

# ② 添加节点
workflow.add_node("ai_node", ai_answer_node)

# ③ 连接边（流程路线）
workflow.add_edge(START, "ai_node")  # 起点 → AI节点
workflow.add_edge("ai_node", END)    # AI节点 → 结束

# ④ 编译成可运行的程序
app = workflow.compile()


# ========================
# 5. 运行！
# ========================
if __name__ == "__main__":
    # 输入你的问题
    inputs = {"question": "你好，LangGraph！"}

    # 运行图
    result = app.invoke(inputs)

    # 打印结果
    print("用户问题：", result["question"])
    print("AI 回答：", result["answer"])