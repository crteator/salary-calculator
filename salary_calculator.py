# salary_calculator.py
import calendar
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class AdvancedSalaryCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("薪资计算系统")
        self.root.geometry("920x1050")
        self.root.minsize(850, 950)
        
        self.style = tb.Style(theme="flatly")
        
        # 薪资参数
        self.normal_rate = 20.25      # 正常/常规加班时薪
        self.holiday_rate = 40.5      # 节假日加班时薪
        self.day_allowance = 10       # 白班补贴（元/天）
        self.night_allowance = 62     # 夜班补贴（元/天）
        
        # 默认固定金额
        self.defaults = {
            'base': 2030, 'perf': 400, 'meal': 400, 'full': 100,
            'social': 432, 'fund': 300,
            'day_days': 0, 'night_days': 0, 'overtime_hours': 0, 'holiday_hours': 0
        }
        
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        
        self.create_widgets()
        self.update_work_info()
    
    # ---------- 节假日及考勤计算函数 ----------
    def is_weekend(self, d):
        return d.weekday() >= 5
    
    def get_legal_holidays(self, year, month):
        holidays_by_year = {
            2024: ["2024-01-01","2024-02-10","2024-02-11","2024-02-12","2024-04-04","2024-05-01","2024-06-10","2024-09-17","2024-10-01","2024-10-02","2024-10-03"],
            2025: ["2025-01-01","2025-01-29","2025-01-30","2025-01-31","2025-04-04","2025-05-01","2025-05-31","2025-10-06","2025-10-01","2025-10-02","2025-10-03"],
            2026: ["2026-01-01","2026-02-17","2026-02-18","2026-02-19","2026-04-05","2026-05-01","2026-06-19","2026-09-25","2026-10-01","2026-10-02","2026-10-03"],
            2027: ["2027-01-01","2027-02-06","2027-02-07","2027-02-08","2027-04-05","2027-05-01","2027-06-08","2027-09-15","2027-10-01","2027-10-02","2027-10-03"],
            2028: ["2028-01-01","2028-01-26","2028-01-27","2028-01-28","2028-04-04","2028-05-01","2028-05-28","2028-10-03","2028-10-01","2028-10-02","2028-10-03"],
            2029: ["2029-01-01","2029-02-13","2029-02-14","2029-02-15","2029-04-04","2029-05-01","2029-06-16","2029-09-22","2029-10-01","2029-10-02","2029-10-03"],
            2030: ["2030-01-01","2030-02-03","2030-02-04","2030-02-05","2030-04-05","2030-05-01","2030-06-05","2030-09-12","2030-10-01","2030-10-02","2030-10-03"],
        }
        holidays = holidays_by_year.get(year, [])
        month_str = f"{year}-{month:02d}"
        return [h for h in holidays if h.startswith(month_str)]
    
    def get_work_info(self, year, month):
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                last_day = 29
            else:
                last_day = 28
        elif month in [4,6,9,11]:
            last_day = 30
        else:
            last_day = 31
        
        work_days = 0
        weekend_days = 0
        holiday_days = 0
        holiday_list = []
        legal_holidays = self.get_legal_holidays(year, month)
        
        for day in range(1, last_day + 1):
            d = date(year, month, day)
            ds = d.strftime("%Y-%m-%d")
            if ds in legal_holidays:
                holiday_days += 1
                holiday_list.append(f"{month}月{day}日")
            elif self.is_weekend(d):
                weekend_days += 1
            else:
                work_days += 1
        
        return {
            "total_days": last_day,
            "work_days": work_days,
            "weekend_days": weekend_days,
            "holiday_days": holiday_days,
            "holiday_list": holiday_list
        }
    # -----------------------------------------
    
    def create_widgets(self):
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=BOTH, expand=YES)
        
        # 可滚动区域
        canvas = tb.Canvas(main, highlightthickness=0, bg="#ffffff")
        scrollbar = tb.Scrollbar(main, orient=VERTICAL, command=canvas.yview, bootstyle="secondary")
        scrollable = tb.Frame(canvas)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        def _on_mousewheel(event):
            widget = event.widget
            if hasattr(self, 'income_tree') and (widget == self.income_tree or widget == self.deduction_tree):
                return
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 页眉
        header = tb.Frame(scrollable)
        header.pack(fill=X, pady=(0,20))
        tb.Label(header, text="薪酬计算系统", font=("Segoe UI",28,"bold"), foreground="#2c3e50").pack()
        tb.Label(header, text="智能 · 精准 · 便捷", font=("Segoe UI",11), foreground="#7f8c8d").pack()
        
        # 1. 月份卡片
        month_card = tb.Labelframe(scrollable, text="📅 计算周期", padding=15, bootstyle="primary")
        month_card.pack(fill=X, pady=12)
        sel_frame = tb.Frame(month_card)
        sel_frame.pack(pady=5)
        tb.Label(sel_frame, text="年份", font=("Segoe UI",10)).pack(side=LEFT, padx=5)
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_cb = ttk.Combobox(sel_frame, textvariable=self.year_var,
                               values=[str(y) for y in range(2020,2031)],
                               width=8, state="readonly")
        year_cb.pack(side=LEFT, padx=5)
        year_cb.bind('<<ComboboxSelected>>', lambda e: self.update_work_info())
        tb.Label(sel_frame, text="月份", font=("Segoe UI",10)).pack(side=LEFT, padx=15)
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_cb = ttk.Combobox(sel_frame, textvariable=self.month_var,
                                values=[str(m) for m in range(1,13)],
                                width=5, state="readonly")
        month_cb.pack(side=LEFT, padx=5)
        month_cb.bind('<<ComboboxSelected>>', lambda e: self.update_work_info())
        
        # 2. 考勤统计卡片
        info_card = tb.Labelframe(scrollable, text="📊 当月标准考勤（自动识别）", padding=10, bootstyle="info")
        info_card.pack(fill=X, pady=12)
        self.info_text = tb.Text(info_card, height=5, font=("Consolas",10), wrap=WORD, padx=10, pady=5)
        self.info_text.pack(fill=X)
        
        # 3. 基本工资与补贴（两列）
        salary_card = tb.Labelframe(scrollable, text="💰 基本薪酬与补贴", padding=15, bootstyle="success")
        salary_card.pack(fill=X, pady=12)
        
        self.entries = {}
        left_sal = tb.Frame(salary_card)
        left_sal.pack(side=LEFT, fill=BOTH, expand=YES, padx=10)
        right_sal = tb.Frame(salary_card)
        right_sal.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)
        
        left_fields = [
            ("底薪 (元)", "base", self.defaults['base']),
            ("绩效 (元)", "perf", self.defaults['perf']),
            ("餐补 (元)", "meal", self.defaults['meal']),
        ]
        right_fields = [
            ("全勤奖 (元)", "full", self.defaults['full']),
            ("社保扣款 (元)", "social", self.defaults['social']),
            ("公积金扣款 (元)", "fund", self.defaults['fund']),
        ]
        
        for label, key, default in left_fields:
            row = tb.Frame(left_sal)
            row.pack(fill=X, pady=8)
            tb.Label(row, text=label, width=12, anchor=W, font=("Segoe UI",10)).pack(side=LEFT)
            e = tb.Entry(row, width=18, bootstyle="secondary", font=("Segoe UI",10))
            e.pack(side=LEFT, padx=12)
            e.insert(0, str(default))
            self.entries[key] = e
        
        for label, key, default in right_fields:
            row = tb.Frame(right_sal)
            row.pack(fill=X, pady=8)
            tb.Label(row, text=label, width=12, anchor=W, font=("Segoe UI",10)).pack(side=LEFT)
            e = tb.Entry(row, width=18, bootstyle="secondary", font=("Segoe UI",10))
            e.pack(side=LEFT, padx=12)
            e.insert(0, str(default))
            self.entries[key] = e
        
        # 4. 考勤数据（两列）
        attend_card = tb.Labelframe(scrollable, text="📋 本月考勤录入", padding=15, bootstyle="warning")
        attend_card.pack(fill=X, pady=12)
        
        left_att = tb.Frame(attend_card)
        left_att.pack(side=LEFT, fill=BOTH, expand=YES, padx=10)
        right_att = tb.Frame(attend_card)
        right_att.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)
        
        att_left = [
            ("白班天数", "day_days", self.defaults['day_days']),
            ("夜班天数", "night_days", self.defaults['night_days']),
        ]
        att_right = [
            ("常规加班工时 (小时)", "overtime_hours", self.defaults['overtime_hours']),
            ("节假日加班工时 (小时)", "holiday_hours", self.defaults['holiday_hours']),
        ]
        
        for label, key, default in att_left:
            row = tb.Frame(left_att)
            row.pack(fill=X, pady=8)
            tb.Label(row, text=label, width=12, anchor=W, font=("Segoe UI",10)).pack(side=LEFT)
            e = tb.Entry(row, width=18, bootstyle="secondary", font=("Segoe UI",10))
            e.pack(side=LEFT, padx=12)
            e.insert(0, str(default))
            self.entries[key] = e
        
        for label, key, default in att_right:
            row = tb.Frame(right_att)
            row.pack(fill=X, pady=8)
            tb.Label(row, text=label, width=18, anchor=W, font=("Segoe UI",10)).pack(side=LEFT)
            e = tb.Entry(row, width=18, bootstyle="secondary", font=("Segoe UI",10))
            e.pack(side=LEFT, padx=12)
            e.insert(0, str(default))
            self.entries[key] = e
        
        # 提示
        tip_line = tb.Frame(scrollable)
        tip_line.pack(pady=8)
        tb.Label(tip_line, text="💡 正常工时 = (白班天数 + 夜班天数) × 8 小时（系统自动计算）",
                 font=("Segoe UI",9), foreground="#6c757d").pack()
        
        # 5. 按钮
        btn_frame = tb.Frame(scrollable)
        btn_frame.pack(pady=20)
        tb.Button(btn_frame, text="计算薪酬", command=self.calculate,
                  bootstyle="success", width=15).pack(side=LEFT, padx=10)
        tb.Button(btn_frame, text="填充示例", command=self.fill_example,
                  bootstyle="info", width=12).pack(side=LEFT, padx=10)
        tb.Button(btn_frame, text="清空数据", command=self.clear_all,
                  bootstyle="secondary", width=10).pack(side=LEFT, padx=10)
        
        # 6. 结果展示区域（双表格，收入明细带计算式）
        result_card = tb.Labelframe(scrollable, text="📄 薪酬明细", padding=10, bootstyle="dark")
        result_card.pack(fill=BOTH, expand=YES, pady=12)
        
        table_frame = tb.Frame(result_card)
        table_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # 收入表格（增加“计算说明”列或直接在项目名称中体现）
        income_frame = tb.Labelframe(table_frame, text="收入项目明细（含计算过程）", bootstyle="success", padding=8)
        income_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=5)
        # 三列：项目、金额、计算式
        self.income_tree = ttk.Treeview(income_frame, columns=("项目", "金额", "计算式"), show="headings", height=10)
        self.income_tree.heading("项目", text="项目")
        self.income_tree.heading("金额", text="金额 (元)")
        self.income_tree.heading("计算式", text="计算过程")
        self.income_tree.column("项目", width=130)
        self.income_tree.column("金额", width=100)
        self.income_tree.column("计算式", width=200)
        self.income_tree.pack(fill=BOTH, expand=YES)
        
        # 扣款表格
        deduction_frame = tb.Labelframe(table_frame, text="扣款项目明细", bootstyle="danger", padding=8)
        deduction_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=5)
        self.deduction_tree = ttk.Treeview(deduction_frame, columns=("项目", "金额"), show="headings", height=10)
        self.deduction_tree.heading("项目", text="项目")
        self.deduction_tree.heading("金额", text="金额 (元)")
        self.deduction_tree.column("项目", width=150)
        self.deduction_tree.column("金额", width=120)
        self.deduction_tree.pack(fill=BOTH, expand=YES)
        
        # 底部汇总
        summary_frame = tb.Frame(result_card)
        summary_frame.pack(fill=X, pady=10)
        self.gross_label = tb.Label(summary_frame, text="应发合计：0.00 元", font=("Segoe UI",12,"bold"))
        self.gross_label.pack(side=LEFT, padx=20)
        self.net_label = tb.Label(summary_frame, text="实发工资：0.00 元", font=("Segoe UI",16,"bold"), foreground="#28a745")
        self.net_label.pack(side=RIGHT, padx=20)
    
    def update_work_info(self):
        try:
            y = int(self.year_var.get())
            m = int(self.month_var.get())
            info = self.get_work_info(y, m)
            std_hours = info['work_days'] * 8
            text = f"{y}年{m}月 标准考勤\n"
            text += f"总天数 {info['total_days']}天  |  工作日 {info['work_days']}天  |  周末 {info['weekend_days']}天  |  法定节假日 {info['holiday_days']}天\n"
            text += f"标准应出勤工时 {std_hours}小时\n"
            text += f"法定节假日明细：{', '.join(info['holiday_list']) if info['holiday_list'] else '无'}"
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, text)
        except:
            pass
    
    def fill_example(self):
        example_values = {
            'base': 2030, 'perf': 400, 'meal': 400, 'full': 100,
            'social': 432, 'fund': 300,
            'day_days': 15, 'night_days': 5, 'overtime_hours': 10, 'holiday_hours': 8
        }
        for key, val in example_values.items():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, str(val))
    
    def clear_all(self):
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, "0")
        for row in self.income_tree.get_children():
            self.income_tree.delete(row)
        for row in self.deduction_tree.get_children():
            self.deduction_tree.delete(row)
        self.gross_label.config(text="应发合计：0.00 元")
        self.net_label.config(text="实发工资：0.00 元")
    
    def calculate(self):
        try:
            y = int(self.year_var.get())
            m = int(self.month_var.get())
            info = self.get_work_info(y, m)
            
            base = float(self.entries['base'].get())
            perf = float(self.entries['perf'].get())
            meal = float(self.entries['meal'].get())
            full = float(self.entries['full'].get())
            social = float(self.entries['social'].get())
            fund = float(self.entries['fund'].get())
            day_days = float(self.entries['day_days'].get())
            night_days = float(self.entries['night_days'].get())
            overtime_hours = float(self.entries['overtime_hours'].get())
            holiday_hours = float(self.entries['holiday_hours'].get())
            
            # 正常工时 = (白班+夜班) × 8
            normal_hours = (day_days + night_days) * 8
            # 白班部分和夜班部分分开计算（用于展示）
            day_work_hours = day_days * 8
            night_work_hours = night_days * 8
            
            day_work_pay = day_work_hours * self.normal_rate
            night_work_pay = night_work_hours * self.normal_rate
            # 常规加班费
            overtime_pay = overtime_hours * self.normal_rate
            # 节假日加班费
            holiday_pay = holiday_hours * self.holiday_rate
            # 补贴
            day_allowance = day_days * self.day_allowance
            night_allowance = night_days * self.night_allowance
            
            # 收入明细（带计算式）
            income_items = [
                ("底薪", base, "固定"),
                ("绩效奖金", perf, "固定"),
                ("餐补", meal, "固定"),
                ("全勤奖", full, "固定"),
                ("白班工时工资", day_work_pay, f"{day_days}天 × 8小时/天 × {self.normal_rate}元/小时"),
                ("夜班工时工资", night_work_pay, f"{night_days}天 × 8小时/天 × {self.normal_rate}元/小时"),
                ("常规加班费", overtime_pay, f"{overtime_hours}小时 × {self.normal_rate}元/小时"),
                ("节假日加班费", holiday_pay, f"{holiday_hours}小时 × {self.holiday_rate}元/小时"),
                ("白班补贴", day_allowance, f"{day_days}天 × {self.day_allowance}元/天"),
                ("夜班补贴", night_allowance, f"{night_days}天 × {self.night_allowance}元/天"),
            ]
            gross = sum(v for _, v, _ in income_items)
            
            # 扣款明细
            deduction_items = [
                ("社保个人部分", social),
                ("公积金个人部分", fund),
            ]
            total_deduction = sum(v for _, v in deduction_items)
            net = gross - total_deduction
            
            # 刷新收入表格
            for row in self.income_tree.get_children():
                self.income_tree.delete(row)
            for name, amount, formula in income_items:
                self.income_tree.insert("", "end", values=(name, f"{amount:.2f}", formula))
            
            # 刷新扣款表格
            for row in self.deduction_tree.get_children():
                self.deduction_tree.delete(row)
            for name, amount in deduction_items:
                self.deduction_tree.insert("", "end", values=(name, f"{amount:.2f}"))
            
            self.gross_label.config(text=f"应发合计：{gross:.2f} 元")
            self.net_label.config(text=f"实发工资：{net:.2f} 元", foreground="#28a745" if net >= 0 else "#dc3545")
            
        except Exception as e:
            messagebox.showerror("输入错误", f"请检查所有数据是否正确填写\n{str(e)}")

if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    AdvancedSalaryCalculator(app)
    app.mainloop()