from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

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
# 1. 定义状态（自带 messages）
# ==========================
def call_llm(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ==========================
# 2. 构建流程图
# ==========================
builder = StateGraph(MessagesState)
builder.add_node("llm", call_llm)
builder.add_edge(START, "llm")
builder.add_edge("llm", END)

# 开启记忆
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# ==========================
# 3. 运行测试（多轮对话）
# ==========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "user_1"}}

    # 第一轮
    graph.invoke({"messages": [("human", "我今年27岁")]}, config=config)

    # 第二轮（带记忆）
    result = graph.invoke({"messages": [("human", "我几岁？")]}, config=config)

    print("AI 回答：", result["messages"][-1].content)