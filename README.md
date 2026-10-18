# AI 应用开发 · 起手项目

> 目标：三个小时内，让你用 Python 亲手调通一次大模型 API，看到真实的回复。
> 这个目录是你后面 RAG 项目的起点，不要新建别的目录，就在这里长。

---

## 第 0 步：先装三样东西（约 40 分钟，一次性的）

### 1. Python 3.11 或更高

打开 <https://www.python.org/downloads/> 下载 Windows 安装包。

**安装时务必勾选 `Add python.exe to PATH`**（这一步漏了后面全是坑）。

装完后打开 PowerShell，输入下面这行验证：

```powershell
python --version
```

看到 `Python 3.11.x` 或更高就成功了。

### 2. Git

打开 <https://git-scm.com/download/win>，一路默认安装。

验证：

```powershell
git --version
```

### 3. VS Code

打开 <https://code.visualstudio.com/>，装好后在扩展市场里搜 `Python`，装上微软官方那个。

---

## 第 1 步：拿到一个 API Key（约 15 分钟）

下面四个都支持同一套接口，**代码不用改，只改配置**。按你的钱包选一个：

| 平台 | base_url | 参考模型名 | 说明 |
|---|---|---|---|
| **智谱 GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | 有免费额度，学生首选 |
| **硅基流动** | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-7B-Instruct` | 注册送额度，部分模型免费 |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | 极便宜，充 10 块能用很久 |
| **阿里百炼** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | 新用户有免费额度 |

> ⚠️ 模型名和免费政策会变。注册后在控制台的「模型列表」里确认当前的名字，照抄过来即可。

注册 → 实名认证 → 在控制台创建一个 API Key → 复制出来（**只显示一次，先粘到记事本**）。

---

## 第 2 步：把项目跑起来（约 20 分钟）

在这个目录下打开 PowerShell（地址栏输入 `powershell` 回车最快），依次执行：

```powershell
# 1. 创建虚拟环境（只做一次）
python -m venv .venv

# 2. 激活虚拟环境（每次开新终端都要做）
.\.venv\Scripts\Activate.ps1

# 3. 装依赖（只做一次）
pip install -r requirements.txt
```

> 如果第 2 步报"禁止运行脚本"，执行这一行后重试：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 配置你的 Key

把 `.env.example` 复制一份改名成 `.env`，然后填进去：

```powershell
Copy-Item .env.example .env
```

用 VS Code 打开 `.env`，把你的 Key、base_url、模型名填进去。**`.env` 已被 git 忽略，不会泄露。**

### 跑第一个脚本

```powershell
python step1_hello_llm.py
```

如果屏幕上打印出模型的回复和 token 用量 —— **恭喜，你已经是一个调过大模型 API 的人了。**

接着跑流式版本：

```powershell
python step2_stream.py
```

你会看到回复像打字一样一个字一个字冒出来。这就是所有 AI 聊天产品的底层原理。

---

## 第 3 步：别停在这里

跑通之后，把这两个脚本**自己改一遍**，这是最重要的一步：

1. 改 `system` 提示词，让它扮演一个角色（比如"一个爱吐槽的编程老师"），看输出怎么变。
2. 把 `temperature` 分别设成 0 和 1.5，同一个问题问三遍，观察差别。
3. 把多轮对话加进去：让它记住你上一句说的话（提示：`messages` 列表里把历史也塞进去）。
4. 数一下：一次请求大概花多少 token？按你用的平台的价格算算是多少钱？

**做完这四件事，第 4—5 周的内容你就自学完了大半。**

---

## 常见报错

| 报错 | 原因 | 解决 |
|---|---|---|
| `python 不是内部或外部命令` | 装 Python 时没勾 PATH | 重装 Python，勾上 `Add python.exe to PATH` |
| `Activate.ps1 无法加载，因为在此系统上禁止运行脚本` | PowerShell 执行策略限制 | 见上面第 2 步的提示 |
| `AuthenticationError` / `401` | Key 填错或过期 | 检查 `.env` 里的 `LLM_API_KEY`，前后别留空格 |
| `NotFoundError` / `404` | 模型名写错 | 去平台控制台复制当前准确的模型名 |
| `ConnectionError` / 超时 | 网络问题 | 换平台试试，或检查是否需要代理 |
| 中文乱码 | 终端编码 | PowerShell 里执行 `chcp 65001` |
| `ssh: connect to host github.com port 22: Connection refused` | 22 端口被挡 | 让 SSH 走 443：`ssh.github.com:443` |
| `schannel ... CRYPT_E_NO_REVOCATION_CHECK` | 代理/加速器拦截了证书吊销检查 | 换 `http.sslBackend openssl`，或直接改走 SSH |
| `Bad owner or permissions on .ssh/config` | SSH 配置/私钥权限太宽 | `icacls "文件" /inheritance:r /grant:r "用户名:(R)"` |

**卡住了就把完整报错发我，别自己硬扛超过 30 分钟。**
## 我的学习记录

- 2026-10-18：跑通了大模型 API、流式输出、多轮对话，并完成了第一次 Git 提交。