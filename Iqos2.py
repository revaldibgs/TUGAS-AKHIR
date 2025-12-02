import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("Agg")
import csv, os
from datetime import datetime
import webbrowser

# ===================== BACKEND =====================
class RunningAnalysis:
    def __init__(self, name, distance, time, heart_rate):
        self.name = name
        self.distance = distance
        self.time = time
        self.heart_rate = heart_rate

    def calculate_pace(self):
        try:
            pace = self.time / self.distance
            if pace <= 4: category = "Elite Pace"
            elif pace <= 6: category = "Strong Training Pace"
            elif pace <= 8: category = "Comfortable Pace"
            else: category = "Easy Jogging Pace"
            return pace, category
        except ZeroDivisionError:
            return 0, "Invalid"

    def calorie_burn(self): return round(self.distance*60)

    def heart_zone(self):
        if self.heart_rate < 100: return "Very Light Zone (Recovery)"
        elif self.heart_rate < 130: return "Light Zone (Fat Burning)"
        elif self.heart_rate < 150: return "Moderate Zone (Aerobic)"
        elif self.heart_rate < 170: return "Hard Zone (Anaerobic)"
        else: return "Maximum Effort Zone"

    def vo2max_estimate(self):
        pace,_ = self.calculate_pace()
        vo2 = round(15*(self.distance/(self.time/60))/(self.heart_rate/100),1)
        return vo2

    def vo2max_category(self):
        vo2 = self.vo2max_estimate()
        if vo2 < 30: return "Poor"
        elif vo2 <= 38: return "Below Average"
        elif vo2 <= 45: return "Average"
        elif vo2 <= 52: return "Good"
        elif vo2 <= 60: return "Excellent"
        else: return "Elite"

    def coaching_feedback(self):
        pace,_ = self.calculate_pace()
        tips=[]
        if pace<=5 and self.heart_rate>=165: tips.append("- Pace cepat, HR tinggi → turunkan intensitas.")
        if pace>8 and self.heart_rate<120: tips.append("- Lari santai, pertimbangkan naikkan ritme.")
        if self.heart_rate>=150: tips.append("- Zona anaerob → fokus pernapasan.")
        if 120<=self.heart_rate<=145 and 6<=pace<=7.5: tips.append("- Ritme stabil, ideal untuk long run.")
        if self.distance<2 and self.heart_rate>170: tips.append("- Pemanasan kurang, tingkatkan pemanasan.")
        if not tips: tips.append("- Latihan stabil. Pertahankan ritme saat ini.")
        return "\n".join(tips)

    def coach_mode(self, mode="balanced"):
        pace,_ = self.calculate_pace(); hr=self.heart_rate
        if mode=="extrim":
            plan=[
                "Day1: Interval Sprint 8×400m",
                "Day2: Tempo Run 6 km",
                "Day3: Recovery Jog 3 km",
                "Day4: Long Run 12 km",
                "Day5: Rest",
                "Day6: Hill Repeats 6×100 m",
                "Day7: Free Choice Run"
            ]
        elif pace<=5 and hr>=160:
            plan=[
                "Day1: Easy Run 3 km",
                "Day2: Interval 6×400 m",
                "Day3: Recovery Jog 2 km",
                "Day4: Tempo Run 4 km",
                "Day5: Rest",
                "Day6: Long Run 8–10 km",
                "Day7: Free Choice Run"
            ]
        elif pace<=7:
            plan=[
                "Day1: Easy Run 2–3 km",
                "Day2: Tempo Run 3 km",
                "Day3: Light Jog 2 km",
                "Day4: Interval 4×400 m",
                "Day5: Rest",
                "Day6: Long Run 6–7 km",
                "Day7: Brisk Walk / Light Jog"
            ]
        else:
            plan=[
                "Day1: Walk-Jog 2 km",
                "Day2: Easy Run 2 km",
                "Day3: Rest or Stretching",
                "Day4: Easy Run 2–3 km",
                "Day5: Rest",
                "Day6: Long Run 4–5 km",
                "Day7: Light Jog"
            ]
        return "\n".join(plan)

    def summary(self):
        pace,_ = self.calculate_pace()
        return (
            f"Nama: {self.name}\nJarak: {self.distance} km\nWaktu: {self.time} menit\n"
            f"Pace: {pace:.2f} menit/km\nZona HR: {self.heart_zone()}\n"
            f"Kalori: {self.calorie_burn()} kcal\nVO₂max: {self.vo2max_estimate()} ml/kg/min ({self.vo2max_category()})\n\n"
            f"AI Personal Trainer Feedback:\n{self.coaching_feedback()}\n\n"
            f"Coach Mode (7 Hari):\n{self.coach_mode()}"
        )

# ===================== GUI =====================
class IQOSApp:
    def __init__(self, root):
        self.root=root
        self.root.title("IQOS - Intelligent Quantified Output for Sports")
        self.root.geometry("1024x650")
        self.theme="dark"
        self.set_theme()
        self.history_file="iqos_history.csv"

        # Header
        header=tk.Frame(root,bg=self.bg_color)
        header.pack(fill="x",pady=5)
        tk.Label(header,text="IQOS - Running Performance Analyzer",fg=self.orange,
                 bg=self.bg_color,font=("Segoe UI Black",20)).pack(side="left",padx=20)
        self.create_top_button(header,"Toggle Theme",self.toggle_theme)
        self.create_top_button(header,"Project Mbappé",self.project_mbappe)
        self.create_top_button(header,"Load / Compare",self.load_compare)

        # Main container
        container=tk.Frame(root,bg=self.bg_color)
        container.pack(expand=True,fill="both",pady=10)

        # Sidebar Input
        sidebar=tk.Frame(container,bg=self.bg_color)
        sidebar.pack(side="left",fill="y",padx=15)

        self.name=self.create_input(sidebar,"Nama Pelari:")
        self.distance=self.create_input(sidebar,"Jarak (km):")
        self.time=self.create_input(sidebar,"Waktu (menit):")
        self.heartrate=self.create_input(sidebar,"Detak Jantung (bpm):")

        self.create_button(sidebar,"Analisis",self.run_analysis)
        self.create_button(sidebar,"Save Session",self.save_session)

        # Panel Output
        self.panel=tk.Frame(container,bg="#2C2C2C")
        self.panel.pack(side="right",expand=True,fill="both",padx=15)
        tk.Label(self.panel,text="Hasil Analisis IQOS",font=("Segoe UI Black",14),
                 bg="#2C2C2C",fg=self.orange).pack(pady=10)
        self.output=tk.Label(self.panel,text="Belum ada data.",bg="#2C2C2C",fg="white",
                             justify="left",anchor="nw",wraplength=400,font=("Consolas",11))
        self.output.pack(padx=10,pady=10,fill="both",expand=True)

        # Graph
        self.graph_frame=tk.Frame(self.panel,bg="#2C2C2C")
        self.graph_frame.pack(fill="both",expand=True,pady=10)

    # ===================== THEME =====================
    def set_theme(self):
        self.orange="#FF8C42"
        if self.theme=="dark": self.bg_color="#1E1E1E"; self.fg_color="white"
        else: self.bg_color="white"; self.fg_color="black"
        self.root.configure(bg=self.bg_color)

    def toggle_theme(self):
        self.theme="light" if self.theme=="dark" else "dark"
        self.set_theme()
        messagebox.showinfo("Theme",f"Mode {self.theme} aktif!")

    # ===================== INPUT & BUTTON =====================
    def create_input(self,parent,text):
        ttk.Label(parent,text=text).pack(anchor="w",pady=(5,0))
        entry=ttk.Entry(parent,width=25)
        entry.pack(pady=(0,5))
        return entry

    def create_button(self,parent,text,command):
        btn=ttk.Button(parent,text=text,command=command)
        btn.pack(pady=10,fill="x")
        return btn

    def create_top_button(self,parent,text,command):
        btn=tk.Button(parent,text=text,command=command,bg=self.orange,fg="black")
        btn.pack(side="left",padx=5)
        return btn

    # ===================== ANALYSIS =====================
    def run_analysis(self):
        try:
            name=self.name.get()
            distance=float(self.distance.get())
            time=float(self.time.get())
            heart=int(self.heartrate.get())
            self.runner=RunningAnalysis(name,distance,time,heart)
            self.output.config(text=self.runner.summary())
            self.show_graph(distance,time)
        except ValueError:
            messagebox.showerror("Error","Masukkan angka yang valid.")

    # ===================== GRAPH =====================
    def show_graph(self,distance,time):
        for widget in self.graph_frame.winfo_children(): widget.destroy()
        fig=Figure(figsize=(5,2.5),dpi=100)
        ax=fig.add_subplot(111)
        km_list=list(range(1,int(distance)+1))
        pace_list=[time/distance]*len(km_list)
        ax.plot(km_list,pace_list,marker='o',color=self.orange,linewidth=2)
        ax.fill_between(km_list,pace_list, [0]*len(km_list), color=self.orange, alpha=0.1)
        ax.set_title("Grafik Pace per Kilometer")
        ax.set_xlabel("Kilometer")
        ax.set_ylabel("Pace (menit/km)")
        ax.grid(True,alpha=0.3)
        canvas=FigureCanvasTkAgg(fig,master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both",expand=True)

    # ===================== SAVE & COMPARE =====================
    def save_session(self):
        if not hasattr(self,"runner"):
            messagebox.showwarning("Warning","Jalankan analisis dulu!")
            return
        headers=["Timestamp","Nama","Distance","Time","HeartRate","VO2max","VO2maxCategory","Calories","Pace"]
        data=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              self.runner.name,self.runner.distance,self.runner.time,
              self.runner.heart_rate,self.runner.vo2max_estimate(),
              self.runner.vo2max_category(),
              self.runner.calorie_burn(),round(self.runner.time/self.runner.distance,2)]
        file_exists=os.path.isfile("iqos_history.csv")
        with open("iqos_history.csv","a",newline="") as f:
            writer=csv.writer(f)
            if not file_exists: writer.writerow(headers)
            writer.writerow(data)
        messagebox.showinfo("Saved","Sesi berhasil disimpan!")

    def load_compare(self):
        if not os.path.isfile("iqos_history.csv"):
            messagebox.showwarning("Warning","Belum ada history tersimpan!")
            return
        with open("iqos_history.csv","r") as f: reader=list(csv.reader(f))
        sessions=reader[1:]
        if not sessions: messagebox.showwarning("Warning","Belum ada session tersimpan!"); return
        messagebox.showinfo("History","Session terakhir:\n"+str(sessions[-1]))

    # ===================== PROJECT MBAPPE =====================
    def project_mbappe(self): webbrowser.open("https://www.instagram.com/revaldibgs_/")

# ===================== MAIN =====================
root=tk.Tk()
app=IQOSApp(root)
root.mainloop()
