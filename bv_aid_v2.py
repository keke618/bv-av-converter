# -*- coding: utf-8 -*-
"""BV / AV 转换器 v2

B 站视频编号（BV 号 / av 号）双向转换工具，带图形界面。

特点：
  * 支持 2026 新版 BV 编号（9 位 58 进制），同时对 2020 年的老视频依然正确
  * 自动识别输入是 BV 号还是 av 号，不需要手动切换
  * 可以直接粘贴完整链接，例如 https://www.bilibili.com/video/BV1xx411c7mD/
  * 边输入边转换，结果显示在只读框里，一键复制

依赖：仅 Python 标准库（tkinter），无需 pip 安装任何东西。

用法：
    python bv_aid_v2.py
"""
import os
import re
import sys
import tkinter as tk

__version__ = "2.0.0"

# ---------------------------------------------------------------- 算法
#
# B 站的视频编号有两套：
#   1. av 号：纯数字，如 av170001
#   2. BV 号：12 位字符串，固定以 "BV1" 开头，如 BV17x411w7KC
#
# 两者是**一一对应**的，换算过程如下（2026 版算法）：
#
#   av -> BV:
#       ① 与掩码异或，打乱数值分布
#       ② 转成 9 位 58 进制
#       ③ 交换第 2/8 位、第 4/7 位（打乱顺序）
#       ④ 整体反转，前面加 "BV1"
#
#   BV -> av: 上面四步倒着做
#
# 58 进制：0-9 + a-z + A-Z 共 62 个字符，去掉容易混淆的 0 O I l 后剩 58 个。
# 掩码和字母表是米哈游在客户端里写死的常量，版本升级时可能变，届时这里要同步更新。

#: 58 进制字母表（注意：不是顺序排列，是打乱过的，必须原样使用）
TABLE = "FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf"

#: 异或掩码，用于打散连续 av 号，使其无法被顺序枚举
MASK = 2275242641476827

#: 字母 -> 数值 的反查表，避免每次都用 TABLE.index() 做线性查找
TR = {c: i for i, c in enumerate(TABLE)}


def av2bv(aid):
    """av 号 -> BV 号。

    >>> av2bv(170001)
    'BV17x411w7KC'
    """
    # ① 异或掩码
    n = int(aid) ^ MASK

    # ② 转 58 进制，低位在前（digits[0] 是最低位）
    digits = []
    for _ in range(9):
        digits.append(TABLE[n % 58])
        n //= 58

    # ③ 交换两个固定位置，进一步打乱
    digits[2], digits[8] = digits[8], digits[2]
    digits[4], digits[7] = digits[7], digits[4]

    # ④ 反转成高位在前，加上前缀
    digits.reverse()
    return "BV1" + "".join(digits)


def bv2av(bv):
    """BV 号 -> av 号。

    >>> bv2av("BV17x411w7KC")
    170001
    """
    s = bv.strip()
    # 允许带 "BV1" 或 "BV" 前缀，也允许额外字符（如从链接里截出来的）
    if s.upper().startswith("BV1"):
        s = s[3:]
    elif s.upper().startswith("BV"):
        s = s[2:]
    s = s[:9]
    if len(s) != 9:
        raise ValueError("BV 号长度不对")

    # 把编码时的四步倒过来：反转 -> 换位 -> 按权求和 -> 异或
    digits = list(s)
    digits.reverse()
    digits[2], digits[8] = digits[8], digits[2]
    digits[4], digits[7] = digits[7], digits[4]

    n = 0
    for i in range(9):
        n += TR[digits[i]] * 58 ** i

    return n ^ MASK


BV_RE = re.compile(r"BV1?([0-9A-Za-z]{9,10})")
AV_RE = re.compile(r"(?:av|aid=|aid/)(\d+)", re.I)


def convert(text):
    """返回 (类型, 结果)。类型为 'bvid' 或 'aid'。"""
    text = text.strip()
    if not text:
        raise ValueError("请输入内容")
    m = BV_RE.search(text)
    if m:
        bv = "BV1" + m.group(1)
        return "aid", bv2av(bv)
    m = AV_RE.search(text)
    if m:
        return "bvid", av2bv(int(m.group(1)))
    digits = re.sub(r"[^0-9]", "", text)
    if digits and len(digits) <= 15:
        return "bvid", av2bv(int(digits))
    raise ValueError("认不出来，请输入 BV 号或 av 号")


# ---------------------------------------------------------------- 界面
BG = "#f2f3f5"
CARD = "#ffffff"
TEXT = "#1f2329"
MUTED = "#8b93a1"
ACCENT = "#fb7299"
ACCENT_DK = "#f25d8a"
BORDER = "#e5e6eb"
FIELD = "#f7f8fa"
ERR = "#f53f3f"
OK = "#00a1d6"

UI = "Microsoft YaHei UI"


class App:
    def __init__(self, root):
        self.root = root
        root.title("BV / AV 转换器")
        root.configure(bg=BG)
        root.resizable(False, False)

        self._build()
        self._set_icon()
        root.update_idletasks()
        self._center(468, root.winfo_reqheight())
        self.entry.focus_set()
        self._schedule = None

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))

    def _set_icon(self):
        try:
            if getattr(sys, "frozen", False):
                self.root.iconbitmap(default=sys.executable)
            else:
                ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
                if os.path.exists(ico):
                    self.root.iconbitmap(default=ico)
        except Exception:
            pass
    # ---------------- 组件
    def _build(self):
        root = self.root

        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=26, pady=(20, 10))
        tk.Label(header, text="BV / AV 转换器", bg=BG, fg=TEXT,
                 font=(UI, 17, "bold")).pack(anchor="w")
        tk.Label(header, text="支持新旧两套编号 · 自动识别 · 可粘贴链接", bg=BG, fg=MUTED,
                 font=(UI, 9)).pack(anchor="w", pady=(3, 0))

        card = tk.Frame(root, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(inner, text="输入 BV 号 / av 号", bg=CARD, fg=MUTED,
                 font=(UI, 9)).pack(anchor="w")
        self.entry = tk.Entry(inner, font=(UI, 13), bg=FIELD, fg=TEXT, relief="flat",
                              insertbackground=TEXT, highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=ACCENT)
        self.entry.pack(fill="x", ipady=7, pady=(5, 12))
        self.entry.bind("<Return>", lambda e: self.do_convert(True))
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<<Paste>>", lambda e: root.after(40, self._on_key))

        btns = tk.Frame(inner, bg=CARD)
        btns.pack(fill="x")
        self._primary(btns, "转 换", self.do_convert).pack(side="left")
        self._secondary(btns, "复制结果", self.do_copy, 9).pack(side="left", padx=(8, 0))
        self._ghost(btns, "清空", self.do_clear).pack(side="left", padx=(8, 0))

        tk.Label(inner, text="结果", bg=CARD, fg=MUTED,
                 font=(UI, 9)).pack(anchor="w", pady=(16, 0))
        self.result = tk.Entry(inner, font=(UI, 13), bg=FIELD, fg=TEXT, relief="flat",
                               readonlybackground=FIELD, state="readonly",
                               highlightthickness=1, highlightbackground=BORDER,
                               highlightcolor=BORDER)
        self.result.pack(fill="x", ipady=7, pady=(5, 0))
        self.result.bind("<FocusIn>", lambda e: self.result.selection_range(0, "end"))

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=(14, 0))
        self.status = tk.Label(inner, text="等待输入", bg=CARD, fg=MUTED,
                               font=(UI, 9), anchor="w")
        self.status.pack(fill="x", pady=(9, 0))

    def _primary(self, parent, text, cmd):
        wrap = tk.Frame(parent, bg=ACCENT)
        b = tk.Button(wrap, text=text, command=cmd, bg=ACCENT, fg="#ffffff",
                      activebackground=ACCENT_DK, activeforeground="#ffffff",
                      relief="flat", bd=0, cursor="hand2", width=12,
                      font=(UI, 10, "bold"), padx=4, pady=7)
        b.pack(padx=1, pady=1)
        b.bind("<Enter>", lambda e: (b.configure(bg=ACCENT_DK), wrap.configure(bg=ACCENT_DK)))
        b.bind("<Leave>", lambda e: (b.configure(bg=ACCENT), wrap.configure(bg=ACCENT)))
        return wrap

    def _secondary(self, parent, text, cmd, width):
        wrap = tk.Frame(parent, bg=BORDER)
        b = tk.Button(wrap, text=text, command=cmd, bg="#f7f8fa", fg=TEXT,
                      activebackground="#eceef1", activeforeground=TEXT,
                      relief="flat", bd=0, cursor="hand2", width=width,
                      font=(UI, 10), padx=4, pady=7)
        b.pack(padx=1, pady=1)
        b.bind("<Enter>", lambda e: b.configure(bg="#eceef1"))
        b.bind("<Leave>", lambda e: b.configure(bg="#f7f8fa"))
        return wrap

    def _ghost(self, parent, text, cmd):
        b = tk.Button(parent, text=text, command=cmd, bg=CARD, fg=MUTED,
                      activebackground=CARD, activeforeground=TEXT,
                      relief="flat", bd=0, cursor="hand2",
                      font=(UI, 10), padx=8, pady=7)
        b.bind("<Enter>", lambda e: b.configure(fg=TEXT))
        b.bind("<Leave>", lambda e: b.configure(fg=MUTED))
        return b

    # ---------------- 行为
    def _on_key(self, _event=None):
        if self._schedule:
            self.root.after_cancel(self._schedule)
        self._schedule = self.root.after(260, self._auto)

    def _auto(self):
        text = self.entry.get().strip()
        if not text:
            self._set_result("")
            self._status("等待输入", MUTED)
            return
        try:
            kind, val = convert(text)
        except Exception:
            self._set_result("")
            self._status("继续输入…", MUTED)
            return
        self._show(kind, val)

    def do_convert(self, _event=None):
        try:
            kind, val = convert(self.entry.get())
        except Exception as exc:
            self._set_result("")
            self._status(str(exc), ERR)
            return
        self._show(kind, val)

    def _show(self, kind, val):
        if kind == "aid":
            self._set_result("av%d" % val)
            self._status("已识别为 BV 号，转换为 av 号", OK)
        else:
            self._set_result(av2bv(val))
            self._status("已识别为 av 号，转换为 BV 号", OK)

    def do_copy(self):
        text = self.result.get()
        if not text:
            self._status("还没有可复制的结果", ERR)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._status("已复制到剪贴板", OK)

    def do_clear(self):
        self.entry.delete(0, "end")
        self._set_result("")
        self._status("等待输入", MUTED)
        self.entry.focus_set()

    def _set_result(self, text):
        self.result.configure(state="normal")
        self.result.delete(0, "end")
        if text:
            self.result.insert(0, text)
        self.result.configure(state="readonly")

    def _status(self, text, color):
        self.status.configure(text=text, fg=color)


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    root.option_add("*Font", (UI, 10))
    app = App(root)
    demo = os.environ.get("BVAV_DEMO")
    if demo:
        def _demo():
            app.entry.insert(0, demo)
            app.do_convert()
        root.after(250, _demo)
    if os.environ.get("BVAV_SELFTEST"):
        root.after(700, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
