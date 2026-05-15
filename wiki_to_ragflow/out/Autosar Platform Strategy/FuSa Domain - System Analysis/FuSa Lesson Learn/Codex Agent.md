# Codex Agent

> Source: /spaces/CARSFW/pages/7018374934/Codex+Agent
> Last modified: 2026-04-13T09:10:53.000+02:00

---

codex 是OpenAI 出的开源的可以嵌入到vscode中的ai agent， 可以帮助补充代码，支持skills等等，可以一段时间免费有一些token。 windows下的使用 WSL2 中的使用

### codex 是OpenAI 出的开源的可以嵌入到vscode中的ai agent， 可以帮助补充代码，支持skills等等，可以一段时间免费有一些token。

##### windows下的使用

1 . 在vscode中安装 continue 和 codex 插件。

![](../../../_images/Codex%20Agent/image-2026-4-9_16-43-20.png)

2. 由于codex默认用的是 chatgpt， 需要登陆chatgpt账号。  可以自己注册一个账号就可以使用。

打开后会出现登陆的界面，登陆对应账号。

![](../../../_images/Codex%20Agent/image-2026-4-9_16-56-43.png)

3. 如果不想用默认的模型， 可以自己在本地用ollama部署 模型， 后端模型改成ollama部署的模型 。 部署方法。

可以下载开源的ollama 软件，配置下载的模型。

然后下载 qwen2.5-coder 大模型， https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/tree/main

配合codex 或者continue 来使用。

但目前使用下来 qwen2.5-coder 返回的json格式 codex没识别， 没能进一步自动操作本地code。

##### WSL2 中的使用

1. 除了在windows上安装的continue 和 codex， 再安装remote  explorer.
2. 通过remote explorer 登陆到 WSL TARGETS中的工程文件夹。
