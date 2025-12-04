import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("Agg")
import csv, os, json
from datetime import datetime, timedelta
import webbrowser
from functools import lru_cache
import numpy as np
from collections import deque
import random

# ===================== BACKEND ENHANCED =====================
class RunningAnalysisEnhanced:
    def __init__(self, name, distance, time, heart_rate, age=None, weight=None):
        self.name = name
        self.distance = float(distance)
        self.time = float(time)
        self.heart_rate = int(heart_rate)
        self.age = int(age) if age else None
        self.weight = float(weight) if weight else None
        self.timestamp = datetime.now()
        # ini tipe data
        # tambah private encaplution
    def calculate_pace(self):
        try:
            if self.distance <= 0:
                return 0, "Invalid Distance"
            
            pace = self.time / self.distance
            if pace <= 4: category = "Elite Pace"
            elif pace <= 6: category = "Strong Training Pace"
            elif pace <= 8: category = "Comfortable Pace"
            else: category = "Easy Jogging Pace"
            return pace, category
        except (ZeroDivisionError, TypeError):
            return 0, "Invalid"
        # ini array
    @lru_cache(maxsize=128)
    def calculate_pace_cached(self, distance, time):
        try:
            return time / distance
        except ZeroDivisionError:
            return 0

    def calorie_burn(self):
        try:
            if self.weight:
                pace, _ = self.calculate_pace()
                met = 8 * (pace / 6) if pace > 0 else 5
                return round(met * self.weight * (self.time / 60))
            return round(self.distance * 60)
        except:
            return round(self.distance * 60)

    def heart_zone(self):
        try:
            max_hr = self._estimate_max_hr()
            zones = self.calculate_training_zones(max_hr)
            current_hr = self.heart_rate
            
            for zone_name, (min_hr, max_hr_zone) in zones.items():
                if min_hr <= current_hr <= max_hr_zone:
                    return zone_name, (min_hr, max_hr_zone)
            return "Unknown Zone", (0, 0)
        except:
            return "Error Calculating", (0, 0)

    def _estimate_max_hr(self):
        try:
            if self.age:
                return 220 - self.age
            return 220 - 30
        except:
            return 190

    def calculate_training_zones(self, max_hr=None):
        try:
            if not max_hr:
                max_hr = self._estimate_max_hr()
            
            return {
                "Recovery Zone": (int(0.6 * max_hr), int(0.7 * max_hr)),
                "Aerobic Zone": (int(0.7 * max_hr), int(0.8 * max_hr)),
                "Threshold Zone": (int(0.8 * max_hr), int(0.9 * max_hr)),
                "VO2 Max Zone": (int(0.9 * max_hr), int(1.0 * max_hr))
            }
        except:
            return {
                "Recovery Zone": (114, 133),
                "Aerobic Zone": (133, 152),
                "Threshold Zone": (152, 171),
                "VO2 Max Zone": (171, 190)
            }

    def vo2max_estimate(self):
        try:
            pace, _ = self.calculate_pace()
            if pace <= 0 or self.heart_rate <= 0:
                return 0
            vo2 = round(15 * (self.distance / (self.time / 60)) / (self.heart_rate / 100), 1)
            return max(vo2, 0)
        except:
            return 0

    def vo2max_category(self):
        vo2 = self.vo2max_estimate()
        if vo2 < 30: return "Poor"
        elif vo2 <= 38: return "Below Average"
        elif vo2 <= 45: return "Average"
        elif vo2 <= 52: return "Good"
        elif vo2 <= 60: return "Excellent"
        else: return "Elite"

    def coaching_feedback(self):
        try:
            pace, _ = self.calculate_pace()
            tips = []
            
            if pace <= 5 and self.heart_rate >= 165: 
                tips.append("- Pace cepat, HR tinggi → turunkan intensitas.")
            if pace > 8 and self.heart_rate < 120: 
                tips.append("- Lari santai, pertimbangkan naikkan ritme.")
            if self.heart_rate >= 150: 
                tips.append("- Zona anaerob → fokus pernapasan.")
            if 120 <= self.heart_rate <= 145 and 6 <= pace <= 7.5: 
                tips.append("- Ritme stabil, ideal untuk long run.")
            if self.distance < 2 and self.heart_rate > 170: 
                tips.append("- Pemanasan kurang, tingkatkan pemanasan.")
            if not tips: 
                tips.append("- Latihan stabil. Pertahankan ritme saat ini.")
            return "\n".join(tips)
        except:
            return "- Data tidak cukup untuk analisis."

    def coach_mode(self, mode="balanced"):
        try:
            pace, _ = self.calculate_pace()
            hr = self.heart_rate
            
            if mode == "extrim":
                plan = [
                    "Day1: Interval Sprint 8×400m",
                    "Day2: Tempo Run 6 km",
                    "Day3: Recovery Jog 3 km",
                    "Day4: Long Run 12 km",
                    "Day5: Rest",
                    "Day6: Hill Repeats 6×100 m",
                    "Day7: Free Choice Run"
                ]
            elif pace <= 5 and hr >= 160:
                plan = [
                    "Day1: Easy Run 3 km",
                    "Day2: Interval 6×400 m",
                    "Day3: Recovery Jog 2 km",
                    "Day4: Tempo Run 4 km",
                    "Day5: Rest",
                    "Day6: Long Run 8–10 km",
                    "Day7: Free Choice Run"
                ]
            elif pace <= 7:
                plan = [
                    "Day1: Easy Run 2–3 km",
                    "Day2: Tempo Run 3 km",
                    "Day3: Light Jog 2 km",
                    "Day4: Interval 4×400 m",
                    "Day5: Rest",
                    "Day6: Long Run 6–7 km",
                    "Day7: Brisk Walk / Light Jog"
                ]
            else:
                plan = [
                    "Day1: Walk-Jog 2 km",
                    "Day2: Easy Run 2 km",
                    "Day3: Rest or Stretching",
                    "Day4: Easy Run 2–3 km",
                    "Day5: Rest",
                    "Day6: Long Run 4–5 km",
                    "Day7: Light Jog"
                ]
            return "\n".join(plan)
        except:
            return "Tidak dapat generate training plan."

    # ===================== FITUR TRAINING PLAN LENGKAP =====================
    def generate_training_plan(self, goal="5k", weeks=8, level="beginner"):
        try:
            plans = {
                "5k": {
                    "beginner": self._5k_beginner_plan(weeks),
                    "intermediate": self._5k_intermediate_plan(weeks),
                    "advanced": self._5k_advanced_plan(weeks)
                },
                "10k": {
                    "beginner": self._10k_beginner_plan(weeks),
                    "intermediate": self._10k_intermediate_plan(weeks),
                    "advanced": self._10k_advanced_plan(weeks)
                },
                "half_marathon": {
                    "beginner": self._half_marathon_beginner_plan(weeks),
                    "intermediate": self._half_marathon_intermediate_plan(weeks),
                    "advanced": self._half_marathon_advanced_plan(weeks)
                },
                "marathon": {
                    "beginner": self._marathon_beginner_plan(weeks),
                    "intermediate": self._marathon_intermediate_plan(weeks),
                    "advanced": self._marathon_advanced_plan(weeks)
                }
            }
            return plans.get(goal, {}).get(level, self._maintenance_plan())
        except:
            return self._maintenance_plan()

    def _5k_beginner_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 2:
                plan.append(f"Week {week}: Run 2km × 3, Walk 1km × 2")
            elif week <= 4:
                plan.append(f"Week {week}: Run 3km × 3, Walk 1km × 1")
            elif week <= 6:
                plan.append(f"Week {week}: Run 4km × 3, Interval 400m × 4")
            else:
                plan.append(f"Week {week}: Run 5km × 2, Tempo 3km × 1")
        return plan
    # parameter jelasin
    def _5k_intermediate_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 3:
                plan.append(f"Week {week}: Run 5km × 3, Tempo 3km × 1")
            elif week <= 6:
                plan.append(f"Week {week}: Run 6km × 2, Interval 800m × 6, Long Run 8km")
            else:
                plan.append(f"Week {week}: Speed work 8×400m, Tempo 5km, Long Run 10km")
        return plan

    def _5k_advanced_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 4:
                plan.append(f"Week {week}: Interval training + Hill repeats")
            else:
                plan.append(f"Week {week}: High intensity intervals + Long tempo runs")
        return plan

    def _10k_beginner_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 4:
                plan.append(f"Week {week}: Build from 3km to 6km")
            elif week <= 8:
                plan.append(f"Week {week}: Long runs up to 8km + tempo")
            else:
                plan.append(f"Week {week}: 10km practice + recovery")
        return plan

    def _10k_intermediate_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: Mixed intervals, tempo, long runs (8-12km)")
        return plan

    def _10k_advanced_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: Advanced intervals, hill repeats, pace work")
        return plan

    def _half_marathon_beginner_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 8:
                plan.append(f"Week {week}: Gradual build up to 15km")
            else:
                plan.append(f"Week {week}: Taper week + 21km practice")
        return plan

    def _half_marathon_intermediate_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: Structured training with speed endurance")
        return plan

    def _half_marathon_advanced_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: High mileage + quality workouts")
        return plan

    def _marathon_beginner_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            if week <= 16:
                plan.append(f"Week {week}: Build phase up to 32km")
            else:
                plan.append(f"Week {week}: Taper + marathon preparation")
        return plan

    def _marathon_intermediate_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: Balanced mileage + speed work")
        return plan

    def _marathon_advanced_plan(self, weeks):
        plan = []
        for week in range(1, weeks + 1):
            plan.append(f"Week {week}: High intensity + peak performance")
        return plan

    def _maintenance_plan(self):
        return [
            "Week 1: Variety maintenance workouts",
            "Week 2: Focus on consistency",
            "Week 3: Intensity modulation", 
            "Week 4: Active recovery focus",
            "Week 5: Technique refinement",
            "Week 6: Endurance building",
            "Week 7: Speed development",
            "Week 8: Recovery and assessment"
        ]

    # ===================== FITUR PREDIKSI RACE =====================
    def predict_race_times(self):
        try:
            pace, _ = self.calculate_pace()
            if pace <= 0:
                return {
                    "5k": "N/A",
                    "10k": "N/A", 
                    "Half Marathon": "N/A",
                    "Marathon": "N/A"
                }
                
            return {
                "5k": f"{pace * 5:.1f} menit",
                "10k": f"{pace * 10 * 1.08:.1f} menit",
                "Half Marathon": f"{pace * 21.1 * 1.15:.1f} menit",
                "Marathon": f"{pace * 42.2 * 1.25:.1f} menit"
            }
        except:
            return {
                "5k": "N/A",
                "10k": "N/A",
                "Half Marathon": "N/A", 
                "Marathon": "N/A"
            }

    # ===================== FITUR INSIGHTS & ACHIEVEMENTS =====================
    def generate_insights(self):
        try:
            insights = []
            pace, _ = self.calculate_pace()
            hr_zone, _ = self.heart_zone()
            
            # Performance insights
            if self.heart_rate > 170 and pace > 7:
                insights.append("🚨 HIGH EFFORT, LOW PACE - Mungkin butuh recovery")
            elif self.heart_rate < 120 and pace < 6:
                insights.append("💪 EFFICIENT RUNNING - Kondisi fisik baik")
            
            if self.distance > 15:
                insights.append("🏃 LONG RUN COMPLETED - Pastikan recovery cukup")
            
            # VO2Max based insights
            vo2 = self.vo2max_estimate()
            if vo2 < 35:
                insights.append("📈 FOKUS: Build aerobic base dengan easy runs")
            elif vo2 > 50:
                insights.append("⚡ POTENSI: Bisa coba intensitas lebih tinggi")
            
            # Pace insights
            if pace < 5:
                insights.append("🎯 PACING: Excellent speed maintenance")
            elif pace > 8:
                insights.append("🐢 PACING: Consider speed work improvements")
                
            return insights if insights else ["- Data menunjukkan performa normal."]
        except:
            return ["- Tidak dapat menganalisis data."]

    def get_achievements(self):
        try:
            achievements = []
            pace, _ = self.calculate_pace()
            
            # Distance achievements
            if self.distance >= 5:
                achievements.append("🏆 First 5K!")
            if self.distance >= 10:
                achievements.append("🎯 10K Runner!")
            if self.distance >= 21.1:
                achievements.append("🥈 Half Marathon Finisher!")
            if self.distance >= 42.2:
                achievements.append("🥇 Marathon Finisher!")
                
            # Speed achievements
            if pace <= 5:
                achievements.append("⚡ Speed Demon!")
            elif pace <= 6:
                achievements.append("🚀 Fast Runner!")
                
            # VO2Max achievements
            vo2 = self.vo2max_estimate()
            if vo2 >= 50:
                achievements.append("💪 Excellent Fitness!")
            elif vo2 >= 45:
                achievements.append("👍 Good Fitness!")
                
            # Consistency achievements
            if self.time > 60:
                achievements.append("⏱️ Endurance Runner!")
                
            return achievements if achievements else ["- Keep running untuk mendapatkan achievements!"]
        except:
            return ["- Achievements tidak tersedia."]

    def get_performance_score(self):
        """Memberikan skor performa 0-100"""
        try:
            score = 0
            pace, _ = self.calculate_pace()
            vo2 = self.vo2max_estimate()
            
            # Pace score (40%)
            if pace <= 4: score += 40
            elif pace <= 5: score += 35
            elif pace <= 6: score += 30
            elif pace <= 7: score += 25
            elif pace <= 8: score += 20
            else: score += 15
            
            # VO2Max score (30%)
            if vo2 >= 55: score += 30
            elif vo2 >= 50: score += 25
            elif vo2 >= 45: score += 20
            elif vo2 >= 40: score += 15
            elif vo2 >= 35: score += 10
            else: score += 5
            
            # Distance score (20%)
            if self.distance >= 21: score += 20
            elif self.distance >= 15: score += 15
            elif self.distance >= 10: score += 10
            elif self.distance >= 5: score += 5
            
            # Heart rate efficiency (10%)
            if self.heart_rate < 140 and pace < 6: score += 10
            elif self.heart_rate < 160: score += 7
            else: score += 5
            
            return min(score, 100)
        except:
            return 0

    def summary(self):
        try:
            pace, pace_cat = self.calculate_pace()
            hr_zone, hr_range = self.heart_zone()
            insights = self.generate_insights()
            achievements = self.get_achievements()
            race_predictions = self.predict_race_times()
            performance_score = self.get_performance_score()

            summary_text = (
                f"🏃 ANALISIS LARI - {self.name}\n"
                f"{'='*50}\n"
                f"📊 Data Dasar:\n"
                f"• Jarak: {self.distance} km\n"
                f"• Waktu: {self.time} menit\n"
                f"• Pace: {pace:.2f} menit/km ({pace_cat})\n"
                f"• Detak Jantung: {self.heart_rate} bpm\n"
                f"• Zona HR: {hr_zone} {hr_range}\n\n"
                
                f"🔥 Metrics Lanjutan:\n"
                f"• Kalori Terbakar: {self.calorie_burn()} kcal\n"
                f"• VO₂max: {self.vo2max_estimate()} ml/kg/min ({self.vo2max_category()})\n"
                f"• Skor Performa: {performance_score}/100\n\n"
                
                f"🏆 Achievements ({len(achievements)}):\n" + "\n".join(achievements) + "\n\n"
                
                f"📈 Race Predictions:\n"
                f"• 5K: {race_predictions['5k']}\n"
                f"• 10K: {race_predictions['10k']}\n"
                f"• Half Marathon: {race_predictions['Half Marathon']}\n"
                f"• Marathon: {race_predictions['Marathon']}\n\n"
                
                f"💡 AI Insights:\n" + "\n".join(insights) + "\n\n"
                
                f"👨‍🏫 Personal Trainer Feedback:\n{self.coaching_feedback()}\n\n"
                
                f"📅 Recommended Training Plan (7 Hari):\n{self.coach_mode()}\n\n"
                
                f"🕒 Analisis dibuat: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return summary_text
        except Exception as e:
            return f"Error generating summary: {str(e)}"

# ===================== SESSION MANAGER =====================
class SessionManager:
    def __init__(self, history_file="iqos_history.csv"):
        self.history_file = history_file
        self.sessions = []
        self.load_sessions()

    def load_sessions(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.sessions = list(reader)
            except:
                self.sessions = []

    def add_session(self, session_data):
        self.sessions.append(session_data)
        self.save_sessions()

    def save_sessions(self):
        try:
            if self.sessions:
                with open(self.history_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.sessions[0].keys())
                    writer.writeheader()
                    writer.writerows(self.sessions)
        except Exception as e:
            print(f"Error saving sessions: {e}")

    def get_recent_sessions(self, count=10):
        return self.sessions[-count:] if self.sessions else []
        # setter getter

    def compare_sessions(self, session_ids):
        comparison_data = []
        for session_id in session_ids:
            if session_id < len(self.sessions):
                session = self.sessions[session_id]
                comparison_data.append({
                    'date': session.get('Timestamp', 'N/A'),
                    'distance': float(session.get('Distance', 0)),
                    'time': float(session.get('Time', 0)),
                    'pace': float(session.get('Pace', 0)),
                    'vo2max': float(session.get('VO2max', 0)),
                    'calories': session.get('Calories', '0')
                })
        return comparison_data

    def get_progress_trend(self, metric='VO2max'):
        metrics = []
        dates = []
        for session in self.sessions[-10:]:
            if metric in session:
                try:
                    metrics.append(float(session[metric]))
                    dates.append(session['Timestamp'][:10])
                except (ValueError, KeyError):
                    continue
        return dates, metrics

    def get_statistics(self):
        if not self.sessions:
            return {}
        
        distances = [float(s.get('Distance', 0)) for s in self.sessions]
        paces = [float(s.get('Pace', 0)) for s in self.sessions]
        vo2max_scores = [float(s.get('VO2max', 0)) for s in self.sessions]
        
        return {
            'total_sessions': len(self.sessions),
            'avg_distance': sum(distances) / len(distances),
            'avg_pace': sum(paces) / len(paces),
            'avg_vo2max': sum(vo2max_scores) / len(vo2max_scores),
            'best_pace': min(paces),
            'longest_run': max(distances),
            'total_distance': sum(distances)
        }

# ===================== ENHANCED GUI DENGAN SEMUA FITUR =====================
class IQOSAppEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("IQOS PRO - Intelligent Quantified Output for Sports")
        self.root.geometry("1300x900")
        self.theme = "dark"
        self.session_manager = SessionManager()
        self.set_theme()
        
        self.current_data = {}
        self.history_data = []
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_color, height=70)
        header.pack(fill="x", pady=5)
        header.pack_propagate(False)
        
        tk.Label(header, text="🏃 IQOS PRO - Running Performance Analyzer", 
                fg=self.orange, bg=self.bg_color, 
                font=("Segoe UI Black", 18)).pack(side="left", padx=20)
        
        # Top buttons dengan semua fitur
        button_frame = tk.Frame(header, bg=self.bg_color)
        button_frame.pack(side="right", padx=20)
        
        buttons = [
            ("Toggle Theme", self.toggle_theme),
            ("Project Mbappé", self.project_mbappe),
            ("Progress Trend", self.show_progress_trend),
            ("Statistics", self.show_statistics),
            ("Training Plans", self.show_training_plans),
            ("Export Data", self.export_data),
            ("Compare", self.show_comparison)
        ]
        
        for text, command in buttons:
            self.create_top_button(button_frame, text, command)

        # Main container dengan notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Semua tabs
        self.setup_main_tab()
        self.setup_history_tab()
        self.setup_training_tab()
        self.setup_statistics_tab()
        self.setup_comparison_tab()

    def setup_main_tab(self):
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="🏠 Main Analysis")
        
        main_container = tk.Frame(self.main_tab, bg=self.bg_color)
        main_container.pack(expand=True, fill="both")

        # Sidebar Input
        sidebar = tk.Frame(main_container, bg=self.bg_color, width=320)
        sidebar.pack(side="left", fill="y", padx=15)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📝 Input Data Lari", font=("Segoe UI", 14, "bold"),
                bg=self.bg_color, fg=self.orange).pack(pady=(10, 20))

        # Input fields dengan default values
        self.name = self.create_input(sidebar, "Nama Pelari:")
        self.name.insert(0, "John Runner")
        
        self.distance = self.create_input(sidebar, "Jarak (km):")
        self.distance.insert(0, "5")
        
        self.time = self.create_input(sidebar, "Waktu (menit):")
        self.time.insert(0, "30")
        
        self.heartrate = self.create_input(sidebar, "Detak Jantung (bpm):")
        self.heartrate.insert(0, "150")
        
        self.age = self.create_input(sidebar, "Usia (tahun, opsional):")
        self.age.insert(0, "25")
        
        self.weight = self.create_input(sidebar, "Berat Badan (kg, opsional):")
        self.weight.insert(0, "70")

        # Action buttons
        self.create_button(sidebar, "🚀 Analisis Lengkap", self.run_analysis)
        self.create_button(sidebar, "⚡ Quick Analysis", self.quick_analysis)
        self.create_button(sidebar, "💾 Save Session", self.save_session)
        self.create_button(sidebar, "🗑️ Clear Input", self.clear_input)
        self.create_button(sidebar, "🔄 Load Last Session", self.load_last_session)

        # Panel Output
        output_frame = tk.Frame(main_container, bg="#2C2C2C")
        output_frame.pack(side="right", expand=True, fill="both", padx=15)

        # Output area dengan scrollbar
        output_container = tk.Frame(output_frame, bg="#2C2C2C")
        output_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_text = tk.Text(output_container, bg="#2C2C2C", fg="white", 
                                 font=("Consolas", 10), wrap="word", height=20)
        scrollbar = ttk.Scrollbar(output_container, orient="vertical", 
                                command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Graph Frame
        self.graph_frame = tk.Frame(output_frame, bg="#2C2C2C", height=280)
        self.graph_frame.pack(fill="x", pady=10)
        self.graph_frame.pack_propagate(False)

    def setup_history_tab(self):
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="📊 History")
        
        container = tk.Frame(self.history_tab, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(container, text="📋 Session History", 
                font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.orange).pack(pady=10)

        # History list dengan multiple selection
        history_frame = tk.Frame(container, bg=self.bg_color)
        history_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(history_frame, bg="#2C2C2C", fg="white", 
                                         font=("Consolas", 10), selectmode="multiple")
        scrollbar = ttk.Scrollbar(history_frame, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)

        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons untuk history
        button_frame = tk.Frame(container, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Refresh History", 
                  command=self.load_history_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="View Selected", 
                  command=self.view_selected_session).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected_sessions).pack(side="left", padx=5)

    def setup_training_tab(self):
        self.training_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.training_tab, text="📅 Training Plans")
        
        container = tk.Frame(self.training_tab, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(container, text="🎯 Personalized Training Plans", 
                font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.orange).pack(pady=10)

        # Training plan configuration
        config_frame = tk.Frame(container, bg=self.bg_color)
        config_frame.pack(fill="x", pady=15)

        # Goal selection
        ttk.Label(config_frame, text="Goal:").pack(side="left", padx=5)
        self.goal_var = tk.StringVar(value="5k")
        goals = ["5k", "10k", "half_marathon", "marathon"]
        goal_combo = ttk.Combobox(config_frame, textvariable=self.goal_var, 
                                 values=goals, width=15)
        goal_combo.pack(side="left", padx=5)

        # Level selection
        ttk.Label(config_frame, text="Level:").pack(side="left", padx=5)
        self.level_var = tk.StringVar(value="beginner")
        levels = ["beginner", "intermediate", "advanced"]
        level_combo = ttk.Combobox(config_frame, textvariable=self.level_var,
                                  values=levels, width=12)
        level_combo.pack(side="left", padx=5)

        # Weeks selection
        ttk.Label(config_frame, text="Weeks:").pack(side="left", padx=5)
        self.weeks_var = tk.StringVar(value="8")
        weeks_combo = ttk.Combobox(config_frame, textvariable=self.weeks_var,
                                  values=["4", "8", "12", "16", "20"], width=8)
        weeks_combo.pack(side="left", padx=5)

        # Generate button
        ttk.Button(config_frame, text="Generate Training Plan", 
                  command=self.generate_training_plan).pack(side="left", padx=10)

        # Training plan display
        self.training_text = tk.Text(container, bg="#2C2C2C", fg="white", 
                                   font=("Consolas", 10), wrap="word")
        self.training_text.pack(expand=True, fill="both", pady=10)

    def setup_statistics_tab(self):
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📈 Statistics")
        
        container = tk.Frame(self.stats_tab, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(container, text="📊 Running Statistics", 
                font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.orange).pack(pady=10)

        self.stats_text = tk.Text(container, bg="#2C2C2C", fg="white", 
                                font=("Consolas", 11), wrap="word")
        self.stats_text.pack(expand=True, fill="both")

        ttk.Button(container, text="Refresh Statistics", 
                  command=self.update_statistics).pack(pady=10)

    def setup_comparison_tab(self):
        self.compare_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_tab, text="🔄 Compare")
        
        container = tk.Frame(self.compare_tab, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(container, text="📋 Compare Sessions", 
                font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.orange).pack(pady=10)

        self.compare_text = tk.Text(container, bg="#2C2C2C", fg="white", 
                                  font=("Consolas", 10), wrap="word")
        self.compare_text.pack(expand=True, fill="both")

        ttk.Button(container, text="Compare Selected Sessions", 
                  command=self.compare_selected_sessions).pack(pady=10)

    # ===================== METHODS UTAMA =====================
    def create_input(self, parent, text):
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill="x", pady=5)
        
        tk.Label(frame, text=text, bg=self.bg_color, fg=self.fg_color,
                font=("Segoe UI", 9)).pack(anchor="w")
        entry = ttk.Entry(frame, font=("Segoe UI", 10))
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def create_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, 
                       bg=self.orange, fg="black", font=("Segoe UI", 10),
                       relief="flat", padx=15, pady=8)
        btn.pack(fill="x", pady=5)
        return btn

    def create_top_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.orange, fg="black", font=("Segoe UI", 8),
                       relief="flat", padx=8, pady=4)
        btn.pack(side="left", padx=3)
        return btn

    # ===================== FITUR UTAMA =====================
    def clear_input(self):
        self.name.delete(0, tk.END)
        self.distance.delete(0, tk.END)
        self.time.delete(0, tk.END)
        self.heartrate.delete(0, tk.END)
        self.age.delete(0, tk.END)
        self.weight.delete(0, tk.END)

    def load_last_session(self):
        sessions = self.session_manager.get_recent_sessions(1)
        if sessions:
            session = sessions[0]
            self.clear_input()
            self.name.insert(0, session.get('Nama', ''))
            self.distance.insert(0, session.get('Distance', ''))
            self.time.insert(0, session.get('Time', ''))
            self.heartrate.insert(0, session.get('HeartRate', ''))
            messagebox.showinfo("Success", "Last session loaded!")
        else:
            messagebox.showwarning("Warning", "No previous sessions found!")

    def validate_inputs(self):
        try:
            if not self.name.get().strip():
                raise ValueError("Nama harus diisi")
            
            distance_str = self.distance.get().strip()
            time_str = self.time.get().strip()
            heart_rate_str = self.heartrate.get().strip()
            
            if not distance_str or not time_str or not heart_rate_str:
                raise ValueError("Jarak, waktu, dan detak jantung harus diisi")
            
            distance = float(distance_str)
            time = float(time_str)
            heart_rate = int(heart_rate_str)
            
            if distance <= 0:
                raise ValueError("Jarak harus lebih dari 0 km")
            if time <= 0:
                raise ValueError("Waktu harus lebih dari 0 menit")
            if heart_rate < 40 or heart_rate > 220:
                raise ValueError("Detak jantung harus antara 40-220 bpm")
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Error: {str(e)}")
            return False

    def run_analysis(self):
        if not self.validate_inputs():
            return
            
        try:
            name = self.name.get().strip()
            distance = float(self.distance.get())
            time = float(self.time.get())
            heart_rate = int(self.heartrate.get())
            
            age = self.age.get().strip()
            weight = self.weight.get().strip()
            
            age_val = int(age) if age else None
            weight_val = float(weight) if weight else None
            
            self.runner = RunningAnalysisEnhanced(
                name, distance, time, heart_rate, age_val, weight_val
            )
            
            self.output_text.delete(1.0, tk.END)
            summary = self.runner.summary()
            self.output_text.insert(1.0, summary)
            
            self.show_enhanced_graphs()
            
            self.current_data = {
                'distance': distance,
                'time': time,
                'heart_rate': heart_rate
            }
            
        except Exception as e:
            error_msg = f"Error dalam analisis: {str(e)}"
            messagebox.showerror("Analysis Error", error_msg)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, f"ERROR: {error_msg}")

    def quick_analysis(self):
        if not self.validate_inputs():
            return
            
        try:
            runner = RunningAnalysisEnhanced(
                self.name.get().strip(),
                float(self.distance.get()),
                float(self.time.get()),
                int(self.heartrate.get())
            )
            
            pace, pace_cat = runner.calculate_pace()
            quick_summary = (
                f"Quick Analysis untuk {runner.name}:\n\n"
                f"• Jarak: {runner.distance} km\n"
                f"• Waktu: {runner.time} menit\n" 
                f"• Pace: {pace:.2f} min/km ({pace_cat})\n"
                f"• Zona HR: {runner.heart_zone()[0]}\n"
                f"• VO2max: {runner.vo2max_estimate()} ({runner.vo2max_category()})\n"
                f"• Kalori: {runner.calorie_burn()} kcal\n"
                f"• Skor Performa: {runner.get_performance_score()}/100"
            )
            
            messagebox.showinfo("⚡ Quick Analysis", quick_summary)
            
        except Exception as e:
            messagebox.showerror("Error", f"Quick analysis error: {str(e)}")

    def show_enhanced_graphs(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        try:
            if not self.current_data:
                return
                
            # Create notebook untuk multiple graphs
            graph_notebook = ttk.Notebook(self.graph_frame)
            graph_notebook.pack(fill="both", expand=True)

            # Tab 1: Pace Analysis
            pace_frame = ttk.Frame(graph_notebook)
            graph_notebook.add(pace_frame, text="Pace Analysis")
            self.create_pace_graph(pace_frame)

            # Tab 2: Heart Rate Zones
            hr_frame = ttk.Frame(graph_notebook)
            graph_notebook.add(hr_frame, text="HR Zones")
            self.create_hr_zone_graph(hr_frame)

            # Tab 3: Progress (jika ada history)
            if self.session_manager.sessions:
                progress_frame = ttk.Frame(graph_notebook)
                graph_notebook.add(progress_frame, text="Progress")
                self.create_progress_graph(progress_frame)
                
        except Exception as e:
            print(f"Graph error: {e}")

    def create_pace_graph(self, parent):
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        distance = self.current_data['distance']
        time = self.current_data['time']
        
        if distance > 0:
            km_list = list(range(1, int(distance) + 1))
            pace_list = [time / distance] * len(km_list)
            
            ax.plot(km_list, pace_list, marker='o', color=self.orange, linewidth=2)
            ax.fill_between(km_list, pace_list, [0]*len(km_list), color=self.orange, alpha=0.1)
            ax.set_title("Grafik Pace per Kilometer")
            ax.set_xlabel("Kilometer")
            ax.set_ylabel("Pace (menit/km)")
            ax.grid(True, alpha=0.3)
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_hr_zone_graph(self, parent):
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        runner = RunningAnalysisEnhanced("Temp", 1, 1, self.current_data['heart_rate'])
        zones = runner.calculate_training_zones()
        current_hr = self.current_data['heart_rate']
        
        zone_names = list(zones.keys())
        y_pos = np.arange(len(zone_names))
        zone_widths = [zones[zone][1] - zones[zone][0] for zone in zone_names]
        
        colors = ['green', 'blue', 'orange', 'red']
        bars = ax.barh(y_pos, zone_widths, left=[zones[zone][0] for zone in zone_names], 
                      alpha=0.6, color=colors)
        
        for i, zone in enumerate(zone_names):
            if zones[zone][0] <= current_hr <= zones[zone][1]:
                bars[i].set_alpha(1.0)
                ax.axvline(x=current_hr, color='red', linestyle='--', linewidth=2, label=f'Current HR: {current_hr}')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(zone_names)
        ax.set_xlabel("Heart Rate (bpm)")
        ax.set_title("Heart Rate Training Zones")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_progress_graph(self, parent):
        dates, vo2max_scores = self.session_manager.get_progress_trend('VO2max')
        
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        if len(dates) > 1:
            ax.plot(dates, vo2max_scores, marker='o', linewidth=2, color=self.orange)
            ax.fill_between(dates, vo2max_scores, alpha=0.2, color=self.orange)
            ax.set_title("VO2Max Progress Trend")
            ax.set_xlabel("Session Date")
            ax.set_ylabel("VO2Max Score")
            ax.grid(True, alpha=0.3)
            
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
        else:
            ax.text(0.5, 0.5, "Need more data for progress tracking", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ===================== FITUR HISTORY =====================
    def load_history_data(self):
        self.history_listbox.delete(0, tk.END)
        sessions = self.session_manager.get_recent_sessions(20)
        
        if not sessions:
            self.history_listbox.insert(tk.END, "Belum ada data history")
            return
            
        for i, session in enumerate(sessions):
            display_text = (
                f"{session.get('Timestamp', 'N/A')[:16]} | "
                f"Jarak: {session.get('Distance', '0')}km | "
                f"Pace: {session.get('Pace', '0')}min/km | "
                f"VO2: {session.get('VO2max', '0')}"
            )
            self.history_listbox.insert(tk.END, display_text)

    def view_selected_session(self):
        selections = self.history_listbox.curselection()
        if not selections:
            messagebox.showwarning("Warning", "Pilih session untuk dilihat")
            return
            
        session = self.session_manager.sessions[selections[0]]
        details = (
            f"Session Details:\n"
            f"Timestamp: {session.get('Timestamp', 'N/A')}\n"
            f"Nama: {session.get('Nama', 'N/A')}\n"
            f"Jarak: {session.get('Distance', '0')} km\n"
            f"Waktu: {session.get('Time', '0')} menit\n"
            f"Pace: {session.get('Pace', '0')} min/km\n"
            f"Detak Jantung: {session.get('HeartRate', '0')} bpm\n"
            f"VO2Max: {session.get('VO2max', '0')}\n"
            f"Kalori: {session.get('Calories', '0')} kcal"
        )
        messagebox.showinfo("Session Details", details)

    def delete_selected_sessions(self):
        selections = self.history_listbox.curselection()
        if not selections:
            messagebox.showwarning("Warning", "Pilih session untuk dihapus")
            return
            
        if messagebox.askyesno("Confirm", "Hapus session terpilih?"):
            # Delete in reverse order to maintain correct indices
            for index in sorted(selections, reverse=True):
                if index < len(self.session_manager.sessions):
                    del self.session_manager.sessions[index]
            self.session_manager.save_sessions()
            self.load_history_data()
            messagebox.showinfo("Success", "Session terpilih telah dihapus")

    # ===================== FITUR TRAINING PLANS =====================
    def generate_training_plan(self):
        if not hasattr(self, 'runner'):
            messagebox.showwarning("Warning", "Lakukan analisis terlebih dahulu!")
            return
            
        try:
            goal = self.goal_var.get()
            level = self.level_var.get()
            weeks = int(self.weeks_var.get())
            
            plan = self.runner.generate_training_plan(goal, weeks, level)
            
            plan_text = (
                f"=== PERSONALIZED TRAINING PLAN ===\n"
                f"Goal: {goal.upper()} | Level: {level.title()} | Duration: {weeks} weeks\n"
                f"Generated for: {self.runner.name}\n"
                f"Current VO2Max: {self.runner.vo2max_estimate()} ({self.runner.vo2max_category()})\n"
                f"Performance Score: {self.runner.get_performance_score()}/100\n\n"
            )
            
            for week_plan in plan:
                plan_text += f"{week_plan}\n"
            
            self.training_text.delete(1.0, tk.END)
            self.training_text.insert(1.0, plan_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal generate plan: {str(e)}")

    # ===================== FITUR STATISTICS =====================
    def update_statistics(self):
        stats = self.session_manager.get_statistics()
        
        if not stats:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "No data available for statistics")
            return
            
        stats_text = (
            f"=== RUNNING STATISTICS ===\n\n"
            f"📈 Overall Summary:\n"
            f"• Total Sessions: {stats['total_sessions']}\n"
            f"• Total Distance: {stats['total_distance']:.1f} km\n"
            f"• Average Distance: {stats['avg_distance']:.1f} km\n"
            f"• Average Pace: {stats['avg_pace']:.1f} min/km\n"
            f"• Average VO2Max: {stats['avg_vo2max']:.1f}\n\n"
            
            f"🏆 Personal Bests:\n"
            f"• Best Pace: {stats['best_pace']:.1f} min/km\n"
            f"• Longest Run: {stats['longest_run']:.1f} km\n\n"
            
            f"📊 Performance Trends:\n"
        )
        
        # Add progress analysis
        if stats['total_sessions'] > 1:
            if stats['avg_pace'] < 6:
                stats_text += "• Pace: Excellent maintenance\n"
            else:
                stats_text += "• Pace: Room for improvement\n"
                
            if stats['avg_vo2max'] > 45:
                stats_text += "• Fitness: Good level\n"
            else:
                stats_text += "• Fitness: Building phase\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

    def show_statistics(self):
        self.notebook.select(3)  # Switch to statistics tab
        self.update_statistics()

    # ===================== FITUR COMPARISON =====================
    def compare_selected_sessions(self):
        selections = self.history_listbox.curselection()
        if len(selections) < 2:
            messagebox.showwarning("Warning", "Pilih minimal 2 session untuk dibandingkan")
            return
            
        comparison_data = self.session_manager.compare_sessions(selections)
        
        comparison_text = "=== SESSION COMPARISON ===\n\n"
        for i, data in enumerate(comparison_data):
            comparison_text += (
                f"Session {i+1} ({data['date'][:10]}):\n"
                f"  • Jarak: {data['distance']} km\n"
                f"  • Waktu: {data['time']} menit\n"
                f"  • Pace: {data['pace']:.1f} min/km\n"
                f"  • VO2Max: {data['vo2max']:.1f}\n"
                f"  • Kalori: {data['calories']} kcal\n\n"
            )
        
        self.compare_text.delete(1.0, tk.END)
        self.compare_text.insert(1.0, comparison_text)

    def show_comparison(self):
        self.notebook.select(4)  # Switch to comparison tab

    # ===================== FITUR LAINNYA =====================
    def save_session(self):
        if not hasattr(self, "runner"):
            messagebox.showwarning("Warning", "Jalankan analisis dulu!")
            return
        
        try:
            session_data = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nama": self.runner.name,
                "Distance": str(self.runner.distance),
                "Time": str(self.runner.time),
                "HeartRate": str(self.runner.heart_rate),
                "VO2max": str(self.runner.vo2max_estimate()),
                "VO2maxCategory": self.runner.vo2max_category(),
                "Calories": str(self.runner.calorie_burn()),
                "Pace": str(round(self.runner.time/self.runner.distance, 2))
            }
            
            self.session_manager.add_session(session_data)
            self.load_history_data()
            messagebox.showinfo("Saved", "Sesi berhasil disimpan!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Gagal menyimpan: {str(e)}")

    def export_data(self):
        if not hasattr(self, 'runner'):
            messagebox.showwarning("Warning", "Tidak ada data untuk di-export!")
            return
            
        try:
            filename = f"iqos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.runner.summary())
            messagebox.showinfo("Export Success", f"Data berhasil di-export ke {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Gagal export: {str(e)}")

    def show_progress_trend(self):
        if not self.session_manager.sessions:
            messagebox.showwarning("Warning", "Belum ada data history!")
            return
        
        self.notebook.select(1)  # Switch to history tab
        messagebox.showinfo("Progress Trend", "Grafik progress tersedia di tab Main Analysis")

    def show_training_plans(self):
        self.notebook.select(2)  # Switch to training plans tab

    def set_theme(self):
        self.orange = "#FF8C42"
        if self.theme == "dark": 
            self.bg_color = "#1E1E1E"
            self.fg_color = "white"
            style = ttk.Style()
            style.theme_use('clam')
        else: 
            self.bg_color = "white"
            self.fg_color = "black"
        self.root.configure(bg=self.bg_color)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.set_theme()

    def project_mbappe(self): 
        webbrowser.open("https://www.instagram.com/revaldibgs_/")

# ===================== MAIN =====================
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = IQOSAppEnhanced(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")