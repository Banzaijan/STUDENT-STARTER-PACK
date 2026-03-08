"""
╔══════════════════════════════════════╗
║     STUDENT STARTER PACK 🎒          ║
║  Kivy version — Android APK Ready    ║
║  v2 — Bug fixes + New Features       ║
╚══════════════════════════════════════╝
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import json, os, calendar
from datetime import datetime, date
import threading

try:
    import urllib.request
    HAS_URLLIB = True
except:
    HAS_URLLIB = False

# ─── OTA Update ──────────────────────────────────────────────────────────────
APP_VERSION     = 2
OTA_UPDATE_URL  = "https://raw.githubusercontent.com/Banzaijan/STUDENT-STARTER-PACK/refs/heads/main/Main.py"
OTA_VERSION_URL = "https://raw.githubusercontent.com/Banzaijan/STUDENT-STARTER-PACK/refs/heads/main/version.json"

def check_ota_update():
    if not HAS_URLLIB:
        return
    try:
        with urllib.request.urlopen(OTA_VERSION_URL, timeout=5) as r:
            info = json.loads(r.read().decode())
        latest = info.get("version", 1)
        if latest > APP_VERSION:
            with urllib.request.urlopen(OTA_UPDATE_URL, timeout=10) as r:
                new_code = r.read()
            script_path = os.path.abspath(__file__)
            with open(script_path, "wb") as f:
                f.write(new_code)
            print(f"[OTA] Updated to version {latest} — restart app to apply.")
    except Exception as e:
        print(f"[OTA] Check failed: {e}")

# ─── Colors ──────────────────────────────────────────────────────────────────
BG      = get_color_from_hex("#0D0D0D")
CARD    = get_color_from_hex("#1A1A1A")
CARD2   = get_color_from_hex("#222222")
ACCENT  = get_color_from_hex("#F4C97A")
ACCENT2 = get_color_from_hex("#E8B85A")
TEXT    = get_color_from_hex("#F0EDE8")
MUTED   = get_color_from_hex("#888888")
RED     = get_color_from_hex("#FF6B6B")
GREEN   = get_color_from_hex("#A8E6CF")
BLUE    = get_color_from_hex("#4ECDC4")
PURPLE  = get_color_from_hex("#C7CEEA")
NAV_BG  = get_color_from_hex("#151515")
TOPBAR  = get_color_from_hex("#1A1A2E")

# ─── Data ────────────────────────────────────────────────────────────────────
DATA_FILE = "student_data.json"

DEFAULT_SCHEDULE = {
    "Monday":    [("7:00 AM","Mathematics","Room 204"),("9:00 AM","English","Room 112"),("1:00 PM","Physics","Lab 3")],
    "Tuesday":   [("8:00 AM","History","Room 305"),("10:00 AM","P.E.","Gym"),("2:00 PM","Chemistry","Lab 1")],
    "Wednesday": [("7:00 AM","Mathematics","Room 204"),("9:00 AM","Filipino","Room 110"),("11:00 AM","MAPEH","Room 201")],
    "Thursday":  [("8:00 AM","English","Room 112"),("10:00 AM","TLE","Lab 2"),("1:00 PM","Science","Lab 1")],
    "Friday":    [("7:00 AM","Physics","Lab 3"),("9:00 AM","Values Ed","Room 302"),("2:00 PM","Free Period","Library")],
    "Saturday":  [],
    "Sunday":    [],
}

DEFAULT_EXAMS = [
    {"id":1,"subject":"Mathematics","type":"Long Quiz","date":"2026-03-10","notes":"Chapters 5-7","done":False},
    {"id":2,"subject":"Physics","type":"Lab Exam","date":"2026-03-12","notes":"Optics & Waves","done":False},
    {"id":3,"subject":"English","type":"Essay","date":"2026-03-15","notes":"Literary analysis","done":False},
    {"id":4,"subject":"Chemistry","type":"Unit Test","date":"2026-03-18","notes":"Periodic Table","done":False},
    {"id":5,"subject":"History","type":"Recitation","date":"2026-03-07","notes":"World War II","done":True},
]

DEFAULT_TODOS = [
    {"id":1,"text":"Finish Math homework","done":False,"priority":"high"},
    {"id":2,"text":"Read Chapter 8 of English","done":False,"priority":"medium"},
    {"id":3,"text":"Submit lab report","done":True,"priority":"high"},
    {"id":4,"text":"Study for Physics quiz","done":False,"priority":"high"},
    {"id":5,"text":"Print History assignment","done":False,"priority":"low"},
]

DEFAULT_GRADES = [
    {"id":1,"subject":"Mathematics","written":88,"performance":90,"exam":85},
    {"id":2,"subject":"English","written":92,"performance":88,"exam":90},
    {"id":3,"subject":"Physics","written":80,"performance":85,"exam":78},
    {"id":4,"subject":"Chemistry","written":75,"performance":80,"exam":72},
    {"id":5,"subject":"History","written":95,"performance":92,"exam":94},
]

SUBJECT_COLORS = {
    "Mathematics":"#FF6B6B","English":"#4ECDC4","Physics":"#F4C97A",
    "History":"#A8E6CF","P.E.":"#FF8B94","Chemistry":"#C7CEEA",
    "Filipino":"#FFDAC1","MAPEH":"#B5EAD7","TLE":"#F7DC6F",
    "Science":"#A9CCE3","Values Ed":"#D2B4DE","Free Period":"#A8D8EA",
}
PRIORITY_COLORS = {"high":"#FF6B6B","medium":"#F4C97A","low":"#A8E6CF"}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                d = json.load(f)
            if "grades"   not in d: d["grades"]   = DEFAULT_GRADES[:]
            if "schedule" not in d: d["schedule"]  = {k: list(v) for k, v in DEFAULT_SCHEDULE.items()}
            return d
        except:
            pass
    return {
        "exams":    DEFAULT_EXAMS[:],
        "todos":    DEFAULT_TODOS[:],
        "grades":   DEFAULT_GRADES[:],
        "schedule": {k: list(v) for k, v in DEFAULT_SCHEDULE.items()},
    }

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[SAVE] Error: {e}")

def days_left(date_str):
    try:
        exam_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (exam_date - date.today()).days
        if delta < 0:  return "Past"
        if delta == 0: return "Today!"
        return f"{delta}d left"
    except:
        return "?"

def subject_color(s):
    return get_color_from_hex(SUBJECT_COLORS.get(s, "#666666"))

def compute_gwa(written, performance, exam):
    try:
        return round(float(written)*0.25 + float(performance)*0.50 + float(exam)*0.25, 1)
    except:
        return 0.0

def grade_remark(g):
    if g >= 90: return ("Outstanding",        GREEN)
    if g >= 85: return ("Very Satisfactory",  BLUE)
    if g >= 80: return ("Satisfactory",       ACCENT)
    if g >= 75: return ("Fairly Satisfactory",PURPLE)
    return ("Did Not Meet", RED)


# ─── Reusable Widgets ────────────────────────────────────────────────────────

class CardLayout(BoxLayout):
    def __init__(self, bg=CARD, radius=14, padding=None, **kw):
        kw.setdefault("orientation", "vertical")
        super().__init__(**kw)
        self.padding = padding or [dp(12), dp(10)]
        self.spacing = dp(4)
        with self.canvas.before:
            Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


def lbl(text, size=13, color=TEXT, bold=False, halign="left", **kw):
    l = Label(text=text, font_size=dp(size), color=color, bold=bold, halign=halign, **kw)
    l.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0], None)))
    return l


def accent_btn(text, on_press, height=dp(42), font_size=13):
    btn = Button(text=text, font_size=dp(font_size), bold=True,
                 size_hint_y=None, height=height,
                 background_normal="", background_color=ACCENT,
                 color=get_color_from_hex("#111111"))
    btn.bind(on_press=on_press)
    return btn


def muted_btn(text, on_press, width=dp(80), height=dp(34)):
    btn = Button(text=text, font_size=dp(11),
                 size_hint=(None, None), size=(width, height),
                 background_normal="", background_color=CARD2, color=MUTED)
    btn.bind(on_press=on_press)
    return btn


def section_label(text):
    return lbl(text, size=14, bold=True, color=TEXT, size_hint_y=None, height=dp(36))


def scrollable(content_widget):
    sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
    sv.add_widget(content_widget)
    return sv


def vstack(spacing=8, padding=None):
    bl = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(spacing))
    bl.padding = [dp(x) for x in (padding or [14, 8, 14, 16])]
    bl.bind(minimum_height=bl.setter("height"))
    return bl


def safe_popup(content, height=dp(400)):
    return Popup(title="", content=content,
                 size_hint=(0.92, None), height=height,
                 background="", background_color=(0, 0, 0, 0),
                 separator_height=0, auto_dismiss=False)


# ─── Nav Bar ─────────────────────────────────────────────────────────────────

class NavBar(BoxLayout):
    TABS = [
        ("home",     "🏠", "Home"),
        ("schedule", "📅", "Schedule"),
        ("exams",    "📝", "Exams"),
        ("tasks",    "✅", "Tasks"),
        ("grades",   "📊", "Grades"),
        ("timer",    "⏱️",  "Timer"),
        ("weather",  "🌤️", "Weather"),
    ]

    def __init__(self, switch_cb, **kw):
        super().__init__(orientation="horizontal",
                         size_hint_y=None, height=dp(60), spacing=0, **kw)
        self.switch_cb = switch_cb
        self._btns = {}
        with self.canvas.before:
            Color(*NAV_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        for tid, icon, label in self.TABS:
            btn = Button(text=f"{icon}\n{label}", font_size=dp(8),
                         background_normal="", background_color=NAV_BG,
                         color=MUTED, halign="center")
            btn.bind(on_press=lambda b, t=tid: self.switch_cb(t))
            self._btns[tid] = btn
            self.add_widget(btn)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def set_active(self, tab):
        for tid, btn in self._btns.items():
            if tid == tab:
                btn.color = ACCENT
                btn.background_color = CARD2
            else:
                btn.color = MUTED
                btn.background_color = NAV_BG


# ─── Top Bar ─────────────────────────────────────────────────────────────────

class TopBar(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", size_hint_y=None,
                         height=dp(80), padding=[dp(16), dp(8)], spacing=dp(2), **kw)
        with self.canvas.before:
            Color(*TOPBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        now   = datetime.now()
        h     = now.hour
        greet = "Good Morning ☀️" if h < 12 else "Good Afternoon 🌤️" if h < 18 else "Good Evening 🌙"
        self.add_widget(lbl(greet, size=10, color=MUTED, size_hint_y=None, height=dp(16)))
        self.add_widget(lbl("Student 🎒", size=20, bold=True, color=ACCENT, size_hint_y=None, height=dp(30)))
        self.add_widget(lbl(f"📅 {now.strftime('%A, %B %d %Y')}", size=10, color=MUTED, size_hint_y=None, height=dp(16)))

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size


# ═══════════════════════════════════════════════════════════════════════════
#  BASE SCREEN
# ═══════════════════════════════════════════════════════════════════════════

class BaseScreen(Screen):
    def __init__(self, app_ref, **kw):
        super().__init__(**kw)
        self.app = app_ref
        with self.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def class_card(self, time_, subj, room):
        col  = subject_color(subj)
        card = CardLayout(bg=CARD, radius=12, padding=[dp(16), dp(8)],
                          size_hint_y=None, height=dp(64),
                          orientation="vertical", spacing=dp(2))
        row  = BoxLayout(size_hint_y=None, height=dp(22))
        row.add_widget(lbl(time_, size=10, color=MUTED, size_hint_x=None, width=dp(72)))
        row.add_widget(lbl(subj,  size=13, bold=True, color=TEXT))
        with card.canvas.after:
            Color(*col)
            card._bar = RoundedRectangle(pos=(card.x, card.y),
                                         size=(dp(4), card.height), radius=[dp(2)])
        def _upd_bar(inst, *a):
            inst._bar.pos  = (inst.x, inst.y)
            inst._bar.size = (dp(4), inst.height)
        card.bind(pos=_upd_bar, size=_upd_bar)
        card.add_widget(row)
        card.add_widget(lbl(f"📍 {room}", size=10, color=MUTED, size_hint_y=None, height=dp(16)))
        return card


# ── HOME ─────────────────────────────────────────────────────────────────────

class HomeScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root  = BoxLayout(orientation="vertical")
        stack = vstack()
        data  = self.app.data

        pending_exams = sum(1 for e in data["exams"] if not e["done"])
        pending_tasks = sum(1 for t in data["todos"]  if not t["done"])

        stat_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(8))
        for num, label in [(pending_exams,"Upcoming Exams"), (pending_tasks,"Pending Tasks")]:
            c = CardLayout(bg=CARD, radius=14, size_hint_x=1, padding=[dp(10), dp(10)])
            c.add_widget(lbl(str(num), size=28, bold=True, color=ACCENT,
                             halign="center", size_hint_y=None, height=dp(36)))
            c.add_widget(lbl(label, size=10, color=MUTED,
                             halign="center", size_hint_y=None, height=dp(20)))
            stat_row.add_widget(c)
        stack.add_widget(stat_row)

        today_name = datetime.now().strftime("%A")
        classes    = data.get("schedule", DEFAULT_SCHEDULE).get(today_name, [])
        stack.add_widget(section_label(f"📅 Today — {today_name}"))
        if not classes:
            c = CardLayout(bg=CARD, size_hint_y=None, height=dp(54))
            c.add_widget(lbl("🎉 No classes today! Enjoy your day.", color=MUTED, halign="center"))
            stack.add_widget(c)
        else:
            for item in classes:
                stack.add_widget(self.class_card(item[0], item[1], item[2]))

        upcoming = [e for e in data["exams"] if not e["done"] and days_left(e["date"]) != "Past"]
        upcoming.sort(key=lambda x: x["date"])
        stack.add_widget(section_label("📝 Next Exam"))
        if upcoming:
            e  = upcoming[0]
            dl = days_left(e["date"])
            c  = CardLayout(bg=CARD, radius=14, size_hint_y=None, height=dp(80))
            c.add_widget(lbl(f"{e['subject']} — {e['type']}", size=13, bold=True,
                             color=TEXT, size_hint_y=None, height=dp(22)))
            c.add_widget(lbl(f"📅 {e['date']}  ·  {e['notes']}", size=10,
                             color=MUTED, size_hint_y=None, height=dp(18)))
            c.add_widget(lbl(dl, size=12, bold=True,
                             color=RED if dl == "Today!" else ACCENT,
                             size_hint_y=None, height=dp(20)))
            stack.add_widget(c)

        root.add_widget(scrollable(stack))
        self.add_widget(root)


# ── SCHEDULE (with editor) ────────────────────────────────────────────────────

class ScheduleScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.current_day = datetime.now().strftime("%A")
        root = BoxLayout(orientation="vertical", spacing=dp(4))

        hdr = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(14), 0])
        hdr.add_widget(section_label("📅 Class Schedule"))
        add_btn = Button(text="+ Class", font_size=dp(11), bold=True,
                         size_hint=(None, None), size=(dp(76), dp(30)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=self._add_class_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)

        days    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
        self._day_btns = {}
        for d in days:
            btn = Button(text=d[:3], font_size=dp(10), bold=True,
                         size_hint_x=None, width=dp(44),
                         background_normal="",
                         background_color=ACCENT if d == self.current_day else CARD2,
                         color=get_color_from_hex("#111") if d == self.current_day else MUTED)
            btn.bind(on_press=lambda b, day=d: self._load_day(day))
            self._day_btns[d] = btn
            day_row.add_widget(btn)
        root.add_widget(day_row)

        self.sched_scroll = ScrollView(do_scroll_x=False)
        self.sched_stack  = vstack()
        self.sched_scroll.add_widget(self.sched_stack)
        root.add_widget(self.sched_scroll)
        self._load_day(self.current_day)
        self.add_widget(root)

    def _load_day(self, day):
        self.current_day = day
        for d, btn in self._day_btns.items():
            btn.background_color = ACCENT if d == day else CARD2
            btn.color = get_color_from_hex("#111") if d == day else MUTED
        self.sched_stack.clear_widgets()
        schedule = self.app.data.get("schedule", DEFAULT_SCHEDULE)
        classes  = schedule.get(day, [])
        if not classes:
            c = CardLayout(bg=CARD, size_hint_y=None, height=dp(54))
            c.add_widget(lbl("🎉 No classes — rest day!", color=MUTED, halign="center"))
            self.sched_stack.add_widget(c)
        else:
            for i, item in enumerate(classes):
                self.sched_stack.add_widget(self._class_row(item, i))

    def _class_row(self, item, idx):
        row  = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(6))
        card = self.class_card(item[0], item[1], item[2])
        card.size_hint_x = 1
        del_btn = Button(text="×", font_size=dp(18),
                         size_hint=(None, None), size=(dp(36), dp(64)),
                         background_normal="", background_color=CARD2, color=RED)
        del_btn.bind(on_press=lambda b, i=idx: Clock.schedule_once(
            lambda dt: self._delete_class(i), 0))
        row.add_widget(card)
        row.add_widget(del_btn)
        return row

    def _delete_class(self, idx):
        sched   = self.app.data.get("schedule", {k: list(v) for k,v in DEFAULT_SCHEDULE.items()})
        classes = sched.get(self.current_day, [])
        if 0 <= idx < len(classes):
            classes.pop(idx)
            sched[self.current_day]  = classes
            self.app.data["schedule"] = sched
            save_data(self.app.data)
            self._load_day(self.current_day)

    def _add_class_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(16), dp(14)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(14)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("Add Class", size=14, bold=True, color=ACCENT,
                               halign="center", size_hint_y=None, height=dp(28)))
        fields = {}
        for label, key, ph in [("Time","time","e.g. 7:00 AM"),
                                ("Subject","subject","e.g. Mathematics"),
                                ("Room","room","e.g. Room 204")]:
            content.add_widget(lbl(label, size=10, color=MUTED, size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           size_hint_y=None, height=dp(38))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(360))

        def save(*a):
            t = fields["time"].text.strip()
            s = fields["subject"].text.strip()
            r = fields["room"].text.strip()
            if not t or not s or not r:
                return
            sched = self.app.data.get("schedule", {k: list(v) for k,v in DEFAULT_SCHEDULE.items()})
            sched.setdefault(self.current_day, []).append((t, s, r))
            self.app.data["schedule"] = sched
            save_data(self.app.data)
            popup.dismiss()
            self._load_day(self.current_day)

        content.add_widget(accent_btn("Save Class", save, height=dp(42)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss()))
        popup.open()


# ── EXAMS ─────────────────────────────────────────────────────────────────────

class ExamsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))
        hdr  = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(14), 0])
        hdr.add_widget(lbl("📝 Exams & Quizzes", size=14, bold=True, color=TEXT))
        add_btn = Button(text="+ Add", font_size=dp(11), bold=True,
                         size_hint=(None, None), size=(dp(64), dp(30)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=self._add_exam_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)
        self.exams_scroll = ScrollView(do_scroll_x=False)
        self.exams_stack  = vstack()
        self.exams_scroll.add_widget(self.exams_stack)
        root.add_widget(self.exams_scroll)
        self._render_exams()
        self.add_widget(root)

    def _render_exams(self):
        self.exams_stack.clear_widgets()
        for exam in sorted(self.app.data["exams"], key=lambda x: x["date"]):
            self.exams_stack.add_widget(self._exam_card(exam))

    def _exam_card(self, exam):
        card = CardLayout(bg=CARD, radius=12, padding=[dp(12), dp(8)],
                          size_hint_y=None, height=dp(70),
                          orientation="vertical", spacing=dp(4))
        row1 = BoxLayout(size_hint_y=None, height=dp(26))
        done_btn = Button(
            text="✓" if exam["done"] else "○",
            font_size=dp(14), bold=True,
            size_hint=(None, None), size=(dp(30), dp(30)),
            background_normal="",
            background_color=ACCENT if exam["done"] else CARD2,
            color=get_color_from_hex("#111") if exam["done"] else MUTED)
        done_btn.bind(on_press=lambda b, eid=exam["id"]: Clock.schedule_once(
            lambda dt: self._toggle_exam(eid), 0))
        row1.add_widget(done_btn)
        row1.add_widget(lbl(f"  {exam['subject']}", size=13, bold=True,
                            color=MUTED if exam["done"] else TEXT))
        row1.add_widget(lbl(exam["type"], size=10, color=MUTED, halign="right"))
        dl       = days_left(exam["date"])
        dl_color = RED if dl == "Today!" else MUTED if dl == "Past" else ACCENT
        row1.add_widget(lbl(dl, size=11, bold=True, color=dl_color,
                            halign="right", size_hint_x=None, width=dp(70)))
        card.add_widget(row1)
        card.add_widget(lbl(f"📅 {exam['date']}  ·  {exam['notes']}",
                            size=10, color=MUTED, size_hint_y=None, height=dp(18)))
        return card

    def _toggle_exam(self, eid):
        for e in self.app.data["exams"]:
            if e["id"] == eid:
                e["done"] = not e["done"]
        save_data(self.app.data)
        self._render_exams()

    def _add_exam_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(16), dp(12)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(14)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("Add New Exam", size=14, bold=True, color=ACCENT,
                               halign="center", size_hint_y=None, height=dp(30)))
        fields = {}
        for label, key, ph in [("Subject","subject","e.g. Mathematics"),
                                ("Type","type","e.g. Long Quiz"),
                                ("Date","date","2026-03-20"),
                                ("Notes","notes","e.g. Chapters 1-5")]:
            content.add_widget(lbl(label, size=10, color=MUTED, size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           size_hint_y=None, height=dp(38))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(380))

        def save(*a):
            new = {k: fields[k].text.strip() for k in fields}
            if not new["subject"] or not new["date"]:
                return
            new["id"]   = max((e["id"] for e in self.app.data["exams"]), default=0) + 1
            new["done"] = False
            self.app.data["exams"].append(new)
            save_data(self.app.data)
            popup.dismiss()
            self._render_exams()

        content.add_widget(accent_btn("Save Exam", save, height=dp(42)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss()))
        popup.open()


# ── TASKS ─────────────────────────────────────────────────────────────────────

class TasksScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))
        root.add_widget(section_label("✅ To-Do List"))
        add_row = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6), padding=[dp(14), 0])
        self.task_entry = TextInput(hint_text="Add a task...", multiline=False,
                                    font_size=dp(13), background_color=CARD2,
                                    foreground_color=TEXT, hint_text_color=MUTED,
                                    cursor_color=ACCENT)
        self.priority_spinner = Spinner(text="medium", values=["high","medium","low"],
                                        font_size=dp(11), size_hint_x=None, width=dp(90),
                                        background_normal="", background_color=CARD2, color=TEXT)
        add_btn = Button(text="+", font_size=dp(20), bold=True,
                         size_hint=(None, None), size=(dp(44), dp(44)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=lambda b: Clock.schedule_once(lambda dt: self._add_todo(), 0))
        add_row.add_widget(self.task_entry)
        add_row.add_widget(self.priority_spinner)
        add_row.add_widget(add_btn)
        root.add_widget(add_row)
        self.todos_scroll = ScrollView(do_scroll_x=False)
        self.todos_stack  = vstack()
        self.todos_scroll.add_widget(self.todos_stack)
        root.add_widget(self.todos_scroll)
        self._render_todos()
        self.add_widget(root)

    def _render_todos(self):
        self.todos_stack.clear_widgets()
        for todo in self.app.data["todos"]:
            self.todos_stack.add_widget(self._todo_card(todo))
        done  = sum(1 for t in self.app.data["todos"] if t["done"])
        total = len(self.app.data["todos"])
        self.todos_stack.add_widget(
            lbl(f"{done}/{total} completed", size=10, color=MUTED,
                halign="center", size_hint_y=None, height=dp(28)))

    def _todo_card(self, todo):
        pcol = get_color_from_hex(PRIORITY_COLORS.get(todo["priority"], "#666"))
        card = CardLayout(bg=CARD, radius=10, padding=[dp(12), dp(6)],
                          size_hint_y=None, height=dp(50),
                          orientation="horizontal", spacing=dp(8))
        dot = Widget(size_hint=(None, None), size=(dp(8), dp(8)))
        with dot.canvas:
            Color(*pcol)
            dot._circ = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda i,v: setattr(i._circ,"pos",v))
        card.add_widget(dot)
        done_btn = Button(
            text="✓" if todo["done"] else "○", font_size=dp(14), bold=True,
            size_hint=(None, None), size=(dp(30), dp(30)),
            background_normal="",
            background_color=ACCENT if todo["done"] else CARD2,
            color=get_color_from_hex("#111") if todo["done"] else MUTED)
        done_btn.bind(on_press=lambda b, tid=todo["id"]: Clock.schedule_once(
            lambda dt: self._toggle_todo(tid), 0))
        card.add_widget(done_btn)
        card.add_widget(lbl(todo["text"], size=13,
                            color=MUTED if todo["done"] else TEXT))
        del_btn = Button(text="×", font_size=dp(18),
                         size_hint=(None, None), size=(dp(30), dp(30)),
                         background_normal="", background_color=(0,0,0,0), color=MUTED)
        del_btn.bind(on_press=lambda b, tid=todo["id"]: Clock.schedule_once(
            lambda dt: self._remove_todo(tid), 0))
        card.add_widget(del_btn)
        return card

    def _toggle_todo(self, tid):
        for t in self.app.data["todos"]:
            if t["id"] == tid:
                t["done"] = not t["done"]
        save_data(self.app.data)
        self._render_todos()

    def _remove_todo(self, tid):
        self.app.data["todos"] = [t for t in self.app.data["todos"] if t["id"] != tid]
        save_data(self.app.data)
        self._render_todos()

    def _add_todo(self):
        text = self.task_entry.text.strip()
        if not text:
            return
        self.app.data["todos"].append({
            "id":       max((t["id"] for t in self.app.data["todos"]), default=0) + 1,
            "text":     text,
            "done":     False,
            "priority": self.priority_spinner.text,
        })
        save_data(self.app.data)
        self.task_entry.text = ""
        self._render_todos()


# ── GRADES ────────────────────────────────────────────────────────────────────

class GradesScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))
        hdr  = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(14), 0])
        hdr.add_widget(lbl("📊 Grades Tracker", size=14, bold=True, color=TEXT))
        add_btn = Button(text="+ Add", font_size=dp(11), bold=True,
                         size_hint=(None, None), size=(dp(64), dp(30)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=self._add_grade_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)
        self.grades_scroll = ScrollView(do_scroll_x=False)
        self.grades_stack  = vstack()
        self.grades_scroll.add_widget(self.grades_stack)
        root.add_widget(self.grades_scroll)
        self._render_grades()
        self.add_widget(root)

    def _render_grades(self):
        self.grades_stack.clear_widgets()
        grades = self.app.data.get("grades", [])
        if grades:
            avg = sum(compute_gwa(g["written"], g["performance"], g["exam"])
                      for g in grades) / len(grades)
            remark, rcol = grade_remark(avg)
            summary = CardLayout(bg=CARD2, radius=14, size_hint_y=None, height=dp(70),
                                 padding=[dp(14), dp(10)])
            summary.add_widget(lbl("Overall GWA", size=10, color=MUTED,
                                   size_hint_y=None, height=dp(18)))
            row = BoxLayout(size_hint_y=None, height=dp(32))
            row.add_widget(lbl(f"{avg:.1f}", size=26, bold=True, color=ACCENT,
                               size_hint_x=None, width=dp(80)))
            row.add_widget(lbl(remark, size=12, bold=True, color=rcol))
            summary.add_widget(row)
            self.grades_stack.add_widget(summary)

        hdr = BoxLayout(size_hint_y=None, height=dp(22), padding=[dp(12), 0])
        for t, w in [("Subject",1),("Written\n25%",None),("Perf.\n50%",None),("Exam\n25%",None),("Final",None)]:
            hdr.add_widget(lbl(t, size=9, color=MUTED,
                               size_hint_x=w, width=dp(52) if w is None else None,
                               halign="center"))
        self.grades_stack.add_widget(hdr)
        for g in grades:
            self.grades_stack.add_widget(self._grade_card(g))

    def _grade_card(self, g):
        final      = compute_gwa(g["written"], g["performance"], g["exam"])
        remark, rc = grade_remark(final)
        card = CardLayout(bg=CARD, radius=10, padding=[dp(12), dp(6)],
                          size_hint_y=None, height=dp(54),
                          orientation="vertical", spacing=dp(2))
        row1 = BoxLayout(size_hint_y=None, height=dp(22))
        row1.add_widget(lbl(g["subject"], size=12, bold=True, color=TEXT))
        for val in [g["written"], g["performance"], g["exam"]]:
            row1.add_widget(lbl(str(val), size=11, color=TEXT,
                                halign="center", size_hint_x=None, width=dp(52)))
        row1.add_widget(lbl(f"{final:.1f}", size=12, bold=True, color=ACCENT,
                            halign="center", size_hint_x=None, width=dp(52)))
        card.add_widget(row1)

        pb_row = BoxLayout(size_hint_y=None, height=dp(14), spacing=dp(6))
        pb_row.add_widget(lbl(remark, size=8, color=rc, size_hint_x=None, width=dp(120)))
        pb_bg = Widget(size_hint_y=None, height=dp(6))
        with pb_bg.canvas:
            Color(*CARD2)
            pb_bg._bg_rect = RoundedRectangle(pos=pb_bg.pos, size=pb_bg.size, radius=[dp(3)])
            Color(*rc)
            pb_bg._fill = RoundedRectangle(pos=pb_bg.pos,
                                           size=(pb_bg.width * min(final/100.0,1.0), pb_bg.height),
                                           radius=[dp(3)])
        def _upd_pb(inst, *a):
            inst._bg_rect.pos  = inst.pos
            inst._bg_rect.size = inst.size
            inst._fill.pos     = inst.pos
            inst._fill.size    = (inst.width * min(final/100.0,1.0), inst.height)
        pb_bg.bind(pos=_upd_pb, size=_upd_pb)
        pb_row.add_widget(pb_bg)

        del_btn = Button(text="×", font_size=dp(16),
                         size_hint=(None, None), size=(dp(28), dp(28)),
                         background_normal="", background_color=(0,0,0,0), color=MUTED)
        del_btn.bind(on_press=lambda b, gid=g["id"]: Clock.schedule_once(
            lambda dt: self._delete_grade(gid), 0))
        pb_row.add_widget(del_btn)
        card.add_widget(pb_row)
        return card

    def _delete_grade(self, gid):
        self.app.data["grades"] = [g for g in self.app.data["grades"] if g["id"] != gid]
        save_data(self.app.data)
        self._render_grades()

    def _add_grade_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(16), dp(12)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(14)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("Add Grades", size=14, bold=True, color=ACCENT,
                               halign="center", size_hint_y=None, height=dp(28)))
        content.add_widget(lbl("Written 25% + Performance 50% + Exam 25%",
                               size=9, color=MUTED, halign="center",
                               size_hint_y=None, height=dp(18)))
        fields = {}
        for label, key, ph in [("Subject","subject","e.g. Mathematics"),
                                ("Written Works (25%)","written","e.g. 88"),
                                ("Performance Tasks (50%)","performance","e.g. 90"),
                                ("Quarterly Exam (25%)","exam","e.g. 85")]:
            content.add_widget(lbl(label, size=10, color=MUTED, size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           input_filter="float" if key != "subject" else None,
                           size_hint_y=None, height=dp(38))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(430))

        def save(*a):
            subj = fields["subject"].text.strip()
            if not subj:
                return
            try:
                w = float(fields["written"].text or 0)
                p = float(fields["performance"].text or 0)
                e = float(fields["exam"].text or 0)
            except:
                return
            self.app.data["grades"].append({
                "id":          max((g["id"] for g in self.app.data["grades"]), default=0) + 1,
                "subject":     subj,
                "written":     w,
                "performance": p,
                "exam":        e,
            })
            save_data(self.app.data)
            popup.dismiss()
            self._render_grades()

        content.add_widget(accent_btn("Save Grades", save, height=dp(42)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss()))
        popup.open()


# ── POMODORO TIMER ────────────────────────────────────────────────────────────

class TimerScreen(BaseScreen):
    WORK_MINS  = 25
    BREAK_MINS = 5

    def on_enter(self):
        self.clear_widgets()
        self._timer_event = None
        self._seconds     = self.WORK_MINS * 60
        self._running     = False
        self._is_break    = False
        self._sessions    = 0

        root = BoxLayout(orientation="vertical", spacing=dp(8))
        root.add_widget(section_label("⏱️ Pomodoro Timer"))

        self._session_lbl = lbl("Sessions completed: 0", size=11, color=MUTED,
                                 halign="center", size_hint_y=None, height=dp(22))
        root.add_widget(self._session_lbl)

        self._mode_lbl = lbl("🍅 Focus Time", size=14, bold=True, color=ACCENT,
                              halign="center", size_hint_y=None, height=dp(30))
        root.add_widget(self._mode_lbl)

        timer_card = CardLayout(bg=CARD, radius=20, size_hint_y=None, height=dp(160))
        self._timer_lbl = lbl("25:00", size=52, bold=True, color=TEXT,
                               halign="center", size_hint_y=None, height=dp(80))
        timer_card.add_widget(self._timer_lbl)

        self._pb_total = self.WORK_MINS * 60
        self._pb_bg    = Widget(size_hint_y=None, height=dp(8))
        with self._pb_bg.canvas:
            Color(*CARD2)
            self._pb_bg._bg = RoundedRectangle(pos=self._pb_bg.pos,
                                               size=self._pb_bg.size, radius=[dp(4)])
            Color(*ACCENT)
            self._pb_bg._fill = RoundedRectangle(pos=self._pb_bg.pos,
                                                  size=self._pb_bg.size, radius=[dp(4)])
        def _upd_pb(inst, *a):
            inst._bg.pos  = inst.pos
            inst._bg.size = inst.size
            ratio = self._seconds / self._pb_total if self._pb_total else 1
            inst._fill.pos  = inst.pos
            inst._fill.size = (inst.width * ratio, inst.height)
        self._pb_bg.bind(pos=_upd_pb, size=_upd_pb)
        self._pb_upd = _upd_pb
        timer_card.add_widget(self._pb_bg)
        root.add_widget(timer_card)

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10),
                            padding=[dp(14), 0])
        self._start_btn = Button(text="▶  Start", font_size=dp(14), bold=True,
                                  background_normal="", background_color=ACCENT,
                                  color=get_color_from_hex("#111"))
        self._start_btn.bind(on_press=self._toggle_timer)
        btn_row.add_widget(self._start_btn)
        reset_btn = Button(text="↺  Reset", font_size=dp(13),
                           background_normal="", background_color=CARD2, color=TEXT)
        reset_btn.bind(on_press=self._reset_timer)
        btn_row.add_widget(reset_btn)
        root.add_widget(btn_row)

        dur_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8),
                            padding=[dp(14), 0])
        dur_row.add_widget(lbl("Work min:", size=11, color=MUTED,
                               size_hint_x=None, width=dp(72)))
        self._work_input = TextInput(text=str(self.WORK_MINS), multiline=False,
                                      font_size=dp(13), input_filter="int",
                                      background_color=CARD2, foreground_color=TEXT,
                                      cursor_color=ACCENT,
                                      size_hint_x=None, width=dp(50))
        dur_row.add_widget(self._work_input)
        dur_row.add_widget(lbl("Break min:", size=11, color=MUTED,
                               size_hint_x=None, width=dp(76)))
        self._break_input = TextInput(text=str(self.BREAK_MINS), multiline=False,
                                       font_size=dp(13), input_filter="int",
                                       background_color=CARD2, foreground_color=TEXT,
                                       cursor_color=ACCENT,
                                       size_hint_x=None, width=dp(50))
        dur_row.add_widget(self._break_input)
        set_btn = Button(text="Set", font_size=dp(11),
                         size_hint_x=None, width=dp(48),
                         background_normal="", background_color=CARD2, color=ACCENT)
        set_btn.bind(on_press=self._reset_timer)
        dur_row.add_widget(set_btn)
        root.add_widget(dur_row)

        tip_card = CardLayout(bg=CARD, radius=12, size_hint_y=None, height=dp(80),
                              padding=[dp(14), dp(8)])
        tip_card.add_widget(lbl("💡 Pomodoro Technique", size=11, bold=True,
                                color=ACCENT, size_hint_y=None, height=dp(20)))
        tip_card.add_widget(lbl("Focus for 25 min → 5 min break → repeat.\nAfter 4 sessions take a long 15-30 min break.",
                                size=10, color=MUTED, size_hint_y=None, height=dp(40)))
        root.add_widget(tip_card)
        self.add_widget(root)

    def _toggle_timer(self, *a):
        if self._running:
            self._running = False
            if self._timer_event:
                self._timer_event.cancel()
                self._timer_event = None
            self._start_btn.text = "▶  Resume"
            self._start_btn.background_color = ACCENT
        else:
            self._running = True
            self._start_btn.text = "⏸  Pause"
            self._start_btn.background_color = CARD2
            self._timer_event = Clock.schedule_interval(self._tick, 1)

    def _tick(self, dt):
        if self._seconds > 0:
            self._seconds -= 1
            self._update_display()
        else:
            self._timer_event.cancel()
            self._timer_event = None
            self._running     = False
            if not self._is_break:
                self._sessions += 1
                self._session_lbl.text = f"Sessions completed: {self._sessions}"
                self._is_break   = True
                self._seconds    = int(self._break_input.text or 5) * 60
                self._pb_total   = self._seconds
                self._mode_lbl.text  = "☕ Break Time!"
                self._mode_lbl.color = GREEN
            else:
                self._is_break  = False
                self._seconds   = int(self._work_input.text or 25) * 60
                self._pb_total  = self._seconds
                self._mode_lbl.text  = "🍅 Focus Time"
                self._mode_lbl.color = ACCENT
            self._start_btn.text = "▶  Start"
            self._start_btn.background_color = ACCENT
            self._update_display()

    def _update_display(self):
        m, s = divmod(self._seconds, 60)
        self._timer_lbl.text = f"{m:02d}:{s:02d}"
        self._pb_upd(self._pb_bg)

    def _reset_timer(self, *a):
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None
        self._running  = False
        self._is_break = False
        self._seconds  = int(self._work_input.text or 25) * 60
        self._pb_total = self._seconds
        self._mode_lbl.text  = "🍅 Focus Time"
        self._mode_lbl.color = ACCENT
        self._start_btn.text = "▶  Start"
        self._start_btn.background_color = ACCENT
        self._update_display()

    def on_leave(self):
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None


# ── WEATHER ──────────────────────────────────────────────────────────────────

WMO_ICONS = {
    0:"☀️",1:"🌤️",2:"⛅",3:"☁️",45:"🌫️",48:"🌫️",
    51:"🌦️",53:"🌦️",55:"🌧️",61:"🌧️",63:"🌧️",65:"🌧️",
    80:"🌦️",81:"🌧️",82:"⛈️",95:"⛈️",96:"⛈️",99:"⛈️"
}
WMO_DESC = {
    0:"Clear Sky",1:"Mainly Clear",2:"Partly Cloudy",3:"Overcast",
    45:"Foggy",51:"Light Drizzle",61:"Light Rain",63:"Moderate Rain",
    65:"Heavy Rain",80:"Rain Showers",95:"Thunderstorm"
}

class WeatherScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))
        root.add_widget(section_label("🌤️ Weather"))
        self.weather_card = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(80))
        self.weather_card.add_widget(lbl("Fetching weather...", color=MUTED, halign="center"))
        root.add_widget(self.weather_card)
        root.add_widget(section_label("📆 Calendar"))
        root.add_widget(self._build_calendar())
        self.add_widget(root)
        threading.Thread(target=self._fetch_weather, daemon=True).start()

    def _fetch_weather(self):
        try:
            if not HAS_URLLIB:
                raise Exception("no urllib")
            url = ("https://api.open-meteo.com/v1/forecast"
                   "?latitude=14.5995&longitude=120.9842"
                   "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
                   "&daily=temperature_2m_max,temperature_2m_min,weather_code"
                   "&timezone=Asia/Manila&forecast_days=5")
            with urllib.request.urlopen(url, timeout=8) as r:
                data = json.loads(r.read().decode())
            Clock.schedule_once(lambda dt: self._render_weather(data))
        except:
            Clock.schedule_once(lambda dt: self._render_fallback())

    def _render_weather(self, data):
        self.weather_card.clear_widgets()
        self.weather_card.height = dp(220)
        c    = data["current"]
        d    = data["daily"]
        temp = round(c["temperature_2m"])
        hum  = c["relative_humidity_2m"]
        wind = c["wind_speed_10m"]
        code = c["weather_code"]
        icon = WMO_ICONS.get(code, "🌡️")
        desc = WMO_DESC.get(code, "Unknown")

        main_row = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(8))
        main_row.add_widget(lbl(icon, size=48, halign="center",
                                size_hint_x=None, width=dp(70)))
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(lbl("Manila, PH", size=10, color=MUTED, size_hint_y=None, height=dp(18)))
        info.add_widget(lbl(f"{temp}°C", size=30, bold=True, color=TEXT, size_hint_y=None, height=dp(40)))
        info.add_widget(lbl(desc, size=10, color=MUTED, size_hint_y=None, height=dp(18)))
        main_row.add_widget(info)
        detail = BoxLayout(orientation="vertical", spacing=dp(4))
        detail.add_widget(lbl(f"💧 {hum}%", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(20)))
        detail.add_widget(lbl(f"💨 {wind} km/h", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(20)))
        main_row.add_widget(detail)
        self.weather_card.add_widget(main_row)

        fc_row     = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(4))
        day_labels = ["Today","Fri","Sat","Sun","Mon"]
        for i in range(min(5, len(d["temperature_2m_max"]))):
            fc = CardLayout(bg=CARD2, radius=10, size_hint_x=1, padding=[dp(4), dp(4)])
            fc.add_widget(lbl(day_labels[i], size=9, color=MUTED,
                              halign="center", size_hint_y=None, height=dp(16)))
            fc.add_widget(lbl(WMO_ICONS.get(d["weather_code"][i],"🌡️"),
                              size=18, halign="center", size_hint_y=None, height=dp(26)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_max'][i])}°",
                              size=11, bold=True, color=TEXT, halign="center",
                              size_hint_y=None, height=dp(18)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_min'][i])}°",
                              size=10, color=MUTED, halign="center",
                              size_hint_y=None, height=dp(16)))
            fc_row.add_widget(fc)
        self.weather_card.add_widget(fc_row)

    def _render_fallback(self):
        self.weather_card.clear_widgets()
        self.weather_card.add_widget(
            lbl("⚠️ Couldn't load weather.\nCheck your internet connection.",
                color=MUTED, halign="center"))

    def _build_calendar(self):
        now   = datetime.now()
        frame = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(260),
                           padding=[dp(14), dp(10)])
        frame.add_widget(lbl(now.strftime("%B %Y"), size=14, bold=True, color=TEXT,
                             size_hint_y=None, height=dp(28)))
        day_row = BoxLayout(size_hint_y=None, height=dp(22))
        for d in ["Su","Mo","Tu","We","Th","Fr","Sa"]:
            day_row.add_widget(lbl(d, size=9, color=MUTED, halign="center"))
        frame.add_widget(day_row)
        for week in calendar.monthcalendar(now.year, now.month):
            week_row = BoxLayout(size_hint_y=None, height=dp(30))
            for day in week:
                is_today = day == now.day
                cell = Button(
                    text=str(day) if day else "",
                    font_size=dp(11), bold=is_today,
                    background_normal="",
                    background_color=ACCENT if is_today else (0,0,0,0),
                    color=get_color_from_hex("#111") if is_today else (TEXT if day else (0,0,0,0)))
                week_row.add_widget(cell)
            frame.add_widget(week_row)
        return frame


# ═══════════════════════════════════════════════════════════════════════════
#  APP ROOT
# ═══════════════════════════════════════════════════════════════════════════

class StudentApp(App):
    def build(self):
        self.data  = load_data()
        self.title = "Student Starter Pack"
        threading.Thread(target=check_ota_update, daemon=True).start()

        root = BoxLayout(orientation="vertical")
        root.add_widget(TopBar())

        self.sm = ScreenManager(transition=NoTransition(), size_hint_y=1)
        for name, cls in [
            ("home",     HomeScreen),
            ("schedule", ScheduleScreen),
            ("exams",    ExamsScreen),
            ("tasks",    TasksScreen),
            ("grades",   GradesScreen),
            ("timer",    TimerScreen),
            ("weather",  WeatherScreen),
        ]:
            self.sm.add_widget(cls(app_ref=self, name=name))
        root.add_widget(self.sm)

        self.nav = NavBar(switch_cb=self.switch_tab)
        root.add_widget(self.nav)
        self.switch_tab("home")
        return root

    def switch_tab(self, tab):
        self.sm.current = tab
        self.nav.set_active(tab)


if __name__ == "__main__":
    StudentApp().run()