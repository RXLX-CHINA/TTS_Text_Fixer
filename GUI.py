#!/usr/bin/env python3
"""
TTS文案多音字替换助手 - 正式版v1.0.2
修复：推荐读音与字符错位问题
采用长度校验+自动回退机制，确保索引始终对齐
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
from dataclasses import dataclass
from typing import List, Optional, Dict
import pypinyin
from pypinyin import Style

# 导入你的字典
from replace_dict import replace_dict

import base64

png_base64 = """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
IiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAIC
HQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEA
ACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAi
INABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgId
AAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAA
IAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg
0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0A
AAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAg
AgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQ
AQAAIAICHQAAACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAA
ACIg0AEAACACAh0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACAC
Ah0AAAAiINABAAAgAgIdAAAAIiDQAQAAIAICHQAAACIg0AEAACAC/z9LNo5e6Jnh
RAAAAABJRU5ErkJggg=="""


@dataclass
class HeteronymInstance:
    index: int
    row: int
    col: int
    char: str
    all_readings: List[str]
    recommended: str
    context_left: str
    context_right: str
    selected_reading: Optional[str] = None
    custom_replacement: Optional[str] = None
    ignore: bool = False
    smart_processed: bool = True
    use_pinyin: bool = False

    def get_final_replacement(self) -> Optional[str]:
        if self.ignore:
            return None
        if self.custom_replacement:
            return self.custom_replacement
        if self.selected_reading:
            if self.use_pinyin:
                return self.selected_reading
            return replace_dict.get(self.selected_reading)
        return None

    def get_status(self) -> str:
        if self.ignore and self.smart_processed:
            return "智能忽略"
        if self.ignore and not self.smart_processed:
            return "已忽略"
        if not self.smart_processed:
            return "手动修改"
        if (self.selected_reading or self.custom_replacement) and self.smart_processed:
            return "智能替换"
        return "智能保留"

    def get_color(self) -> str:
        status = self.get_status()
        colors = {
            "智能保留": "smart_keep",
            "智能忽略": "lightgray",
            "智能替换": "lightgreen",
            "手动修改": "lightblue",
            "已忽略": "lightgray"
        }
        return colors.get(status, "white")


class PinyinReplacerGUI:
    def __init__(self, root):
        self.root = root
        root.title("TTS文案多音字替换助手 - 正式版v1.0.2")
        root.geometry("2200x1000")

        self.original_text = ""
        self.instances: List[HeteronymInstance] = []
        self.current_index = -1
        self.smart_enabled = True
        self.hide_processed = False
        self.fallback_to_pinyin = False

        self.word_readings_path = os.path.join(os.path.dirname(__file__), "word_readings.json")
        self.word_readings = self.load_word_readings()

        self.create_widgets()
        self.create_context_menu()

    # ---------- 词汇表加载 ----------
    def load_word_readings(self) -> Dict[str, Dict[str, str]]:
        default = {
            "中弹": {"中": "zhong4"},
            "目的": {"的": "di4"},
        }
        if not os.path.exists(self.word_readings_path):
            try:
                with open(self.word_readings_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False, indent=2)
            except:
                pass
            return default
        try:
            with open(self.word_readings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载词汇表失败：{e}\n将使用默认词汇表。")
            return default

    # ---------- 界面构建 ----------
    def create_widgets(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=2)

        tool_frame = ttk.Frame(left_frame)
        tool_frame.pack(fill=tk.X, pady=(0,5))
        self.file_path_var = tk.StringVar()
        ttk.Entry(tool_frame, textvariable=self.file_path_var, width=30).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(tool_frame, text="打开文件", command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(tool_frame, text="分析多音字", command=self.analyze).pack(side=tk.LEFT, padx=2)

        self.smart_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tool_frame, text="自动智能预判", variable=self.smart_var, command=self.toggle_smart).pack(side=tk.LEFT, padx=5)
        ttk.Button(tool_frame, text="应用智能预判", command=self.apply_smart_manually).pack(side=tk.LEFT, padx=2)

        ttk.Button(tool_frame, text="编辑词汇表", command=self.edit_word_readings).pack(side=tk.LEFT, padx=2)
        ttk.Button(tool_frame, text="重新加载词汇表", command=self.reload_word_readings).pack(side=tk.LEFT, padx=2)

        self.fallback_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tool_frame, text="无替换字时替换为拼音", variable=self.fallback_var, command=self.toggle_fallback).pack(side=tk.LEFT, padx=5)

        self.hide_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tool_frame, text="隐藏已处理", variable=self.hide_var, command=self.toggle_hide_processed).pack(side=tk.LEFT, padx=5)

        self.input_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("微软雅黑", 12))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.bind('<Button-1>', self.on_text_click)
        self.input_text.bind('<Motion>', self.on_text_motion)

        legend_nav_frame = ttk.Frame(left_frame)
        legend_nav_frame.pack(fill=tk.X, pady=5)

        legend_frame = ttk.Frame(legend_nav_frame)
        legend_frame.pack(side=tk.LEFT, anchor='w')
        self._add_legend(legend_frame)

        nav_frame = ttk.Frame(legend_nav_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="◀ 上一个", command=self.prev_heteronym).pack(side=tk.LEFT, padx=2)
        self.nav_label = ttk.Label(nav_frame, text="0 / 0")
        self.nav_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="下一个 ▶", command=self.next_heteronym).pack(side=tk.LEFT, padx=2)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        ttk.Label(right_frame, text="多音字列表（双击行修改，可多选）", font=("微软雅黑", 10)).pack(anchor='w')

        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=('idx','pos','char','all_read','rec_read','context','status','replace_to'),
                                 show='headings', selectmode='extended')
        self.tree.heading('idx', text='序号')
        self.tree.heading('pos', text='位置(行:列)')
        self.tree.heading('char', text='字')
        self.tree.heading('all_read', text='所有读音 (替换字)')
        self.tree.heading('rec_read', text='推荐读音 (替换字)')
        self.tree.heading('context', text='前后文')
        self.tree.heading('status', text='状态')
        self.tree.heading('replace_to', text='替换为')

        self.tree.column('idx', width=50, minwidth=40)
        self.tree.column('pos', width=80, minwidth=60)
        self.tree.column('char', width=50, minwidth=40)
        self.tree.column('all_read', width=280, minwidth=150)
        self.tree.column('rec_read', width=130, minwidth=100)
        self.tree.column('context', width=300, minwidth=150)
        self.tree.column('status', width=90, minwidth=70)
        self.tree.column('replace_to', width=80, minwidth=60)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 行标签背景色
        self.tree.tag_configure('smart_keep', background='white')
        self.tree.tag_configure('lightgray', background='#E0E0E0')
        self.tree.tag_configure('lightgreen', background='lightgreen')
        self.tree.tag_configure('lightblue', background='lightblue')

        self.tree.bind('<Double-1>', self.on_table_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="一键替换（推荐读音）", command=self.one_click_replace).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="批量忽略指定字", command=self.batch_ignore).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="批量替换指定字", command=self.batch_replace).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="一键忽略轻声", command=self.ignore_light_tone).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="生成结果", command=self.generate_result).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导出结果", command=self.export_result).pack(side=tk.LEFT, padx=2)

        self.output_text = scrolledtext.ScrolledText(bottom_frame, height=6, wrap=tk.WORD, font=("微软雅黑", 10))
        self.output_text.pack(fill=tk.X, pady=5)

    def _add_legend(self, parent):
        colors = [
            ("白色+红字", "white", "智能保留"),
            ("亮灰", "#E0E0E0", "智能忽略 / 已忽略"),
            ("绿色", "lightgreen", "智能替换"),
            ("浅蓝", "lightblue", "手动修改")
        ]
        for text, color, desc in colors:
            frame = ttk.Frame(parent)
            frame.pack(side=tk.LEFT, padx=5)
            label = tk.Label(frame, text="  ", bg=color, width=2, relief=tk.RIDGE)
            label.pack(side=tk.LEFT)
            ttk.Label(frame, text=desc).pack(side=tk.LEFT, padx=2)

    # ---------- 文件操作 ----------
    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.file_path_var.set(filepath)
                self.instances = []
                self.current_index = -1
                self.refresh_display()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败：{e}")

    # ---------- 词汇表编辑/重载 ----------
    def edit_word_readings(self):
        if not os.path.exists(self.word_readings_path):
            self.load_word_readings()
        try:
            if sys.platform == 'win32':
                os.startfile(self.word_readings_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', self.word_readings_path])
            else:
                subprocess.Popen(['xdg-open', self.word_readings_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开编辑器：{e}")

    def reload_word_readings(self):
        self.word_readings = self.load_word_readings()
        if self.instances:
            self.apply_smart_policy(force=True)
            self.refresh_display()
        messagebox.showinfo("提示", "词汇表已重新加载")

    # ---------- 智能匹配（支持变体） ----------
    def _is_word_at_position(self, text, pos, word):
        # 先尝试原词匹配
        start = text.find(word, max(0, pos-len(word)+1), min(len(text), pos+len(word)))
        if start != -1 and start <= pos < start + len(word):
            return True
        # 尝试插入助词 "了", "着", "过"
        particles = ['了', '着', '过']
        for p in particles:
            for j in range(len(word) + 1):
                modified = word[:j] + p + word[j:]
                start = text.find(modified, max(0, pos-len(modified)+1), min(len(text), pos+len(modified)))
                if start != -1 and start <= pos < start + len(modified):
                    return True
        return False

    # ---------- 分析 ----------
    def analyze(self):
        text = self.input_text.get('1.0', 'end-1c')
        if not text.strip():
            messagebox.showwarning("提示", "请输入文本")
            return
        self.original_text = text
        self.instances = self._get_heteronym_instances(text)

        for inst in self.instances:
            pos = self.input_text.index(f"1.0 + {inst.index}c")
            row, col = pos.split('.')
            inst.row = int(row) - 1
            inst.col = int(col) - 1

        self.current_index = -1

        self.apply_smart_policy(force=True)

        self.refresh_display()
        messagebox.showinfo("完成", f"检测到 {len(self.instances)} 个多音字")

    def _get_heteronym_instances(self, text: str) -> List[HeteronymInstance]:
        chars = list(text)
        all_readings = pypinyin.pinyin(chars, heteronym=True, style=Style.TONE3, neutral_tone_with_five=True)

        # 获取推荐读音：先尝试上下文消歧（传入字符串）
        recommended_raw = pypinyin.pinyin(text, heteronym=False, style=Style.TONE3, neutral_tone_with_five=True)

        # 长度校验：若长度不一致，回退到逐字符获取（无上下文，但确保不错位）
        if len(recommended_raw) != len(chars):
            # 回退方案：逐个字符获取默认读音
            fallback = pypinyin.pinyin(chars, heteronym=False, style=Style.TONE3, neutral_tone_with_five=True)
            recommended = [r[0] if r else '' for r in fallback]
        else:
            # 正常情况，提取每个字符的推荐读音
            recommended = [r[0] if r else '' for r in recommended_raw]

        instances = []
        for i, readings in enumerate(all_readings):
            readings = [r for r in readings if r]
            if len(readings) > 1:
                rec = recommended[i] if i < len(recommended) and recommended[i] else readings[0]
                left = text[max(0, i-5):i]
                right = text[i+1:min(len(text), i+6)]
                instances.append(HeteronymInstance(
                    index=i,
                    row=0, col=0,
                    char=chars[i],
                    all_readings=readings,
                    recommended=rec,
                    context_left=left,
                    context_right=right,
                    smart_processed=True,
                    use_pinyin=False
                ))
        return instances

    # ---------- 智能策略 ----------
    def apply_smart_policy(self, force=False):
        if not self.smart_enabled and not force:
            return
        full_text = self.original_text
        for inst in self.instances:
            # 跳过手动操作过的实例
            if not inst.smart_processed:
                continue

            inst.ignore = False
            inst.selected_reading = None
            inst.custom_replacement = None
            inst.use_pinyin = False

            matched = False
            for word, reading_dict in self.word_readings.items():
                if inst.char not in reading_dict:
                    continue
                if self._is_word_at_position(full_text, inst.index, word):
                    correct_reading = reading_dict.get(inst.char)
                    if correct_reading:
                        if replace_dict.get(correct_reading) is not None:
                            inst.selected_reading = correct_reading
                            inst.ignore = False
                            inst.custom_replacement = None
                            inst.smart_processed = True
                            matched = True
                            break
                        else:
                            if self.fallback_to_pinyin:
                                inst.selected_reading = correct_reading
                                inst.use_pinyin = True
                                inst.ignore = False
                                inst.custom_replacement = None
                                inst.smart_processed = True
                                matched = True
                                break
            if matched:
                continue

            # 特殊规则
            if inst.char == '的':
                inst.ignore = False
                inst.smart_processed = True
                inst.selected_reading = None
                inst.custom_replacement = None
                continue

            if inst.char in ('地', '得'):
                if inst.recommended == 'dei3' and replace_dict.get('dei3') is None:
                    if self.fallback_to_pinyin:
                        inst.selected_reading = 'dei3'
                        inst.use_pinyin = True
                        inst.ignore = False
                        inst.custom_replacement = None
                        inst.smart_processed = True
                        continue
                    else:
                        inst.smart_processed = True
                        inst.ignore = False
                        continue
                inst.custom_replacement = '的'
                inst.ignore = False
                inst.selected_reading = None
                inst.smart_processed = True
                continue

            if inst.char in ('一', '不'):
                inst.ignore = True
                inst.smart_processed = True
                inst.selected_reading = None
                inst.custom_replacement = None
                continue

            if inst.recommended.endswith('5'):
                inst.ignore = True
                inst.smart_processed = True
                inst.selected_reading = None
                inst.custom_replacement = None
                continue

            inst.smart_processed = True
            inst.ignore = False

    def apply_smart_manually(self):
        if not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        self.apply_smart_policy(force=True)
        self.refresh_display()
        messagebox.showinfo("完成", "智能预判已应用")

    # ---------- 状态获取 ----------
    def get_status_and_color(self, inst: HeteronymInstance):
        status = inst.get_status()
        color = inst.get_color()
        return status, color

    # ---------- 刷新显示 ----------
    def refresh_display(self):
        if not self.instances:
            self.nav_label.config(text="0 / 0")
            for tag in ('smart_keep', 'lightgray', 'lightgreen', 'lightblue', 'highlight'):
                self.input_text.tag_delete(tag)
            self.tree.selection_remove(*self.tree.selection())
            for item in self.tree.get_children():
                self.tree.delete(item)
            return

        for tag in ('smart_keep', 'lightgray', 'lightgreen', 'lightblue', 'highlight'):
            self.input_text.tag_delete(tag)
        self.input_text.tag_config('smart_keep', background='white', foreground='red')
        self.input_text.tag_config('lightgray', background='#E0E0E0')
        self.input_text.tag_config('lightgreen', background='lightgreen')
        self.input_text.tag_config('lightblue', background='lightblue')
        self.input_text.tag_config('highlight', background='orange')

        for idx, inst in enumerate(self.instances):
            pos = f"{inst.row+1}.{inst.col+1}"
            color = inst.get_color()
            self.input_text.tag_add(color, pos, f"{pos}+1c")
            if idx == self.current_index:
                self.input_text.tag_add('highlight', pos, f"{pos}+1c")

        total = len(self.instances)
        cur = self.current_index + 1 if self.current_index >= 0 else 0
        self.nav_label.config(text=f"{cur} / {total}")

        if self.current_index >= 0:
            inst = self.instances[self.current_index]
            pos = f"{inst.row+1}.{inst.col+1}"
            self.input_text.see(pos)
            self.input_text.mark_set("insert", pos)

        self._rebuild_table()

    def _rebuild_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        hide = self.hide_var.get()
        for idx, inst in enumerate(self.instances):
            status, color = self.get_status_and_color(inst)
            if hide and status in ("智能替换", "手动修改", "已忽略"):
                continue
            all_str = " | ".join([f"{r}→{replace_dict.get(r, '?')}" for r in inst.all_readings])
            rec_str = f"{inst.recommended}→{replace_dict.get(inst.recommended, '?')}"
            context = f"...{inst.context_left}[{inst.char}]{inst.context_right}..."
            pos_str = f"{inst.row+1}:{inst.col+1}"
            replace_to = self._get_replace_to_text(inst)
            values = (idx+1, pos_str, inst.char, all_str, rec_str, context, status, replace_to)
            self.tree.insert('', tk.END, values=values, tags=(color,))

        if self.current_index >= 0:
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if values and int(values[0]) == self.current_index + 1:
                    self.tree.selection_add(item)
                    self.tree.see(item)
                    break

    def _get_replace_to_text(self, inst: HeteronymInstance) -> str:
        repl = inst.get_final_replacement()
        if repl:
            if inst.use_pinyin:
                return f"{inst.char}→拼音({repl})"
            return f"{inst.char}→{repl}"
        return "—"

    # ---------- 点击原文跳转 ----------
    def on_text_click(self, event):
        try:
            idx = self.input_text.index(f"@{event.x},{event.y}")
            row, col = idx.split('.')
            row = int(row) - 1
            col = int(col)
        except:
            return

        for i, inst in enumerate(self.instances):
            if inst.row == row and inst.col == col:
                self.current_index = i
                self.refresh_display()
                return

        nearest = None
        min_dist = float('inf')
        for i, inst in enumerate(self.instances):
            if inst.row == row:
                dist = abs(inst.col - col)
                if dist < min_dist:
                    min_dist = dist
                    nearest = i
        if nearest is not None and min_dist <= 5:
            self.current_index = nearest
            self.refresh_display()

    # ---------- 悬停提示 ----------
    def on_text_motion(self, event):
        try:
            idx = self.input_text.index(f"@{event.x},{event.y}")
            row, col = idx.split('.')
            row = int(row) - 1
            col = int(col)
        except:
            return
        for inst in self.instances:
            if inst.row == row and inst.col == col:
                repl = inst.get_final_replacement()
                if repl:
                    if inst.use_pinyin:
                        self.input_text.config(cursor="hand2")
                        self.input_text.tooltip_text = f"替换为拼音：{repl}"
                    else:
                        self.input_text.config(cursor="hand2")
                        self.input_text.tooltip_text = f"替换为：{repl}"
                else:
                    self.input_text.config(cursor="")
                    self.input_text.tooltip_text = ""
                break
        else:
            self.input_text.config(cursor="")
            self.input_text.tooltip_text = ""

    # ---------- 导航 ----------
    def navigate_to(self, index):
        if not self.instances:
            return
        if index < 0:
            index = 0
        if index >= len(self.instances):
            index = len(self.instances) - 1
        self.current_index = index
        self.refresh_display()

    def prev_heteronym(self):
        self.navigate_to(self.current_index - 1)

    def next_heteronym(self):
        self.navigate_to(self.current_index + 1)

    # ---------- 表格双击 ----------
    def on_table_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        idx = int(values[0]) - 1
        if 0 <= idx < len(self.instances):
            self.current_index = idx
            self.refresh_display()
            self._open_edit_dialog(idx)

    # ---------- 右键菜单 ----------
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="替换为推荐读音", command=self.replace_selected_with_recommended)
        self.context_menu.add_command(label="忽略（信任TTS）", command=self.ignore_selected)
        self.context_menu.add_command(label="取消忽略", command=self.unignore_selected)
        self.context_menu.add_command(label="手动选择读音...", command=self.manual_select_reading)
        self.context_menu.add_command(label="自定义替换...", command=self.custom_replace_selected)

    def show_context_menu(self, event):
        if self.tree.selection():
            for item in self.context_menu.winfo_children():
                item.config(state=tk.NORMAL)
        else:
            for item in self.context_menu.winfo_children():
                item.config(state=tk.DISABLED)
        self.context_menu.post(event.x_root, event.y_root)

    def get_selected_instances(self):
        selected = self.tree.selection()
        inst_list = []
        for item in selected:
            values = self.tree.item(item, 'values')
            if values:
                idx = int(values[0]) - 1
                if 0 <= idx < len(self.instances):
                    inst_list.append(self.instances[idx])
        return inst_list

    def replace_selected_with_recommended(self):
        insts = self.get_selected_instances()
        if not insts:
            return
        for inst in insts:
            if replace_dict.get(inst.recommended) is None:
                if not self._ask_pinyin_or_keep(inst, inst.recommended):
                    continue
            else:
                inst.selected_reading = inst.recommended
                inst.ignore = False
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
        self.refresh_display()
        messagebox.showinfo("完成", f"已为 {len(insts)} 个实例应用推荐读音")

    def _ask_pinyin_or_keep(self, inst, reading):
        resp = messagebox.askyesno("无替换字", f"读音 '{reading}' 没有对应的替换字。\n是否替换为拼音 '{reading}'？\n（点击“是”替换为拼音，点击“否”保留原文）")
        if resp:
            inst.selected_reading = reading
            inst.use_pinyin = True
            inst.ignore = False
            inst.custom_replacement = None
            inst.smart_processed = False
            return True
        else:
            inst.selected_reading = None
            inst.use_pinyin = False
            inst.ignore = False
            inst.custom_replacement = None
            inst.smart_processed = False
            return False

    def ignore_selected(self):
        insts = self.get_selected_instances()
        if not insts:
            return
        for inst in insts:
            inst.ignore = True
            inst.selected_reading = None
            inst.custom_replacement = None
            inst.smart_processed = False
            inst.use_pinyin = False
        self.refresh_display()
        messagebox.showinfo("完成", f"已忽略 {len(insts)} 个实例")

    def unignore_selected(self):
        insts = self.get_selected_instances()
        if not insts:
            return
        for inst in insts:
            inst.ignore = False
            if not inst.custom_replacement and not inst.selected_reading:
                inst.smart_processed = False
                inst.use_pinyin = False
        self.refresh_display()
        messagebox.showinfo("完成", f"已取消忽略 {len(insts)} 个实例")

    def manual_select_reading(self):
        insts = self.get_selected_instances()
        if not insts:
            return
        for inst in insts:
            self._open_edit_dialog_for_instance(inst, manual=True)
        self.refresh_display()

    def _open_edit_dialog_for_instance(self, inst, manual=True):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"修改 '{inst.char}'")
        dialog.geometry("400x350")

        tk.Label(dialog, text=f"字：{inst.char}  位置：{inst.row+1}:{inst.col+1}").pack(pady=5)
        status = inst.get_status()
        tk.Label(dialog, text=f"当前状态：{status}").pack()

        frame = tk.LabelFrame(dialog, text="选择读音")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        var = tk.StringVar(value=inst.recommended)
        for r in inst.all_readings:
            repl = replace_dict.get(r)
            if repl is None:
                disp = f"{r} → (无替换字，可替换为拼音)"
            else:
                disp = f"{r} → {repl}"
            tk.Radiobutton(frame, text=disp, variable=var, value=r).pack(anchor='w')

        custom_frame = tk.LabelFrame(dialog, text="自定义替换字")
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        custom_entry = tk.Entry(custom_frame)
        custom_entry.pack(fill=tk.X, padx=5, pady=2)

        def apply_choice():
            selected = var.get()
            if custom_entry.get():
                inst.custom_replacement = custom_entry.get()
                inst.selected_reading = None
                inst.ignore = False
                inst.use_pinyin = False
                inst.smart_processed = False
            else:
                if replace_dict.get(selected) is None:
                    resp = messagebox.askyesno("无替换字", f"读音 '{selected}' 没有对应的替换字。\n是否替换为拼音 '{selected}'？\n（点击“是”替换为拼音，点击“否”保留原文）")
                    if resp:
                        inst.selected_reading = selected
                        inst.use_pinyin = True
                        inst.ignore = False
                        inst.custom_replacement = None
                        inst.smart_processed = False
                    else:
                        inst.selected_reading = None
                        inst.use_pinyin = False
                        inst.ignore = False
                        inst.custom_replacement = None
                        inst.smart_processed = False
                else:
                    inst.selected_reading = selected
                    inst.ignore = False
                    inst.custom_replacement = None
                    inst.use_pinyin = False
                    inst.smart_processed = False
            dialog.destroy()
            self.refresh_display()

        def set_ignore():
            inst.ignore = True
            inst.selected_reading = None
            inst.custom_replacement = None
            inst.smart_processed = False
            inst.use_pinyin = False
            dialog.destroy()
            self.refresh_display()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="确认选择", command=apply_choice).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="忽略（信任TTS）", command=set_ignore, bg="orange").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def custom_replace_selected(self):
        insts = self.get_selected_instances()
        if not insts:
            return
        repl = simpledialog.askstring("自定义替换", f"请输入替换字（将应用于 {len(insts)} 个实例）：")
        if repl is None:
            return
        if not repl:
            messagebox.showwarning("提示", "替换字不能为空")
            return
        for inst in insts:
            inst.custom_replacement = repl
            inst.selected_reading = None
            inst.ignore = False
            inst.smart_processed = False
            inst.use_pinyin = False
        self.refresh_display()
        messagebox.showinfo("完成", f"已为 {len(insts)} 个实例自定义替换为 '{repl}'")

    def _open_edit_dialog(self, idx):
        inst = self.instances[idx]
        self._open_edit_dialog_for_instance(inst, manual=True)

    # ---------- 批量操作 ----------
    def one_click_replace(self):
        if not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        for inst in self.instances:
            if replace_dict.get(inst.recommended) is None:
                if self.fallback_to_pinyin:
                    inst.selected_reading = inst.recommended
                    inst.use_pinyin = True
                    inst.ignore = False
                    inst.custom_replacement = None
                    inst.smart_processed = False
                else:
                    inst.selected_reading = None
                    inst.use_pinyin = False
                    inst.ignore = False
                    inst.custom_replacement = None
                    inst.smart_processed = False
            else:
                inst.selected_reading = inst.recommended
                inst.ignore = False
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
        self.refresh_display()
        messagebox.showinfo("完成", "已全部替换为推荐读音（无替换字者根据设置处理）")

    def batch_ignore(self):
        if not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        char = simpledialog.askstring("批量忽略", "请输入要忽略（信任TTS）的字：")
        if not char:
            return
        count = 0
        for inst in self.instances:
            if inst.char == char:
                inst.ignore = True
                inst.selected_reading = None
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
                count += 1
        if count:
            self.refresh_display()
            messagebox.showinfo("完成", f"已忽略 '{char}' 共 {count} 个实例")
        else:
            messagebox.showwarning("提示", f"未找到 '{char}'")

    def batch_replace(self):
        if not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        char = simpledialog.askstring("批量替换", "请输入要替换的字：")
        if not char:
            return
        reading = simpledialog.askstring("批量替换", f"请输入 '{char}' 应读的拼音（如 zhong4）：")
        if not reading:
            return
        if replace_dict.get(reading) is None:
            use_pinyin = messagebox.askyesno("无替换字", f"读音 '{reading}' 没有对应的替换字。\n是否替换为拼音 '{reading}'？\n（点击“是”替换为拼音，点击“否”保留原文）")
        else:
            use_pinyin = False
        count = 0
        for inst in self.instances:
            if inst.char == char:
                if replace_dict.get(reading) is None and not use_pinyin:
                    inst.selected_reading = None
                    inst.use_pinyin = False
                    inst.smart_processed = False
                else:
                    inst.selected_reading = reading
                    inst.use_pinyin = use_pinyin
                    inst.smart_processed = False
                inst.ignore = False
                inst.custom_replacement = None
                count += 1
        if count:
            self.refresh_display()
            msg = f"已为 '{char}' 的 {count} 个实例设置读音 '{reading}'"
            if use_pinyin:
                msg += "（替换为拼音）"
            messagebox.showinfo("完成", msg)
        else:
            messagebox.showwarning("提示", f"未找到 '{char}'")

    def ignore_light_tone(self):
        if not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        count = 0
        for inst in self.instances:
            if inst.recommended.endswith('5'):
                inst.ignore = True
                inst.selected_reading = None
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
                count += 1
        self.refresh_display()
        if count:
            messagebox.showinfo("完成", f"已忽略 {count} 个轻声实例")
        else:
            messagebox.showinfo("提示", "未检测到推荐读音为轻声的实例")

    # ---------- 结果生成 ----------
    def generate_result(self):
        if not self.original_text or not self.instances:
            messagebox.showwarning("提示", "请先分析多音字")
            return
        result = self._apply_replacements(self.original_text, self.instances)
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', result)

    def _apply_replacements(self, text: str, instances: List[HeteronymInstance]) -> str:
        sorted_insts = sorted(instances, key=lambda x: x.index)
        parts = []
        last = 0
        for inst in sorted_insts:
            parts.append(text[last:inst.index])
            if inst.ignore:
                parts.append(text[inst.index])
            else:
                repl = None
                if inst.custom_replacement:
                    repl = inst.custom_replacement
                elif inst.selected_reading:
                    if inst.use_pinyin:
                        repl = inst.selected_reading
                    else:
                        repl = replace_dict.get(inst.selected_reading)
                if repl is not None:
                    parts.append(repl)
                else:
                    parts.append(text[inst.index])
            last = inst.index + 1
        parts.append(text[last:])
        return ''.join(parts)

    def export_result(self):
        result = self.output_text.get('1.0', tk.END).strip()
        if not result:
            messagebox.showwarning("提示", "请先生成结果")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result)
                messagebox.showinfo("成功", f"结果已保存到 {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{e}")

    # ---------- 智能开关 ----------
    def toggle_smart(self):
        self.smart_enabled = self.smart_var.get()
        if self.instances:
            if self.smart_enabled:
                self.apply_smart_policy(force=True)
            self.refresh_display()

    # ---------- 隐藏已处理 ----------
    def toggle_hide_processed(self):
        self.hide_processed = self.hide_var.get()
        self._rebuild_table()

    def toggle_fallback(self):
        self.fallback_to_pinyin = self.fallback_var.get()
        if self.instances:
            self.apply_smart_policy(force=True)
            self.refresh_display()


def main():
    root = tk.Tk()  
    img = tk.PhotoImage(data=base64.b64decode(png_base64))
    root.iconphoto(True, img)
    app = PinyinReplacerGUI(root)
    root.mainloop()



if __name__ == "__main__":
    main()