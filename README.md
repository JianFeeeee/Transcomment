# 代码注释翻译工具

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

基于硅基流动(SiliconFlow) API 的代码注释翻译工具，自动将代码中的英文注释转换为中文。

## 功能特点

- 支持 Python/C/C++/Java 文件
- 多进程并发处理（建议不超过90进程）
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
run.bat [目标文件或目录]
```

## 配置说明

编辑 `config/config.ini` 文件：

```ini
[APIKEY]
apikey = 您的硅基流动API密钥

[MAXPROCESS]
max = 90  # 建议值：30-90，根据网络情况调整
```

## 注意事项

1. 需要保持网络连接以调用 API
2. 高并发可能会增加 API 调用频率
3. 首次运行会自动安装所需依赖

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
