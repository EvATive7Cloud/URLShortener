## 运行与开发

### 安装依赖（使用 uv）

```bash
uv sync
```

### 启动开发服务器

```bash
python main.py -p 11000
```

## 接口说明

### `POST /shorten`

- 请求体（JSON）：

```json
{
  "url": "https://example.com/very/long/url"
}
```

- 响应（JSON）：

```json
{
  "original_url": "https://example.com/very/long/url",
  "short_url": "Ab12Cd34Ef"
}
```

- 短链特点：
  - 长度固定 10 位
  - 由数字 + 大小写字母随机组成
  - 同一个原始 URL 多次请求会返回同一个短链

### `GET /{short_url}`

- 访问时会 302 重定向到对应的原始 URL。

## 打包为单文件 EXE

1. 确保已安装 PyInstaller：

   ```bash
   uv add pyinstaller
   ```

2. 在项目根目录执行：

   ```bash
   uv run python build_exe.py
   ```

3. 生成的可执行文件位于 `dist/urlshortener.exe`。
   运行后默认监听 `0.0.0.0:11000`，浏览器访问 `http://127.0.0.1:11000` 即可使用。
