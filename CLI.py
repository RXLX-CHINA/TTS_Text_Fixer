#!/usr/bin/env python3
"""
TTS文案多音字替换助手 - CLI 版 v1.0
功能与 GUI 版一致，支持命令行交互
用法：
    python cli.py "文本"
    python cli.py -f input.txt
    python cli.py -f input.txt -o output.txt
    python cli.py --no-interactive "文本"   # 直接替换不交互
"""

import os
import sys
import json
import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict
import pypinyin
from pypinyin import Style

# 导入你的字典
try:
    from replace_dict import replace_dict
except ImportError:
    print("❌ 错误：找不到 replace_dict.py，请确保该文件在当前目录。")
    sys.exit(1)

# 尝试导入 rich（用于美化表格）
try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️ 未安装 rich，将使用简易输出。建议安装：pip install rich")


@dataclass
class HeteronymInstance:
    index: int
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
        # CLI 不需要颜色，但保留状态
        return ""


class PinyinReplacerCLI:
    def __init__(self, fallback_to_pinyin: bool = False):
        self.fallback_to_pinyin = fallback_to_pinyin
        self.original_text = ""
        self.instances: List[HeteronymInstance] = []
        self.word_readings = self.load_word_readings()
        self.smart_enabled = True

    def load_word_readings(self) -> Dict[str, Dict[str, str]]:
        default = {"中弹": {"中": "zhong4"}, "目的": {"的": "di4"}}
        path = "word_readings.json"
        if not os.path.exists(path):
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False, indent=2)
            except:
                pass
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载词汇表失败：{e}，使用默认。")
            return default

    def _get_heteronym_instances(self, text: str) -> List[HeteronymInstance]:
        chars = list(text)
        all_readings = pypinyin.pinyin(chars, heteronym=True, style=Style.TONE3, neutral_tone_with_five=True)
        recommended_raw = pypinyin.pinyin(text, heteronym=False, style=Style.TONE3, neutral_tone_with_five=True)

        if len(recommended_raw) != len(chars):
            fallback = pypinyin.pinyin(chars, heteronym=False, style=Style.TONE3, neutral_tone_with_five=True)
            recommended = [r[0] if r else '' for r in fallback]
        else:
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
                    char=chars[i],
                    all_readings=readings,
                    recommended=rec,
                    context_left=left,
                    context_right=right,
                    smart_processed=True,
                    use_pinyin=False
                ))
        return instances

    def _is_word_at_position(self, text, pos, word):
        start = text.find(word, max(0, pos-len(word)+1), min(len(text), pos+len(word)))
        if start != -1 and start <= pos < start + len(word):
            return True
        particles = ['了', '着', '过']
        for p in particles:
            for j in range(len(word) + 1):
                modified = word[:j] + p + word[j:]
                start = text.find(modified, max(0, pos-len(modified)+1), min(len(text), pos+len(modified)))
                if start != -1 and start <= pos < start + len(modified):
                    return True
        return False

    def apply_smart_policy(self, force=False):
        if not self.smart_enabled and not force:
            return
        full_text = self.original_text
        for inst in self.instances:
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

    def analyze(self, text: str):
        self.original_text = text
        self.instances = self._get_heteronym_instances(text)
        self.apply_smart_policy(force=True)

    def get_replacement_text(self) -> str:
        sorted_insts = sorted(self.instances, key=lambda x: x.index)
        parts = []
        last = 0
        text = self.original_text
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

    # ---------- 交互式菜单 ----------
    def interactive_mode(self):
        if not self.instances:
            print("⚠️ 没有检测到多音字。")
            return

        self.display_table()

        while True:
            print("\n" + "="*60)
            print("请选择操作：")
            print("  1. 一键替换为推荐读音（全部）")
            print("  2. 指定某个字选择读音")
            print("  3. 指定某个字自定义替换")
            print("  4. 批量替换某字的所有实例")
            print("  5. 指定某字信任TTS（忽略）")
            print("  6. 一键忽略轻声")
            print("  7. 应用智能预判（重新计算）")
            print("  8. 切换无替换字时替换为拼音（当前：{})".format("开启" if self.fallback_to_pinyin else "关闭"))
            print("  9. 预览替换结果")
            print("  10. 生成并输出结果")
            print("  0. 退出（不保存）")
            print("="*60)

            choice = input("请输入选项 (0-10): ").strip()

            if choice == '1':
                self.one_click_replace()
            elif choice == '2':
                self.select_reading_for_char()
            elif choice == '3':
                self.custom_replace_char()
            elif choice == '4':
                self.batch_replace_char()
            elif choice == '5':
                self.ignore_char()
            elif choice == '6':
                self.ignore_light_tone()
            elif choice == '7':
                self.apply_smart_manually()
            elif choice == '8':
                self.toggle_fallback()
            elif choice == '9':
                self.preview_result()
            elif choice == '10':
                result = self.get_replacement_text()
                print("\n✅ 替换结果：\n" + result)
                return result
            elif choice == '0':
                print("退出。")
                return None
            else:
                print("⚠️ 无效选项。")

    def display_table(self):
        if not HAS_RICH:
            self._simple_table()
            return
        console = Console()
        table = Table(title="📊 多音字识别结果", show_lines=True)
        table.add_column("序号", style="cyan")
        table.add_column("位置", style="green")
        table.add_column("字", style="yellow")
        table.add_column("所有读音 (替换字)", style="magenta")
        table.add_column("推荐读音 (替换字)", style="green")
        table.add_column("前后文", style="white")
        table.add_column("状态", style="bold")

        for idx, inst in enumerate(self.instances, 1):
            all_str = " | ".join([f"{r}→{replace_dict.get(r, '?')}" for r in inst.all_readings])
            rec_str = f"{inst.recommended}→{replace_dict.get(inst.recommended, '?')}"
            context = f"...{inst.context_left}[{inst.char}]{inst.context_right}..."
            status = inst.get_status()
            table.add_row(str(idx), str(inst.index), inst.char, all_str, rec_str, context, status)

        console.print(table)

    def _simple_table(self):
        print("\n多音字列表：")
        print(f"{'序号':<4} {'位置':<6} {'字':<4} {'推荐读音':<10} {'状态':<12} {'前后文'}")
        for idx, inst in enumerate(self.instances, 1):
            rec = inst.recommended
            status = inst.get_status()
            context = f"...{inst.context_left}[{inst.char}]{inst.context_right}..."
            print(f"{idx:<4} {inst.index:<6} {inst.char:<4} {rec:<10} {status:<12} {context}")

    def one_click_replace(self):
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
        print("✅ 已全部替换为推荐读音（无替换字者根据设置处理）")
        self.display_table()

    def select_reading_for_char(self):
        char = input("请输入要修改的字: ").strip()
        if not char:
            return
        target_insts = [i for i in self.instances if i.char == char]
        if not target_insts:
            print(f"⚠️ 未找到 '{char}'")
            return
        readings = target_insts[0].all_readings
        print(f"'{char}' 的读音选项：")
        for j, r in enumerate(readings, 1):
            repl = replace_dict.get(r)
            if repl is None:
                print(f"  {j}. {r} → (无替换字，可替换为拼音)")
            else:
                print(f"  {j}. {r} → {repl}")
        try:
            sel = int(input("请选择编号: ")) - 1
            selected = readings[sel]
        except:
            print("⚠️ 无效选择")
            return

        # 检查是否有替换字
        if replace_dict.get(selected) is None:
            use_pinyin = Confirm.ask(f"读音 '{selected}' 没有替换字，是否替换为拼音？")
            if use_pinyin:
                for inst in target_insts:
                    inst.selected_reading = selected
                    inst.use_pinyin = True
                    inst.ignore = False
                    inst.custom_replacement = None
                    inst.smart_processed = False
            else:
                # 保留原文
                for inst in target_insts:
                    inst.selected_reading = None
                    inst.use_pinyin = False
                    inst.ignore = False
                    inst.custom_replacement = None
                    inst.smart_processed = False
        else:
            for inst in target_insts:
                inst.selected_reading = selected
                inst.ignore = False
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
        print("✅ 已更新。")
        self.display_table()

    def custom_replace_char(self):
        char = input("请输入要修改的字: ").strip()
        if not char:
            return
        repl = input("请输入替换后的字: ").strip()
        if not repl:
            print("⚠️ 替换字不能为空")
            return
        count = 0
        for inst in self.instances:
            if inst.char == char:
                inst.custom_replacement = repl
                inst.selected_reading = None
                inst.ignore = False
                inst.smart_processed = False
                inst.use_pinyin = False
                count += 1
        if count:
            print(f"✅ 已为 '{char}' 的 {count} 个实例自定义替换为 '{repl}'")
            self.display_table()
        else:
            print(f"⚠️ 未找到 '{char}'")

    def batch_replace_char(self):
        char = input("请输入要替换的字: ").strip()
        if not char:
            return
        reading = input(f"请输入 '{char}' 应读的拼音（如 zhong4）: ").strip()
        if not reading:
            return
        if replace_dict.get(reading) is None:
            use_pinyin = Confirm.ask(f"读音 '{reading}' 没有替换字，是否替换为拼音？")
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
            msg = f"已为 '{char}' 的 {count} 个实例设置读音 '{reading}'"
            if use_pinyin:
                msg += "（替换为拼音）"
            print("✅", msg)
            self.display_table()
        else:
            print(f"⚠️ 未找到 '{char}'")

    def ignore_char(self):
        char = input("请输入要信任TTS（忽略）的字: ").strip()
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
            print(f"✅ 已忽略 '{char}' 共 {count} 个实例")
            self.display_table()
        else:
            print(f"⚠️ 未找到 '{char}'")

    def ignore_light_tone(self):
        count = 0
        for inst in self.instances:
            if inst.recommended.endswith('5'):
                inst.ignore = True
                inst.selected_reading = None
                inst.custom_replacement = None
                inst.smart_processed = False
                inst.use_pinyin = False
                count += 1
        if count:
            print(f"✅ 已忽略 {count} 个轻声实例")
            self.display_table()
        else:
            print("ℹ️ 未检测到推荐读音为轻声的实例")

    def apply_smart_manually(self):
        self.apply_smart_policy(force=True)
        print("✅ 智能预判已重新应用")
        self.display_table()

    def toggle_fallback(self):
        self.fallback_to_pinyin = not self.fallback_to_pinyin
        print(f"✅ 无替换字时替换为拼音：{'开启' if self.fallback_to_pinyin else '关闭'}")
        # 重新应用智能策略以更新
        self.apply_smart_policy(force=True)
        self.display_table()

    def preview_result(self):
        result = self.get_replacement_text()
        print("\n📝 当前替换结果预览：\n" + result)


def main():
    parser = argparse.ArgumentParser(description="TTS文案多音字替换助手 - CLI版")
    parser.add_argument("text", nargs="?", help="要处理的文本")
    parser.add_argument("-f", "--file", help="从文件读取输入")
    parser.add_argument("-o", "--output", help="将结果输出到文件（若配合 --no-interactive 则直接输出）")
    parser.add_argument("--no-interactive", action="store_true", help="非交互模式：直接使用推荐读音替换并输出")
    parser.add_argument("--fallback-pinyin", action="store_true", help="无替换字时替换为拼音（默认关闭）")
    args = parser.parse_args()

    # 读取输入
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        # 从 stdin 读取
        print("请输入文本（按 Ctrl+D 结束）：")
        text = sys.stdin.read()
        if not text:
            print("❌ 未输入文本")
            sys.exit(1)

    if not text.strip():
        print("❌ 文本为空")
        sys.exit(1)

    cli = PinyinReplacerCLI(fallback_to_pinyin=args.fallback_pinyin)
    cli.analyze(text)

    if args.no_interactive:
        # 非交互模式：直接一键替换并输出
        cli.one_click_replace()
        result = cli.get_replacement_text()
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ 结果已保存到 {args.output}")
        else:
            print(result)
    else:
        # 交互模式
        if not cli.instances:
            print("✅ 未检测到多音字")
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(text)
            return
        result = cli.interactive_mode()
        if result is not None and args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ 结果已保存到 {args.output}")
        elif result is not None and not args.output:
            print("\n" + "="*60)
            print("最终结果：")
            print(result)


if __name__ == "__main__":
    main()