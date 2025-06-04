# 代码注释翻译工具

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

~~基于硅基流动(SiliconFlow) API~~ 兼容一切使用openai式输出的模型平台的代码注释翻译工具，自动将代码中的英文注释转换为中文，并插入到原注释下方。

该工具会读取目标目录下所有文件的所有注释，交由ai翻译后写回文件

## 功能特点

- 支持 Python/C/C++/Java/JavaScript/TypeScript 文件
- 多进程并发处理（建议不超过90进程，在本人设备实测，超过90并发会导致连接被拒绝）
- 自动跳过已翻译文件
- 保留原始代码格式
- 自动管理虚拟环境和依赖

## 快速开始

```bash
# 克隆项目
git clone https://github.com/JianFeeeee/Transcomment.git
cd Transcomment

# 首次运行会自动设置环境
./run.sh [目标文件或目录]
```

Windows 用户：

```cmd
.\run.bat [目标文件或目录]
```

如果您喜欢，也可以将run.bat(windows中)run.sh(linux中)重命名为您喜欢的名称后，将本项目添加至环境变量，方便您随时调用。

## 配置说明

编辑 `config/config.ini` 文件：



```ini
[API]
apikey = 您使用的平台的API密钥
apiurl = 您使用平台的url
[MAXPROCESS]
max = 90  # 建议值：30-90，根据网络情况调整
```

编辑`config/models.json`文件

```
["THUDM/GLM-4-9B-0414", "Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-Coder-7B-Instruct"]
在列表中添加您想使用的模型，删除您不需要的模型
```

## 注意事项

1. 需要保持网络连接以调用 API
2. 高并发可能会增加 API 调用频率
3. 首次运行会自动安装所需依赖
4. 首次运行会自动创建虚拟环境

## 关于拓展

如果您喜欢本项目，可以给本项目点个star，如果您想要添加多语言的支持，可以自行fork。若想要实现任意语言到任意语言的注释翻译，仅需修改

 `src/translate_comments.py`

```
def ai_tr(message, module, i=0):
    try:
        response = client.chat.completions.create(  
            model=module[i],  
            messages=[  
                {"role": "system", "content": "你是一个翻译家，你要为接下来的所有输入给出对应的中文翻译，注意保留原有的符号，注意不要给出解释只给出翻译即可"},  
                {"role": "user", "content": message}  
            ],  
            temperature=0.7,  
            max_tokens=4096
        )
        print(f"Token usage: {response.usage.total_tokens}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in translation: {str(e)}")
        if i < len(module) - 1:
            print(f"Trying next model: {module[i+1]}")
            return ai_tr(message, module, i+1)
        else:
            print("All models busy, waiting 10 seconds before retrying")
            time.sleep(10)
            return ai_tr(message, module, 0)


```

中的提示词即可。

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
