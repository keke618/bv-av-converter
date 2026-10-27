<div align="center">

# BV / AV 转换器

**哔哩哔哩视频编号双向转换工具** · 支持 2026 新版编号

### [⬇ 下载 Windows 版](../../releases/latest)

<sub>单文件免安装 · 8.5 MB · 无需 Python 环境</sub>

<sub>[源代码](bv_aid_v2.py) · [MIT 协议](LICENSE) · [更新日志](../../releases)</sub>

</div>

---

## 功能特性

| 功能 | 说明 |
| :--- | :--- |
| **双向转换** | BV 号 ⇄ av 号，两个方向都支持 |
| **自动识别** | 输入 BV 号就转 av 号，输入 av 号就转 BV 号 |
| **链接直贴** | 可直接粘贴 `https://www.bilibili.com/video/BV1xx.../` |
| **边输边转** | 输入变化后自动出结果，也可按回车 |
| **一键复制** | 点击结果框全选，或按「复制结果」 |
| **新旧兼容** | 47 位新 av 号与 2020 年老视频均正确 |

## 界面预览

<div align="center">
  <img src="docs/screenshot.png" alt="界面截图" width="480">
</div>

## 使用方法

1. 打开程序
2. 输入或粘贴以下**任意一种**格式：

   | 输入 | 说明 |
   | :--- | :--- |
   | `BV13fpm6mEbk` | BV 号 |
   | `av117439639586390` | av 号（带前缀） |
   | `117439639586390` | av 号（纯数字） |
   | `https://www.bilibili.com/video/BV13fpm6mEbk/` | 完整链接 |

3. 结果自动显示在下方
4. 点「复制结果」复制

> **首次运行提示**
> 程序未做数字签名，Windows 可能弹出「已保护你的电脑」。
> 点 **更多信息** → **仍要运行** 即可。

## 换算原理

B 站的两套编号一一对应，换算过程如下：

```
av → BV                          BV → av
──────────────────────           ──────────────────────
① 与掩码异或                      ① 去掉 BV1 前缀，反转
② 转成 9 位 58 进制               ② 交换第 2/8、4/7 位
③ 交换第 2/8、4/7 位              ③ 按 58 的权求和
④ 反转，前面加 "BV1"              ④ 与掩码异或
```

涉及三个常量：

| 常量 | 值 | 作用 |
| :--- | :--- | :--- |
| 字母表 | `FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf` | 58 进制字符集，去掉了易混淆的 `0 O I l` |
| 掩码 | `2275242641476827` | 打散连续编号，使其无法被顺序枚举 |
| 位数 | 9 位 | `58⁹ ≈ 7.4×10¹⁵`，足够覆盖 53 位整数 |

> **为什么网上的转换器会算错？**
> 2020 年流传的版本只用 6 位 58 进制，上限是 `58⁶ ≈ 380 亿`。
> av 号超过这个值后就会得到错误结果（甚至负数）。本项目使用 9 位版本。

## 从源码运行

只依赖 Python 标准库（tkinter），无需安装任何第三方包。

```bash
python bv_aid_v2.py
```

要求 Python 3.8 及以上。

## 自己打包

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon icon.ico --name bv-av-converter bv_aid_v2.py
```

或直接双击 `build.bat`，产物在 `dist/bv-av-converter.exe`。

## 已知限制

- `b23.tv` 短链接需先在浏览器中展开为完整地址
- 输入格式不正确时给出提示，不会崩溃

## 免责声明

本项目为非官方工具，与哔哩哔哩无关联。
BV 号换算规则由社区逆向整理，仅供学习交流使用。

## License

[MIT](LICENSE)
