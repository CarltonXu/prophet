# ENCRYPTION_KEY 设置指南

## 概述

`ENCRYPTION_KEY` 用于加密存储在数据库中的敏感信息（如平台密码、主机凭证等）。为了确保服务重启后能够正确解密已加密的数据，必须设置一个固定的加密密钥。

## 为什么需要设置 ENCRYPTION_KEY？

- **服务重启后密码丢失问题**：如果不设置 `ENCRYPTION_KEY`，每次服务重启都会生成新的随机密钥，导致无法解密之前加密的密码
- **数据一致性**：使用固定的密钥可以确保加密/解密的一致性
- **生产环境要求**：生产环境必须设置固定的密钥

## 生成加密密钥

### 方法 1：使用工具脚本（推荐）

```bash
python3 tools/generate_encryption_key.py
```

脚本会生成一个密钥并显示设置方法。

### 方法 2：使用 Python 命令

```bash
python3 -c "from cryptography.fernet import Fernet; import base64; key = Fernet.generate_key(); print(base64.urlsafe_b64encode(key).decode())"
```

## 设置 ENCRYPTION_KEY

### 方法 1：环境变量（临时，当前会话有效）

**Linux/macOS:**

```bash
export ENCRYPTION_KEY='your-generated-key-here'
```

**Windows CMD:**

```cmd
set ENCRYPTION_KEY=your-generated-key-here
```

**Windows PowerShell:**

```powershell
$env:ENCRYPTION_KEY='your-generated-key-here'
```

### 方法 2：.env 文件（推荐用于开发环境）

在项目根目录创建 `.env` 文件：

```bash
ENCRYPTION_KEY=your-generated-key-here
```

然后在启动应用前加载环境变量（如果使用 python-dotenv）：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 方法 3：系统环境变量（永久设置）

**Linux/macOS:**

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
export ENCRYPTION_KEY='your-generated-key-here'
```

然后重新加载配置：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

**Windows:**

1. 右键"此电脑" -> "属性"
2. "高级系统设置" -> "环境变量"
3. 在"用户变量"或"系统变量"中添加：
   - 变量名：`ENCRYPTION_KEY`
   - 变量值：`your-generated-key-here`

### 方法 4：systemd 服务（推荐用于生产环境）

编辑 systemd 服务文件 `/etc/systemd/system/prophet.service`：

```ini
[Unit]
Description=Prophet Web Application
After=network.target

[Service]
Type=simple
User=prophet
WorkingDirectory=/path/to/prophet
Environment='ENCRYPTION_KEY=your-generated-key-here'
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

然后重新加载并重启服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart prophet
```

### 方法 5：Docker 环境变量

**docker run:**

```bash
docker run -e ENCRYPTION_KEY='your-generated-key-here' ...
```

**docker-compose.yml:**

```yaml
services:
  prophet:
    environment:
      - ENCRYPTION_KEY=your-generated-key-here
```

## 验证设置

启动应用后，检查日志文件，应该看到：

```
INFO utils.encryption: Encryption initialized successfully
```

如果看到警告：

```
WARNING utils.encryption: ENCRYPTION_KEY not set, using generated key (not suitable for production)
```

说明环境变量没有正确设置。

## 获取当前使用的密钥

如果服务已经运行并自动生成了密钥，可以从应用配置中获取：

```python
from app import create_app
app = create_app()
print(app.config.get('ENCRYPTION_KEY'))
```

**注意**：这个密钥只在当前会话中有效，服务重启后会丢失。建议立即设置环境变量。

## 迁移现有数据

如果之前没有设置 `ENCRYPTION_KEY`，服务已经自动生成了密钥并加密了一些数据：

1. **获取当前密钥**（见上一节）
2. **设置环境变量**为获取到的密钥
3. **重启服务**，现在应该可以正常解密了

如果无法获取之前的密钥，需要：

1. 重新设置所有平台的密码
2. 重新设置所有主机的凭证

## 安全建议

1. **不要将密钥提交到版本控制系统**

   - 将 `.env` 添加到 `.gitignore`
   - 不要在代码中硬编码密钥

2. **使用密钥管理服务**（生产环境）

   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - 等

3. **定期轮换密钥**（需要重新加密所有数据）

   - 导出所有加密数据
   - 生成新密钥
   - 使用新密钥重新加密数据
   - 更新环境变量

4. **备份密钥**
   - 安全地备份密钥（加密存储）
   - 确保密钥丢失时可以恢复

## 故障排查

### 问题：服务重启后无法解密密码

**原因**：`ENCRYPTION_KEY` 未设置或已更改

**解决**：

1. 检查环境变量是否正确设置：`echo $ENCRYPTION_KEY`
2. 确保使用与加密时相同的密钥
3. 如果密钥丢失，需要重新设置所有密码

### 问题：看到 "Failed to decode ENCRYPTION_KEY" 错误

**原因**：密钥格式不正确

**解决**：

1. 确保密钥是 base64 编码的字符串
2. 重新生成密钥并设置
3. 注意：更改密钥会导致无法解密现有数据

### 问题：生产环境要求 ENCRYPTION_KEY

**原因**：生产配置要求必须设置密钥

**解决**：

1. 按照上述方法设置环境变量
2. 确保在服务启动前设置
3. 验证日志中显示 "Encryption initialized successfully"

## 相关文件

- `config.py`: 配置定义
- `utils/encryption.py`: 加密工具实现
- `tools/generate_encryption_key.py`: 密钥生成工具
