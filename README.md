# LangGraph 小米MiMo大模型智能体全套学习项目

# \[README\.md\]\(README\.md\) \- LangGraph 小米 MiMo 大模型智能体全套学习项目

## 项目简介

本仓库是一套**从零到完整企业级 AI 智能体**的 LangGraph 学习代码，基于小米 MiMo（mimo\-v2\.5\-pro）大模型开发，兼容所有 OpenAI 格式第三方 LLM 接口。
代码按 Day1\~Day13 循序渐进，覆盖基础图结构、条件路由、多轮对话记忆、工具调用、多工具智能体、自省纠错、多 Agent 调度、性能调试全流程，适合 AI Agent 入门学习。

## 技术栈

- Python \>= 3\.9

- LangGraph：构建 Agent 状态流程图

- LangChain OpenAI：兼容小米 MiMo / 各类大模型 API

- python\-dotenv：环境变量密钥管理（防止 API 密钥泄露）

- OpenAI SDK：模型基础调用

## 仓库文件说明

### 一、LangGraph 阶段学习代码（LangGraph\_D1 \~ D13）

1. `LangGraph_D1.py`：LangGraph 最简入门，基础 State 状态、单节点流程图搭建

2. `LangGraph_D2.py`：条件路由基础，AI 自动判断是否调用计算器工具

3. `LangGraph_D3.py`：多轮对话记忆功能，会话状态持久化

4. `LangGraph_D4.py`：MessagesState 内置消息状态，基础大模型对话

5. `LangGraph_D5.py`：修复 ToolMessage 报错，规范工具调用格式

6. `LangGraph_D6.py`：单工具完整智能体（计算器），标准化执行流程

7. `LangGraph_D7.py`：稳定无报错基础 Agent 模板，超时、温度参数优化

8. `LangGraph_D8.py`：双工具智能体：计算器 \+ 天气查询，自动路由分发

9. `LangGraph_D9.py`：课程最终大作业，完整可用生产级 Agent

10. `LangGraph_D10.py`：自省校验 Agent，AI 自动检查计算结果对错并重算

11. `LangGraph_D11.py`：多 Agent 协作架构：调度 Agent \+ 执行 Agent \+ 复盘 Agent

12. `LangGraph_D12.py`：Agent 性能调试工具，统计每个节点运行耗时

13. `LangGraph_D13.py`：全链路整合终极版，集合工具、记忆、自省、调度、调试

### 二、小米 MiMo 模型原生调用脚本

1. `xiaomi.py`：极简单轮模型调用示例

2. `xiaomi2.py`：带系统提示词、自定义参数基础调用

3. `xiaomi_LLM.py`：流式输出交互式聊天终端，支持 exit 退出

### 三、配置规范说明

所有 LLM 密钥、接口地址统一抽离至`config.py`或`.env`文件，**禁止硬编码密钥上传 GitHub**，保护 API 凭证安全。

## 功能总览

✅ 基础 LangGraph 图编程：State、Node、START/END、Edge、条件路由
✅ 会话记忆：MemorySaver 多轮上下文保存，thread\_id 区分独立用户
✅ 工具调用：计算器（加减乘除）、城市天气查询双工具自动选择
✅ 结果自省校验：AI 自动复核输出，错误自动重新计算
✅ 多 Agent 分工：任务调度、工具执行、结果复盘三层架构
✅ 性能监控：节点运行耗时打印，方便调试优化
✅ 流式对话：实时逐字输出大模型返回内容
✅ 兼容小米 MiMo、OpenAI、通义千问等所有 OpenAI 兼容接口

## 环境部署步骤

### 1\. 安装依赖库

```bash
pip install langgraph langchain langchain-openai openai python-dotenv
```

### 2\. 密钥配置（两种方式任选其一）

#### 方式 1：\.env 文件（推荐，所有 xiaomi 系列脚本使用）

项目根目录新建 `.env` 文件

```env
LLM_API_KEY=你的小米MiMo API密钥
MODEL_URL=https://your-model-api-endpoint
```

#### 方式 2：\[config\.py\]\(config\.py\) 文件（LangGraph 系列代码统一导入）

新建 `config.py`

```python
API_KEY = "你的模型API密钥"
MODEL_URL = "模型接口地址"
MODEL_NAME = "mimo-v2.5-pro"
```

### 3\. 运行代码

直接执行任意 `.py` 文件即可测试：

```bash
# 入门示例
python LangGraph_D1.py

# 完整双工具智能体
python LangGraph_D9.py

# 交互式流式聊天
python xiaomi_LLM.py
```

## 入门代码详解（LangGraph\\\[\_D1\.py\]\(\_D1\.py\)）

### 核心逻辑

1. **定义状态 GraphState**
使用`TypedDict`定义全局共享数据，存储用户问题与 AI 回答，是整个流程图的数据载体。

```python
class GraphState(TypedDict):
    question: str
    answer: str
```

2. **定义节点 Node**
每个函数代表一个执行节点，接收全局状态，处理后返回更新后的状态。

```python
def ai_answer_node(state: GraphState):
    user_question = state["question"]
    ai_reply = f"我收到了你的问题：{user_question}，我是 LangGraph AI！"
    return {"answer": ai_reply}
```

3. **构建流程图四步标准流程**

```python
# 1. 创建图容器
workflow = StateGraph(GraphState)
# 2. 注册节点
workflow.add_node("ai_node", ai_answer_node)
# 3. 连接流程边
workflow.add_edge(START, "ai_node")
workflow.add_edge("ai_node", END)
# 4. 编译为可运行应用
app = workflow.compile()
```

4. **调用执行**
使用`app.invoke()`传入初始状态，获取运行结果：

```python
inputs = {"question": "你好，LangGraph！"}
result = app.invoke(inputs)
print("AI 回答：", result["answer"])
```

### 运行输出示例

```Plain Text
用户问题： 你好，LangGraph！
AI 回答： 我收到了你的问题：你好，LangGraph！，我是 LangGraph AI！
```

## 安全注意事项

1. 严禁将包含真实 API Key 的`config.py`、`.env`提交到 GitHub；

2. 推送仓库前建议添加`.gitignore`，忽略密钥配置文件：

```gitignore
# .gitignore
config.py
.env
__pycache__/
*.pyc
```

3. 密钥建议设置短期有效期，降低泄露风险。

## 学习路线建议

1. 先运行 `LangGraph_D1.py` 理解图、状态、节点基础概念

2. 依次学习 D2\~D3 掌握路由与记忆

3. D4\~D9 学习工具调用完整智能体

4. D10 自省、D11 多 Agent、D12 调试、D13 综合项目作为进阶内容

5. `xiaomi_*.py` 单独学习原生大模型接口调用逻辑

## 开源协议

MIT License，可自由学习、修改、商用，保留项目来源说明。


