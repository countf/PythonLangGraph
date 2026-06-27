# ========================
# LangGraph 阶段一
# 功能：AI 判断 → 要不要调用工具 → 循环执行
# 核心：条件路由 + 工具节点
# ========================

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ========================
# 1. 定义状态（全局共享数据）
# ========================
class GraphState(TypedDict):
    question: str       # 用户问题
    answer: str        # AI 最终回答
    need_tool: bool    # 是否需要调用工具（True/False）


# ========================
# 2. 节点1：AI 判断问题（要不要调用工具）
# ========================
def ai_judge_node(state: GraphState):
    question = state["question"]

    # AI 判断规则：
    # 问题里有 "计算" → 需要工具
    # 其他问题 → 不需要工具
    if "计算" in question or "加" in question or "减" in question:
        need_tool = True
        print("【AI 判断】：需要调用计算器工具")
    else:
        need_tool = False
        print("【AI 判断】：不需要工具，直接回答")

    return {"need_tool": need_tool}


# ========================
# 3. 节点2：工具节点（计算器）
# ========================
def calculator_node(state: GraphState):
    question = state["question"]

    # 简单模拟计算
    if "1+1" in question:
        result = "1+1=2"
    elif "2+3" in question:
        result = "2+3=5"
    else:
        result = "已使用计算器完成计算"

    print(f"【工具执行】：{result}")
    return {"answer": result}


# ========================
# 4. 节点3：普通回答节点
# ========================
def normal_answer_node(state: GraphState):
    answer = f"普通回答：{state['question']} → 这是AI直接回答"
    print(f"【普通回答】：{answer}")
    return {"answer": answer}


# ========================
# 5. 条件路由（Day2 核心！）
# 根据 need_tool 决定走哪条路
# ========================
def judge_router(state: GraphState):
    if state["need_tool"]:
        return "calculator"       # 去计算器
    else:
        return "normal_answer"    # 去普通回答


# ========================
# 6. 画图流程
# ========================
workflow = StateGraph(GraphState)

# 添加节点
workflow.add_node("ai_judge", ai_judge_node)
workflow.add_node("calculator", calculator_node)
workflow.add_node("normal_answer", normal_answer_node)

# 连线
workflow.add_edge(START, "ai_judge")

# 路由（不是固定连线，是动态判断）
workflow.add_conditional_edges(
    "ai_judge",
    judge_router
)

# 结束
workflow.add_edge("calculator", END)
workflow.add_edge("normal_answer", END)

# 编译
app = workflow.compile()


# ========================
# 7. 运行测试
# ========================
if __name__ == "__main__":
    # 测试1：需要工具
    inputs = {"question": "帮我计算 1+1 等于几"}

    # 测试2：不需要工具
    # inputs = {"question": "你好呀"}

    result = app.invoke(inputs)
    print("\n最终结果：", result["answer"])