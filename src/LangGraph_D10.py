from langgraph.graph import StateGraph,START,END,MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

from config import API_KEY, MODEL_URL, MODEL_NAME

llm=ChatOpenAI(api_key=API_KEY,base_url=MODEL_URL,model=MODEL_NAME,temperature=0.1,timeout=10)

# 工具：计算器
def calc(n1,n2,opt):
    if opt=="add":return f"{n1}+{n2}={n1+n2}"
    return "运算异常"

# 业务节点
def tool_node(state:MessagesState):
    msg=state["messages"][-1].content
    res=calc(9,1,"add") if "9+1" in msg else "无计算"
    return {"messages":[ToolMessage(content=res,tool_call_id="t1")]}

# 回答节点
def answer_node(state:MessagesState):
    res=llm.invoke(state["messages"])
    print(res.content)
    return {"messages":[res]}

# 自省校验节点【核心】
def review_node(state:MessagesState):
    prompt="检查上一轮答案是否正确，错误返回'wrong'，正确返回'ok'，只输出单个单词"
    check=llm.invoke([("system",prompt)]+state["messages"])
    return {"messages":[check]}

# 自省路由：错→重算，对→结束
def review_route(state:MessagesState):
    last=state["messages"][-1].content.strip()
    if last=="wrong":
        return "tool"
    return END

# 构图
wf=StateGraph(MessagesState)
wf.add_node("tool",tool_node)
wf.add_node("answer",answer_node)
wf.add_node("review",review_node)

wf.add_edge(START,"tool")
wf.add_edge("tool","answer")
wf.add_edge("answer","review")
wf.add_conditional_edges("review",review_route)

mem=MemorySaver()
app=wf.compile(checkpointer=mem)

if __name__=="__main__":
    cfg={"configurable":{"thread_id":"day7"}}
    out=app.invoke({"messages":[("human","9加1等于多少")]},config=cfg)
    print("最终结果：",out["messages"][-1].content)