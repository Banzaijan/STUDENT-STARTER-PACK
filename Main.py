"""
╔══════════════════════════════════════╗
║     STUDENT STARTER PACK 🎒          ║
║  Kivy version — Android APK Ready    ║
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
from kivy.graphics import Color, RoundedRectangle, Rectangle
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
                return json.load(f)
        except: pass
    return {"exams": DEFAULT_EXAMS[:], "todos": DEFAULT_TODOS[:]}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def days_left(date_str):
    try:
        exam_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (exam_date - date.today()).days
        if delta < 0:  return "Past"
        if delta == 0: return "Today!"
        return f"{delta}d left"
    except: return "?"

def subject_color(s):
    return get_color_from_hex(SUBJECT_COLORS.get(s, "#666666"))


# ─── Reusable Widgets ────────────────────────────────────────────────────────

class RoundedBox(Widget):
    """A rounded rectangle background widget."""
    def __init__(self, color=CARD, radius=14, **kw):
        super().__init__(**kw)
        self._color = color
        self._radius = radius
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self._radius)])


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
        self._rect.pos = self.pos
        self._rect.size = self.size


def lbl(text, size=13, color=TEXT, bold=False, halign="left", **kw):
    l = Label(text=text, font_size=dp(size), color=color,
              bold=bold, halign=halign, **kw)
    l.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0], None)))
    return l


def accent_btn(text, on_press, height=dp(42), font_size=13):
    btn = Button(text=text, font_size=dp(font_size), bold=True,
                 size_hint_y=None, height=height,
                 background_normal="", background_color=ACCENT,
                 color=get_color_from_hex("#111111"))
    btn.bind(on_press=on_press)
    return btn


def muted_btn(text, on_press, width=dp(60), height=dp(32)):
    btn = Button(text=text, font_size=dp(11),
                 size_hint=(None, None), size=(width, height),
                 background_normal="", background_color=CARD2, color=MUTED)
    btn.bind(on_press=on_press)
    return btn


def section_label(text):
    return lbl(text, size=14, bold=True, color=TEXT,
               size_hint_y=None, height=dp(36))


def scrollable(content_widget):
    sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
    sv.add_widget(content_widget)
    return sv


def vstack(spacing=8, padding=None):
    bl = BoxLayout(orientation="vertical",
                   size_hint_y=None, spacing=dp(spacing))
    bl.padding = [dp(x) for x in (padding or [14, 8, 14, 16])]
    bl.bind(minimum_height=bl.setter("height"))
    return bl


# ─── Nav Bar ─────────────────────────────────────────────────────────────────

class NavBar(BoxLayout):
    TABS = [("home","🏠","Home"),("schedule","📅","Schedule"),
            ("exams","📝","Exams"),("tasks","✅","Tasks"),("weather","🌤️","Weather")]

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
            btn = Button(text=f"{icon}\n{label}", font_size=dp(9.5),
                         background_normal="", background_color=NAV_BG,
                         color=MUTED, halign="center")
            btn.bind(on_press=lambda b, t=tid: self.switch_cb(t))
            self._btns[tid] = btn
            self.add_widget(btn)

    def _upd(self, *a):
        self._bg.pos = self.pos
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

        now = datetime.now()
        h = now.hour
        greet = "Good Morning ☀️" if h < 12 else "Good Afternoon 🌤️" if h < 18 else "Good Evening 🌙"
        day_str = now.strftime("%A, %B %d %Y")

        self.add_widget(lbl(greet, size=10, color=MUTED,
                            size_hint_y=None, height=dp(16)))
        self.add_widget(lbl("Student 🎒", size=20, bold=True, color=ACCENT,
                            size_hint_y=None, height=dp(30)))
        self.add_widget(lbl(f"📅 {day_str}", size=10, color=MUTED,
                            size_hint_y=None, height=dp(16)))

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ═══════════════════════════════════════════════════════════════════════════
#  SCREENS
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
        self._bg.pos = self.pos
        self._bg.size = self.size

    def class_card(self, time_, subj, room):
        col = subject_color(subj)
        card = CardLayout(bg=CARD, radius=12,
                          padding=[dp(12), dp(8)],
                          size_hint_y=None, height=dp(64),
                          orientation="vertical", spacing=dp(2))
        row = BoxLayout(size_hint_y=None, height=dp(22))
        with card.canvas.before:
            Color(*col)
            RoundedRectangle(pos=(card.x, card.y), size=(dp(4), card.height),
                             radius=[dp(2)])
        row.add_widget(lbl(time_, size=10, color=MUTED,
                           size_hint_x=None, width=dp(72)))
        row.add_widget(lbl(subj, size=13, bold=True, color=TEXT))
        card.add_widget(row)
        card.add_widget(lbl(f"📍 {room}", size=10, color=MUTED,
                            size_hint_y=None, height=dp(16)))
        return card


# ── HOME ─────────────────────────────────────────────────────────────────────

class HomeScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        stack = vstack()

        data = self.app.data
        pending_exams = sum(1 for e in data["exams"] if not e["done"])
        pending_tasks = sum(1 for t in data["todos"] if not t["done"])

        # Stats row
        stat_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(8))
        for num, label in [(pending_exams,"Upcoming Exams"),(pending_tasks,"Pending Tasks")]:
            c = CardLayout(bg=CARD, radius=14, size_hint_x=1,
                           padding=[dp(10), dp(10)])
            c.add_widget(lbl(str(num), size=28, bold=True, color=ACCENT,
                             halign="center", size_hint_y=None, height=dp(36)))
            c.add_widget(lbl(label, size=10, color=MUTED,
                             halign="center", size_hint_y=None, height=dp(20)))
            stat_row.add_widget(c)
        stack.add_widget(stat_row)

        # Today's classes
        today_name = datetime.now().strftime("%A")
        classes = DEFAULT_SCHEDULE.get(today_name, [])
        stack.add_widget(section_label(f"📅 Today — {today_name}"))
        if not classes:
            c = CardLayout(bg=CARD, size_hint_y=None, height=dp(54))
            c.add_widget(lbl("🎉 No classes today! Enjoy your day.", color=MUTED, halign="center"))
            stack.add_widget(c)
        else:
            for time_, subj, room in classes:
                stack.add_widget(self.class_card(time_, subj, room))

        # Next exam
        upcoming = [e for e in data["exams"] if not e["done"] and days_left(e["date"]) != "Past"]
        upcoming.sort(key=lambda x: x["date"])
        stack.add_widget(section_label("📝 Next Exam"))
        if upcoming:
            e = upcoming[0]
            dl = days_left(e["date"])
            c = CardLayout(bg=CARD, radius=14, size_hint_y=None, height=dp(80))
            c.add_widget(lbl(f"{e['subject']} — {e['type']}", size=13, bold=True, color=TEXT,
                             size_hint_y=None, height=dp(22)))
            c.add_widget(lbl(f"📅 {e['date']}  ·  {e['notes']}", size=10, color=MUTED,
                             size_hint_y=None, height=dp(18)))
            c.add_widget(lbl(dl, size=12, bold=True,
                             color=RED if dl == "Today!" else ACCENT,
                             size_hint_y=None, height=dp(20)))
            stack.add_widget(c)

        root.add_widget(scrollable(stack))
        self.add_widget(root)


# ── SCHEDULE ─────────────────────────────────────────────────────────────────

class ScheduleScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.current_day = datetime.now().strftime("%A")
        root = BoxLayout(orientation="vertical", spacing=dp(4))

        root.add_widget(section_label("📅 Class Schedule"))

        # Day buttons
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
        self._day_btns = {}
        for d in days:
            btn = Button(text=d[:3], font_size=dp(10), bold=True,
                         size_hint_x=None, width=dp(44),
                         background_normal="", corner_radius=dp(8),
                         background_color=ACCENT if d==self.current_day else CARD2,
                         color=get_color_from_hex("#111") if d==self.current_day else MUTED)
            btn.bind(on_press=lambda b, day=d: self._load_day(day))
            self._day_btns[d] = btn
            day_row.add_widget(btn)
        root.add_widget(day_row)

        self.sched_scroll = ScrollView(do_scroll_x=False)
        self.sched_stack = vstack()
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
        classes = DEFAULT_SCHEDULE.get(day, [])
        if not classes:
            c = CardLayout(bg=CARD, size_hint_y=None, height=dp(54))
            c.add_widget(lbl("🎉 No classes — rest day!", color=MUTED, halign="center"))
            self.sched_stack.add_widget(c)
        else:
            for time_, subj, room in classes:
                self.sched_stack.add_widget(self.class_card(time_, subj, room))


# ── EXAMS ─────────────────────────────────────────────────────────────────────

class ExamsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))

        header = BoxLayout(size_hint_y=None, height=dp(40),
                           padding=[dp(14), 0])
        header.add_widget(lbl("📝 Exams & Quizzes", size=14, bold=True, color=TEXT))
        add_btn = Button(text="+ Add", font_size=dp(11), bold=True,
                         size_hint=(None, None), size=(dp(64), dp(30)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=self._add_exam_popup)
        header.add_widget(add_btn)
        root.add_widget(header)

        self.exams_scroll = ScrollView(do_scroll_x=False)
        self.exams_stack = vstack()
        self.exams_scroll.add_widget(self.exams_stack)
        root.add_widget(self.exams_scroll)
        self._render_exams()
        self.add_widget(root)

    def _render_exams(self):
        self.exams_stack.clear_widgets()
        sorted_exams = sorted(self.app.data["exams"], key=lambda x: x["date"])
        for exam in sorted_exams:
            self.exams_stack.add_widget(self._exam_card(exam))

    def _exam_card(self, exam):
        col = subject_color(exam["subject"])
        card = CardLayout(bg=CARD, radius=12,
                          padding=[dp(12), dp(8)],
                          size_hint_y=None, height=dp(70),
                          orientation="vertical", spacing=dp(4))
        row1 = BoxLayout(size_hint_y=None, height=dp(26))

        done_btn = Button(
            text="✓" if exam["done"] else "○",
            font_size=dp(14), bold=True,
            size_hint=(None, None), size=(dp(28), dp(28)),
            background_normal="", background_color=ACCENT if exam["done"] else CARD2,
            color=get_color_from_hex("#111") if exam["done"] else MUTED)
        done_btn.bind(on_press=lambda b, eid=exam["id"]: self._toggle_exam(eid))
        row1.add_widget(done_btn)
        row1.add_widget(lbl(f"  {exam['subject']}", size=13, bold=True,
                            color=MUTED if exam["done"] else TEXT))
        row1.add_widget(lbl(exam["type"], size=10, color=MUTED, halign="right"))

        dl = days_left(exam["date"])
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
        content = BoxLayout(orientation="vertical", spacing=dp(8),
                            padding=[dp(16), dp(12)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(14)])
        content.bind(pos=lambda i,v: setattr(i._bg, "pos", v),
                     size=lambda i,v: setattr(i._bg, "size", v))

        content.add_widget(lbl("Add New Exam", size=14, bold=True, color=ACCENT,
                               halign="center", size_hint_y=None, height=dp(30)))
        fields = {}
        for label, key, ph in [("Subject","subject","e.g. Mathematics"),
                                ("Type","type","e.g. Long Quiz"),
                                ("Date","date","2026-03-20"),
                                ("Notes","notes","e.g. Chapters 1-5")]:
            content.add_widget(lbl(label, size=10, color=MUTED,
                                   size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           size_hint_y=None, height=dp(38))
            content.add_widget(ti)
            fields[key] = ti

        popup = Popup(title="", content=content,
                      size_hint=(0.9, None), height=dp(380),
                      background="", background_color=(0,0,0,0),
                      separator_height=0)

        def save(*a):
            new = {k: fields[k].text.strip() for k in fields}
            if not new["subject"] or not new["date"]:
                return
            new["id"] = len(self.app.data["exams"]) + 1
            new["done"] = False
            self.app.data["exams"].append(new)
            save_data(self.app.data)
            popup.dismiss()
            self._render_exams()

        content.add_widget(accent_btn("Save Exam", save, height=dp(42)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss(),
                                     width=dp(80), height=dp(34)))
        popup.open()


# ── TASKS ─────────────────────────────────────────────────────────────────────

class TasksScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(4))
        root.add_widget(section_label("✅ To-Do List"))

        # Add row
        add_row = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6), padding=[dp(14), 0])
        self.task_entry = TextInput(hint_text="Add a task...", multiline=False,
                                    font_size=dp(13), background_color=CARD2,
                                    foreground_color=TEXT, hint_text_color=MUTED,
                                    cursor_color=ACCENT)
        self.priority_spinner = Spinner(
            text="medium", values=["high", "medium", "low"],
            font_size=dp(11), size_hint_x=None, width=dp(90),
            background_normal="", background_color=CARD2, color=TEXT)
        add_btn = Button(text="+", font_size=dp(20), bold=True,
                         size_hint=(None, None), size=(dp(44), dp(44)),
                         background_normal="", background_color=ACCENT,
                         color=get_color_from_hex("#111"))
        add_btn.bind(on_press=self._add_todo)
        add_row.add_widget(self.task_entry)
        add_row.add_widget(self.priority_spinner)
        add_row.add_widget(add_btn)
        root.add_widget(add_row)

        self.todos_scroll = ScrollView(do_scroll_x=False)
        self.todos_stack = vstack()
        self.todos_scroll.add_widget(self.todos_stack)
        root.add_widget(self.todos_scroll)
        self._render_todos()
        self.add_widget(root)

    def _render_todos(self):
        self.todos_stack.clear_widgets()
        for todo in self.app.data["todos"]:
            self.todos_stack.add_widget(self._todo_card(todo))
        done = sum(1 for t in self.app.data["todos"] if t["done"])
        total = len(self.app.data["todos"])
        self.todos_stack.add_widget(
            lbl(f"{done}/{total} completed", size=10, color=MUTED,
                halign="center", size_hint_y=None, height=dp(28)))

    def _todo_card(self, todo):
        pcol = get_color_from_hex(PRIORITY_COLORS.get(todo["priority"], "#666"))
        card = CardLayout(bg=CARD, radius=10,
                          padding=[dp(12), dp(6)],
                          size_hint_y=None, height=dp(50),
                          orientation="horizontal", spacing=dp(8))
        dot = Widget(size_hint=(None, None), size=(dp(8), dp(8)))
        with dot.canvas:
            Color(*pcol)
            dot._ellipse = RoundedRectangle(pos=dot.pos, size=dot.size, radius=[dp(4)])
        dot.bind(pos=lambda i,v: setattr(i._ellipse,"pos",v))

        card.add_widget(dot)

        done_btn = Button(
            text="✓" if todo["done"] else "○", font_size=dp(14), bold=True,
            size_hint=(None, None), size=(dp(28), dp(28)),
            background_normal="", background_color=ACCENT if todo["done"] else CARD2,
            color=get_color_from_hex("#111") if todo["done"] else MUTED)
        done_btn.bind(on_press=lambda b, tid=todo["id"]: self._toggle_todo(tid))
        card.add_widget(done_btn)

        card.add_widget(lbl(todo["text"], size=13,
                            color=MUTED if todo["done"] else TEXT))

        del_btn = Button(text="×", font_size=dp(16),
                         size_hint=(None, None), size=(dp(28), dp(28)),
                         background_normal="", background_color="transparent",
                         color=MUTED)
        del_btn.bind(on_press=lambda b, tid=todo["id"]: self._remove_todo(tid))
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

    def _add_todo(self, *a):
        text = self.task_entry.text.strip()
        if not text: return
        self.app.data["todos"].append({
            "id": len(self.app.data["todos"]) + 1,
            "text": text, "done": False,
            "priority": self.priority_spinner.text
        })
        save_data(self.app.data)
        self.task_entry.text = ""
        self._render_todos()


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

        self.weather_card = CardLayout(bg=CARD, radius=16,
                                       size_hint_y=None, height=dp(80))
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
        c = data["current"]
        d = data["daily"]
        temp = round(c["temperature_2m"])
        humidity = c["relative_humidity_2m"]
        wind = c["wind_speed_10m"]
        code = c["weather_code"]
        icon = WMO_ICONS.get(code, "🌡️")
        desc = WMO_DESC.get(code, "Unknown")

        main_row = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(8))
        main_row.add_widget(lbl(icon, size=48, halign="center",
                                size_hint_x=None, width=dp(70)))
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(lbl("Manila, PH", size=10, color=MUTED,
                            size_hint_y=None, height=dp(18)))
        info.add_widget(lbl(f"{temp}°C", size=30, bold=True, color=TEXT,
                            size_hint_y=None, height=dp(40)))
        info.add_widget(lbl(desc, size=10, color=MUTED,
                            size_hint_y=None, height=dp(18)))
        main_row.add_widget(info)

        detail = BoxLayout(orientation="vertical", spacing=dp(4))
        detail.add_widget(lbl(f"💧 {humidity}%", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(20)))
        detail.add_widget(lbl(f"💨 {wind} km/h", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(20)))
        main_row.add_widget(detail)
        self.weather_card.add_widget(main_row)

        # Forecast row
        fc_row = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(4))
        day_labels = ["Today","Fri","Sat","Sun","Mon"]
        for i in range(min(5, len(d["temperature_2m_max"]))):
            fc = CardLayout(bg=CARD2, radius=10,
                            size_hint_x=1, padding=[dp(4), dp(4)])
            fc.add_widget(lbl(day_labels[i], size=9, color=MUTED,
                              halign="center", size_hint_y=None, height=dp(16)))
            fc.add_widget(lbl(WMO_ICONS.get(d["weather_code"][i],"🌡️"),
                              size=18, halign="center",
                              size_hint_y=None, height=dp(26)))
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
        now = datetime.now()
        frame = CardLayout(bg=CARD, radius=16,
                           size_hint_y=None, height=dp(260),
                           padding=[dp(14), dp(10)])

        frame.add_widget(lbl(now.strftime("%B %Y"), size=14, bold=True, color=TEXT,
                             size_hint_y=None, height=dp(28)))

        day_row = BoxLayout(size_hint_y=None, height=dp(22))
        for d in ["Su","Mo","Tu","We","Th","Fr","Sa"]:
            day_row.add_widget(lbl(d, size=9, color=MUTED, halign="center"))
        frame.add_widget(day_row)

        cal = calendar.monthcalendar(now.year, now.month)
        for week in cal:
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
        self.data = load_data()
        self.title = "Student Starter Pack"

        root = BoxLayout(orientation="vertical")

        # Top bar
        root.add_widget(TopBar())

        # Screen manager
        self.sm = ScreenManager(transition=NoTransition(), size_hint_y=1)
        screens = [
            ("home",     HomeScreen),
            ("schedule", ScheduleScreen),
            ("exams",    ExamsScreen),
            ("tasks",    TasksScreen),
            ("weather",  WeatherScreen),
        ]
        for name, cls in screens:
            s = cls(app_ref=self, name=name)
            self.sm.add_widget(s)
        root.add_widget(self.sm)

        # Nav bar
        self.nav = NavBar(switch_cb=self.switch_tab)
        root.add_widget(self.nav)

        self.switch_tab("home")
        return root

    def switch_tab(self, tab):
        self.sm.current = tab
        self.nav.set_active(tab)


if __name__ == "__main__":
    StudentApp().run()