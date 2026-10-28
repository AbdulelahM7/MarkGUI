# -*- coding: utf-8 -*-
"""MarkGUI - a simple graphical interface for Microsoft's MarkItDown. Arabic / English, light / dark.
Not affiliated with or endorsed by Microsoft."""
import os
import sys
import json
import queue
import threading
import subprocess
import importlib
import ctypes
import urllib.request
import tkinter as tk
from tkinter import filedialog, font as tkfont, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    HAS_DND = False

DATA_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "MarkGUI")
FONT_DIR = os.path.join(DATA_DIR, "fonts")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
MAX_ROWS = 200

EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm", ".csv",
        ".json", ".xml", ".epub", ".zip", ".msg", ".txt"}
FILETYPES_AR = [("الملفات المدعومة", " ".join("*" + e for e in sorted(EXTS))), ("كل الملفات", "*.*")]
FILETYPES_EN = [("Supported files", " ".join("*" + e for e in sorted(EXTS))), ("All files", "*.*")]

FONT_BASE = "https://github.com/google/fonts/raw/main/ofl/tajawal/"
FONT_FILES = ["Tajawal-Regular.ttf", "Tajawal-Bold.ttf"]

# ----------------------------------------------------------------- themes
LIGHT = dict(
    bg="#F5F5F7", surface="#FFFFFF", border="#D6D9DE", dash="#8E959E",
    text="#1D1D1F", text2="#5A6068",
    accent="#0F766E", accent_hover="#0B5F59", accent_press="#084A45", on_accent="#FFFFFF",
    accent_text="#0B645D", soft="#E2F1EF", soft_hover="#D0E8E5",
    ok="#1A7F37", err="#B42318", track="#E3E5E9", seg_sel="#FFFFFF",
    disabled_bg="#E6E8EB", disabled_fg="#5F666D", focus="#0F766E", scroll="#C3C7CD", dark=False)
DARK = dict(
    bg="#131416", surface="#1C1E21", border="#33373C", dash="#7A828B",
    text="#F5F5F7", text2="#A4AAB2",
    accent="#2DD4BF", accent_hover="#5EEAD4", accent_press="#14B8A6", on_accent="#052E2A",
    accent_text="#5EEAD4", soft="#1B3532", soft_hover="#234440",
    ok="#4ADE80", err="#FF8F85", track="#2A2D31", seg_sel="#3A3E44",
    disabled_bg="#2A2D31", disabled_fg="#9AA0A8", focus="#5EEAD4", scroll="#4A4F56", dark=True)
THEMES = {"light": LIGHT, "dark": DARK}

# ----------------------------------------------------------------- strings
STR = {
    "en": dict(
        subtitle="Turn your documents into Markdown",
        dz_title="Drop your files here", dz_title_nodnd="Add your files to begin",
        dz_sub="Documents, presentations, spreadsheets, web pages and more",
        dz_compact="Drop more files here",
        choose_files="Choose files", choose_folder="Choose folder",
        clear="Clear all", save_to="Save to", loc_same="Next to the original files",
        loc_choose="Choose a folder…", convert="Convert", preparing="Preparing…",
        first_run="Installing the conversion engine for the first time. This can take a few minutes.",
        add_to_start="Add files to get started", ready_n="Ready to convert {files}",
        converting="Converting {i} of {n}…", done_ok="Converted {files}",
        done_mixed="Converted {ok}, {fail} could not be converted",
        open_folder="Open folder", preview="Preview", copy="Copy text", copied="Copied",
        auto="Auto", light="Light", dark="Dark", remove="Remove",
        install_failed="Setup failed. Check your internet connection and reopen the app."),
    "ar": dict(
        subtitle="حوّل ملفاتك إلى نص ماركداون",
        dz_title="أفلت ملفاتك هنا", dz_title_nodnd="أضف ملفاتك للبدء",
        dz_sub="مستندات وعروض تقديمية وجداول وصفحات ويب وغيرها",
        dz_compact="أفلت المزيد من الملفات هنا",
        choose_files="اختيار ملفات", choose_folder="اختيار مجلد",
        clear="مسح الكل", save_to="مكان الحفظ", loc_same="بجانب الملفات الأصلية",
        loc_choose="اختيار مجلد…", convert="تحويل", preparing="جارٍ التحضير…",
        first_run="جارٍ تثبيت أداة التحويل لأول مرة، وقد يستغرق ذلك بضع دقائق.",
        add_to_start="أضف ملفات لتبدأ", ready_n="جاهز لتحويل {files}",
        converting="جارٍ تحويل {i} من {n}…", done_ok="تم تحويل {files}",
        done_mixed="تم تحويل {ok}، وتعذّر تحويل {fail}",
        open_folder="فتح المجلد", preview="معاينة", copy="نسخ النص", copied="تم النسخ",
        auto="تلقائي", light="فاتح", dark="داكن", remove="إزالة",
        install_failed="تعذّر التثبيت. تحقق من الإنترنت ثم أعد فتح البرنامج."),
}


def nfiles(lang, n):
    if lang == "ar":
        if n == 1:
            return "ملف واحد"
        if n == 2:
            return "ملفان"
        if 3 <= n <= 10:
            return f"{n} ملفات"
        return f"{n} ملفًا"
    return "1 file" if n == 1 else f"{n} files"


# ----------------------------------------------------------------- helpers
def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(d):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
    except Exception:
        pass


def system_is_dark():
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
    except Exception:
        return False


def default_lang():
    try:
        if (ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF) == 0x01:
            return "ar"
    except Exception:
        pass
    return "en"


def ensure_fonts():
    """Download Tajawal (SIL OFL) once and register it for this process only."""
    if os.name != "nt":
        return
    try:
        os.makedirs(FONT_DIR, exist_ok=True)
    except Exception:
        return
    for name in FONT_FILES:
        path = os.path.join(FONT_DIR, name)
        if not os.path.exists(path):
            try:
                with urllib.request.urlopen(FONT_BASE + name, timeout=8) as r:
                    data = r.read()
                if len(data) > 10000:
                    tmp = path + ".part"
                    with open(tmp, "wb") as f:
                        f.write(data)
                    os.replace(tmp, path)
            except Exception:
                continue
        try:
            ctypes.windll.gdi32.AddFontResourceExW(path, 0x10, 0)  # FR_PRIVATE
        except Exception:
            pass


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def rr(x1, y1, x2, y2, r):
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


def unique_path(path):
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(path):
        path = f"{base}_{n}{ext}"
        n += 1
    return path


# ----------------------------------------------------------------- widgets
class Btn(tk.Canvas):
    """Rounded button: kinds primary / tint / plain. Keyboard focusable."""

    def __init__(self, master, app, text, command, kind="tint", h=38, minw=0, bg=None, bold=True):
        self.app, self.text, self.command, self.kind = app, text, command, kind
        self.f = app.font(11, bold)
        self.enabled, self.hover, self.down, self.focus = True, False, False, False
        w = max(minw, self.f.measure(text) + app.px(32))
        super().__init__(master, width=w, height=app.px(h), bg=bg or app.T["bg"],
                         highlightthickness=0, bd=0, takefocus=1, cursor="hand2")
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, down=False))
        self.bind("<ButtonPress-1>", lambda e: self._set(down=True))
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<FocusIn>", lambda e: self._set(focus=True))
        self.bind("<FocusOut>", lambda e: self._set(focus=False))
        self.bind("<Return>", self._invoke)
        self.bind("<space>", self._invoke)
        self.bind("<Configure>", lambda e: self.draw())
        self.draw()

    def _set(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.draw()

    def _release(self, _e):
        fire = self.down and self.hover and self.enabled
        self._set(down=False)
        if fire:
            self.app.root.after(1, self.command)

    def _invoke(self, _e=None):
        if self.enabled:
            self.app.root.after(1, self.command)

    def set_enabled(self, on):
        self.enabled = on
        self.config(cursor="hand2" if on else "arrow", takefocus=1 if on else 0)
        self.draw()

    def set_text(self, text):
        self.text = text
        self.config(width=max(int(self["width"]), self.f.measure(text) + self.app.px(32)))
        self.draw()

    def draw(self):
        T = self.app.T
        self.delete("all")
        w, h = max(self.winfo_width(), int(self["width"])), int(self["height"])
        if not self.enabled:
            fill, fg = T["disabled_bg"], T["disabled_fg"]
        elif self.kind == "primary":
            fill = T["accent_press"] if self.down else (T["accent_hover"] if self.hover else T["accent"])
            fg = T["on_accent"]
        elif self.kind == "tint":
            fill = T["soft_hover"] if (self.hover or self.down) else T["soft"]
            fg = T["accent_text"]
        else:
            fill = T["soft"] if (self.hover or self.down) else ""
            fg = T["accent_text"]
        r = min(self.app.px(10), h // 2)
        if fill:
            self.create_polygon(rr(1, 1, w - 1, h - 1, r), smooth=True, fill=fill, outline=fill)
        if self.focus and self.enabled:
            self.create_polygon(rr(2, 2, w - 2, h - 2, r), smooth=True, fill="", outline=T["focus"], width=2)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg, font=self.f)


class Seg(tk.Canvas):
    """Segmented control. `options` is in visual (left to right) order."""

    def __init__(self, master, app, options, value, command, bg):
        self.app, self.options, self.value, self.command = app, options, value, command
        self.f = app.font(10)
        pad, self.m = app.px(13), app.px(3)
        self.ws = [self.f.measure(label) + 2 * pad for _k, label in options]
        super().__init__(master, width=sum(self.ws) + 2 * self.m, height=app.px(32), bg=bg,
                         highlightthickness=0, bd=0, takefocus=1, cursor="hand2")
        self.focus = False
        self.bind("<Button-1>", self._click)
        self.bind("<FocusIn>", lambda e: self._set_focus(True))
        self.bind("<FocusOut>", lambda e: self._set_focus(False))
        self.bind("<Left>", lambda e: self._step(-1))
        self.bind("<Right>", lambda e: self._step(1))
        self.draw()

    def _set_focus(self, v):
        self.focus = v
        self.draw()

    def _select(self, key):
        if key != self.value:
            self.value = key
            self.draw()
            self.app.root.after(1, lambda: self.command(key))

    def _click(self, e):
        x = self.m
        for (k, _l), cw in zip(self.options, self.ws):
            if x <= e.x < x + cw:
                self._select(k)
                return
            x += cw

    def _step(self, d):
        keys = [k for k, _ in self.options]
        i = keys.index(self.value) + d
        if 0 <= i < len(keys):
            self._select(keys[i])

    def draw(self):
        T = self.app.T
        self.delete("all")
        w, h, m = int(self["width"]), int(self["height"]), self.m
        r = self.app.px(9)
        self.create_polygon(rr(0, 0, w, h, r), smooth=True, fill=T["track"], outline=T["track"])
        x = m
        for (k, label), cw in zip(self.options, self.ws):
            sel = k == self.value
            if sel:
                self.create_polygon(rr(x, m, x + cw, h - m, r - 2), smooth=True,
                                    fill=T["seg_sel"], outline=T["seg_sel"])
            self.create_text(x + cw / 2, h / 2, text=label, font=self.f,
                             fill=T["text"] if sel else T["text2"])
            x += cw
        if self.focus:
            self.create_polygon(rr(1, 1, w - 1, h - 1, r), smooth=True, fill="",
                                outline=T["focus"], width=2)


# ----------------------------------------------------------------- app
class App:
    def __init__(self, root):
        self.root = root
        root.title("MarkGUI")
        self.scale = max(1.0, root.winfo_fpixels("1i") / 96.0)
        root.geometry(f"{self.px(800)}x{self.px(740)}")
        root.minsize(self.px(660), self.px(620))

        cfg = load_settings()
        self.lang = cfg.get("lang") if cfg.get("lang") in STR else default_lang()
        self.theme_pref = cfg.get("theme") if cfg.get("theme") in ("auto", "light", "dark") else "auto"
        od = cfg.get("out_dir", "")
        self.out_dir = od if od and os.path.isdir(od) else ""
        try:
            self.has_tajawal = "Tajawal" in tkfont.families(root)
        except Exception:
            self.has_tajawal = False

        self.files, self.row_state, self.row_widgets = [], {}, {}
        self.results, self.last_target_dir = {}, ""
        self.state, self.setup_key = "setup", "preparing"
        self.prog, self.progress_val, self.last_done = (0, 0), 0.0, None
        self.q, self.md, self.fonts = queue.Queue(), None, {}
        self.list_canvas = None
        self.sys_dark = system_is_dark()
        self.tick = 0

        root.bind_all("<MouseWheel>", self.on_wheel)
        root.bind_all("<Control-o>", lambda e: self.choose_files())
        self.render()
        root.after(120, self.poll)
        threading.Thread(target=self.setup_worker, daemon=True).start()

    # ---- basics
    @property
    def S(self):
        return STR[self.lang]

    def px(self, n):
        return int(round(n * self.scale))

    def font(self, size, bold=False):
        ar = self.lang == "ar"
        key = (size, bold, ar)
        if key not in self.fonts:
            fam = "Tajawal" if (ar and self.has_tajawal) else ("Segoe UI" if os.name == "nt" else "TkDefaultFont")
            self.fonts[key] = tkfont.Font(family=fam, size=size + (1 if ar else 0),
                                          weight="bold" if bold else "normal")
        return self.fonts[key]

    def effective_theme(self):
        if self.theme_pref == "auto":
            return "dark" if self.sys_dark else "light"
        return self.theme_pref

    def apply_titlebar(self, win):
        if os.name != "nt":
            return
        try:
            win.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
            v = ctypes.c_int(1 if self.T["dark"] else 0)
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
        except Exception:
            pass

    def style_ttk(self):
        T = self.T
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.layout("Vertical.TScrollbar",
                  [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
                      ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
        st.configure("Vertical.TScrollbar", background=T["scroll"], troughcolor=T["surface"],
                     bordercolor=T["surface"], lightcolor=T["scroll"], darkcolor=T["scroll"],
                     relief="flat", width=self.px(10), arrowsize=self.px(10), gripcount=0)
        st.map("Vertical.TScrollbar", background=[("active", T["text2"])])

    def request_render(self):
        self.root.after(1, self.render)

    # ---- render
    def render(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Toplevel):
                w.destroy()
        self.list_canvas = None
        self.row_widgets = {}
        T = self.T = THEMES[self.effective_theme()]
        S, px = self.S, self.px
        self.rtl = self.lang == "ar"
        self.lead, self.trail = ("right", "left") if self.rtl else ("left", "right")
        self.a_lead = "e" if self.rtl else "w"
        self.j_lead = "right" if self.rtl else "left"
        self.root.configure(bg=T["bg"])
        self.style_ttk()
        self.apply_titlebar(self.root)
        mx = px(28)

        # header
        hdr = tk.Frame(self.root, bg=T["bg"])
        hdr.pack(side="top", fill="x", padx=mx, pady=(px(22), px(6)))
        tb = tk.Frame(hdr, bg=T["bg"])
        tb.pack(side=self.lead)
        tk.Label(tb, text="MarkGUI", font=self.font(20, True), bg=T["bg"],
                 fg=T["text"]).pack(anchor=self.a_lead)
        tk.Label(tb, text=S["subtitle"], font=self.font(11), bg=T["bg"], fg=T["text2"],
                 justify=self.j_lead).pack(anchor=self.a_lead)
        ctl = tk.Frame(hdr, bg=T["bg"])
        ctl.pack(side=self.trail)
        langs = [("en", "English"), ("ar", "عربي")]
        themes = [("auto", S["auto"]), ("light", S["light"]), ("dark", S["dark"])]
        if self.rtl:
            langs, themes = langs[::-1], themes[::-1]
        Seg(ctl, self, themes, self.theme_pref, self.set_theme, T["bg"]).pack(side=self.lead, padx=px(4))
        Seg(ctl, self, langs, self.lang, self.set_lang, T["bg"]).pack(side=self.lead, padx=px(4))

        # footer
        ft = tk.Frame(self.root, bg=T["bg"])
        ft.pack(side="bottom", fill="x", padx=mx, pady=(px(10), px(22)))
        sr = tk.Frame(ft, bg=T["bg"])
        sr.pack(fill="x")
        if self.results:
            Btn(sr, self, S["preview"], self.open_preview, kind="plain", h=34, bg=T["bg"]).pack(side=self.trail)
            Btn(sr, self, S["open_folder"], self.open_output, kind="plain", h=34, bg=T["bg"]).pack(side=self.trail)
        text, tone = self.status_text()
        self.status_lbl = tk.Label(sr, text=text, font=self.font(11), bg=T["bg"], anchor=self.a_lead,
                                   justify=self.j_lead, wraplength=px(470),
                                   fg={"normal": T["text2"], "ok": T["ok"], "err": T["err"]}[tone])
        self.status_lbl.pack(side=self.lead)
        self.pbar = tk.Canvas(ft, height=px(6), bg=T["bg"], highlightthickness=0, bd=0)
        self.pbar.pack(fill="x", pady=(px(8), px(14)))
        self.pbar.bind("<Configure>", lambda e: self.draw_progress())
        ar = tk.Frame(ft, bg=T["bg"])
        ar.pack(fill="x")
        sv = tk.Frame(ar, bg=T["bg"])
        sv.pack(side=self.lead)
        tk.Label(sv, text=S["save_to"], font=self.font(11), bg=T["bg"], fg=T["text2"]).pack(
            side=self.lead, padx=(px(6), 0) if self.rtl else (0, px(6)))
        loc = S["loc_same"] if not self.out_dir else (os.path.basename(self.out_dir.rstrip("\\/")) or self.out_dir)
        self.loc_btn = Btn(sv, self, loc + "  ▾", self.show_loc_menu, kind="plain", h=36, bg=T["bg"], bold=False)
        self.loc_btn.pack(side=self.lead)
        label = S["preparing"] if self.state == "setup" else S["convert"]
        self.convert_btn = Btn(ar, self, label, self.start_convert, kind="primary", h=46,
                               minw=px(170), bg=T["bg"])
        self.convert_btn.pack(side=self.trail)
        self.update_controls()

        # body
        body = tk.Frame(self.root, bg=T["bg"])
        body.pack(side="top", fill="both", expand=True, padx=mx, pady=(px(8), 0))
        self.build_dropzone(body)
        if self.files:
            self.build_list(body)

    # ---- drop zone
    def build_dropzone(self, parent):
        T, S, px = self.T, self.S, self.px
        compact = bool(self.files)
        cv = tk.Canvas(parent, height=px(104) if compact else px(260), bg=T["bg"],
                       highlightthickness=0, bd=0, cursor="hand2")
        if compact:
            cv.pack(fill="x")
        else:
            cv.pack(fill="both", expand=True)
        inner = tk.Frame(cv, bg=T["surface"])
        win = cv.create_window(0, 0, window=inner, anchor="center")
        hot = {"v": False}

        def redraw(_e=None):
            w, h = cv.winfo_width(), cv.winfo_height()
            cv.delete("bg")
            col = T["accent"] if hot["v"] else T["dash"]
            cv.create_polygon(rr(2, 2, w - 2, h - 2, px(18)), smooth=True, fill=T["soft"] if hot["v"] else T["surface"],
                              outline=col, width=2, dash=(7, 5), tags="bg")
            cv.tag_lower("bg")
            cv.coords(win, w / 2, h / 2)
            inner.config(bg=T["soft"] if hot["v"] else T["surface"])
            for c in inner.winfo_children():
                if isinstance(c, tk.Label):
                    c.config(bg=inner["bg"])

        cv.bind("<Configure>", redraw)
        sbg = T["surface"]
        title = S["dz_compact"] if compact else (S["dz_title"] if HAS_DND else S["dz_title_nodnd"])
        if not compact:
            badge = tk.Canvas(inner, width=px(60), height=px(60), bg=sbg, highlightthickness=0, bd=0)
            badge.create_polygon(rr(2, 2, px(58), px(58), px(16)), smooth=True, fill=T["soft"], outline=T["soft"])
            badge.create_text(px(30), px(30), text="MD", font=self.font(15, True), fill=T["accent_text"])
            badge.pack(pady=(0, px(12)))
            tk.Label(inner, text=title, font=self.font(15, True), bg=sbg, fg=T["text"]).pack()
            tk.Label(inner, text=S["dz_sub"], font=self.font(11), bg=sbg, fg=T["text2"]).pack(pady=(px(4), px(16)))
            row = tk.Frame(inner, bg=sbg)
            row.pack()
        else:
            row = tk.Frame(inner, bg=sbg)
            row.pack()
            tk.Label(row, text=title, font=self.font(12, True), bg=sbg, fg=T["text"]).pack(
                side=self.lead, padx=px(12))
        Btn(row, self, S["choose_files"], self.choose_files, kind="primary", h=40, bg=sbg).pack(
            side=self.lead, padx=px(5))
        Btn(row, self, S["choose_folder"], self.choose_folder, kind="tint", h=40, bg=sbg).pack(
            side=self.lead, padx=px(5))

        for w in (cv, inner):
            w.bind("<Button-1>", lambda e: self.choose_files())
        if HAS_DND:
            def enter(e):
                hot["v"] = True
                redraw()
                return e.action

            def leave(e):
                hot["v"] = False
                redraw()
                return e.action

            def drop(e):
                hot["v"] = False
                self.add_paths(self.root.tk.splitlist(e.data))
                return e.action
            for w in (cv, inner):
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<DropEnter>>", enter)
                w.dnd_bind("<<DropLeave>>", leave)
                w.dnd_bind("<<Drop>>", drop)

    # ---- file list
    def build_list(self, parent):
        T, S, px = self.T, self.S, self.px
        sf = T["surface"]
        card = tk.Frame(parent, bg=sf, highlightbackground=T["border"], highlightcolor=T["border"],
                        highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(px(14), 0))
        head = tk.Frame(card, bg=sf)
        head.pack(fill="x", padx=px(16), pady=(px(8), px(4)))
        tk.Label(head, text=nfiles(self.lang, len(self.files)), font=self.font(11, True),
                 bg=sf, fg=T["text"]).pack(side=self.lead)
        Btn(head, self, S["clear"], self.clear_files, kind="plain", h=32, bg=sf).pack(side=self.trail)
        tk.Frame(card, height=1, bg=T["border"]).pack(fill="x")
        wrap = tk.Frame(card, bg=sf)
        wrap.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical", style="Vertical.TScrollbar")
        sb.pack(side=self.trail, fill="y")
        cv = tk.Canvas(wrap, bg=sf, highlightthickness=0, bd=0, yscrollcommand=sb.set)
        cv.pack(side=self.lead, fill="both", expand=True)
        sb.config(command=cv.yview)
        inner = tk.Frame(cv, bg=sf)
        win = cv.create_window(0, 0, window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfigure(win, width=e.width))
        self.list_canvas = cv

        for path in self.files[:MAX_ROWS]:
            row = tk.Frame(inner, bg=sf)
            row.pack(fill="x")
            rm = tk.Label(row, text="✕", font=self.font(10), bg=sf, fg=T["text2"], cursor="hand2",
                          width=3, takefocus=1, highlightthickness=1, highlightbackground=sf,
                          highlightcolor=T["focus"])
            rm.pack(side=self.trail, padx=(px(4), px(10)))
            rm.bind("<Button-1>", lambda e, p=path: self.remove_file(p))
            rm.bind("<Return>", lambda e, p=path: self.remove_file(p))
            rm.bind("<space>", lambda e, p=path: self.remove_file(p))
            rm.bind("<Enter>", lambda e, w=rm: w.config(fg=T["err"]))
            rm.bind("<Leave>", lambda e, w=rm: w.config(fg=T["text2"]))
            st = tk.Label(row, text="", font=self.font(10), bg=sf, fg=T["text2"])
            st.pack(side=self.trail)
            tk.Label(row, text=os.path.basename(path), font=self.font(11), bg=sf, fg=T["text"],
                     anchor=self.a_lead, justify=self.j_lead).pack(
                side=self.lead, fill="x", expand=True, padx=px(16), pady=px(8))
            self.row_widgets[path] = st
            self.apply_row_status(path)
        if len(self.files) > MAX_ROWS:
            tk.Label(inner, text=f"+ {len(self.files) - MAX_ROWS}", font=self.font(10), bg=sf,
                     fg=T["text2"]).pack(pady=px(8))

    def apply_row_status(self, path):
        st = self.row_widgets.get(path)
        if not st:
            return
        T = self.T
        state, msg = self.row_state.get(path, ("pending", ""))
        text, color = {"pending": ("", T["text2"]), "run": ("…", T["text2"]),
                       "ok": ("✓", T["ok"]), "err": ("✗ " + msg[:42], T["err"])}[state]
        try:
            st.config(text=text, fg=color)
        except tk.TclError:
            pass

    def on_wheel(self, e):
        cv = self.list_canvas
        if not cv:
            return
        try:
            w = self.root.winfo_containing(e.x_root, e.y_root)
            if w is not None and str(w).startswith(str(cv)):
                cv.yview_scroll(int(-e.delta / 120), "units")
        except Exception:
            pass

    # ---- status
    def pending_files(self):
        return [f for f in self.files if self.row_state.get(f, ("pending",))[0] != "ok"]

    def status_text(self):
        S = self.S
        if self.state == "setup":
            return S[self.setup_key], "normal"
        if self.state == "fatal":
            return S["install_failed"], "err"
        if self.state == "busy":
            return S["converting"].format(i=self.prog[0], n=self.prog[1]), "normal"
        if self.last_done is not None:
            ok, fail = self.last_done
            if fail:
                return S["done_mixed"].format(ok=nfiles(self.lang, ok), fail=nfiles(self.lang, fail)), "err"
            return S["done_ok"].format(files=nfiles(self.lang, ok)), "ok"
        pend = self.pending_files()
        if pend:
            return S["ready_n"].format(files=nfiles(self.lang, len(pend))), "normal"
        return S["add_to_start"], "normal"

    def update_controls(self):
        T = self.T
        text, tone = self.status_text()
        try:
            self.status_lbl.config(text=text, fg={"normal": T["text2"], "ok": T["ok"], "err": T["err"]}[tone])
            can = self.state == "idle" and bool(self.pending_files())
            self.convert_btn.set_enabled(can)
            self.convert_btn.set_text(self.S["preparing"] if self.state == "setup" else
                                      (self.S["converting"].format(i=self.prog[0], n=self.prog[1])
                                       if self.state == "busy" else self.S["convert"]))
        except tk.TclError:
            pass
        self.draw_progress()

    def draw_progress(self):
        try:
            T, cv = self.T, self.pbar
            cv.delete("all")
            w, h = cv.winfo_width(), cv.winfo_height()
            r = h // 2
            cv.create_polygon(rr(0, 0, w, h, r), smooth=True, fill=T["track"], outline=T["track"])
            fw = int(w * self.progress_val)
            if fw > h:
                cv.create_polygon(rr(0, 0, fw, h, r), smooth=True, fill=T["accent"], outline=T["accent"])
        except tk.TclError:
            pass

    # ---- settings
    def persist(self):
        save_settings({"lang": self.lang, "theme": self.theme_pref, "out_dir": self.out_dir})

    def set_lang(self, lang):
        self.lang = lang
        self.persist()
        self.request_render()

    def set_theme(self, theme):
        self.theme_pref = theme
        self.persist()
        self.request_render()

    def show_loc_menu(self):
        m = tk.Menu(self.root, tearoff=0, font=self.font(10))
        m.add_command(label=self.S["loc_same"], command=self.set_out_same)
        m.add_command(label=self.S["loc_choose"], command=self.choose_out)
        m.tk_popup(self.loc_btn.winfo_rootx(), self.loc_btn.winfo_rooty() + self.loc_btn.winfo_height())

    def set_out_same(self):
        self.out_dir = ""
        self.persist()
        self.request_render()

    def choose_out(self):
        d = filedialog.askdirectory(title=self.S["loc_choose"].rstrip("…"))
        if d:
            self.out_dir = os.path.normpath(d)
            self.persist()
            self.request_render()

    # ---- files
    def add_paths(self, paths):
        added = False
        for p in paths:
            p = os.path.normpath(p)
            if os.path.isdir(p):
                for dp, _, fns in os.walk(p):
                    for fn in sorted(fns):
                        fp = os.path.join(dp, fn)
                        if os.path.splitext(fn)[1].lower() in EXTS and fp not in self.files:
                            self.files.append(fp)
                            added = True
            elif os.path.isfile(p) and p not in self.files:
                self.files.append(p)
                added = True
        if added:
            self.last_done = None
            self.progress_val = 0.0
            self.request_render()

    def choose_files(self):
        if self.state == "busy":
            return
        ft = FILETYPES_AR if self.lang == "ar" else FILETYPES_EN
        paths = filedialog.askopenfilenames(title=self.S["choose_files"], filetypes=ft)
        if paths:
            self.add_paths(paths)

    def choose_folder(self):
        if self.state == "busy":
            return
        d = filedialog.askdirectory(title=self.S["choose_folder"])
        if d:
            self.add_paths([d])

    def remove_file(self, path):
        if self.state == "busy":
            return
        if path in self.files:
            self.files.remove(path)
            self.row_state.pop(path, None)
            self.results.pop(path, None)
            self.last_done = None
            self.request_render()

    def clear_files(self):
        if self.state == "busy":
            return
        self.files.clear()
        self.row_state.clear()
        self.results.clear()
        self.last_done = None
        self.progress_val = 0.0
        self.request_render()

    # ---- setup + convert workers
    def setup_worker(self):
        try:
            try:
                importlib.import_module("markitdown")
            except ImportError:
                if getattr(sys, "frozen", False):  # inside the .exe nothing can be pip-installed
                    self.q.put(("fatal", None))
                    return
                self.q.put(("setup_key", "first_run"))
                cmd = [sys.executable, "-m", "pip", "install", "-U", "--disable-pip-version-check", "markitdown[all]"]
                proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=NO_WINDOW)
                if proc.returncode != 0:
                    self.q.put(("fatal", None))
                    return
                importlib.invalidate_caches()
            from markitdown import MarkItDown
            self.md = MarkItDown()
            self.q.put(("ready", None))
        except Exception:
            self.q.put(("fatal", None))

    def start_convert(self):
        pend = self.pending_files()
        if self.state != "idle" or not pend:
            return
        self.state = "busy"
        self.prog = (0, len(pend))
        self.progress_val = 0.0
        self.last_done = None
        for p in pend:
            self.row_state[p] = ("pending", "")
            self.apply_row_status(p)
        self.update_controls()
        threading.Thread(target=self.convert_worker, args=(pend, self.out_dir), daemon=True).start()

    def convert_worker(self, files, out_dir):
        ok = fail = 0
        for i, f in enumerate(files, 1):
            self.q.put(("row", (f, "run", "")))
            self.q.put(("prog", (i, len(files), False)))
            try:
                text = self.md.convert(f).text_content
                name = os.path.splitext(os.path.basename(f))[0] + ".md"
                folder = out_dir or os.path.dirname(f)
                target = unique_path(os.path.join(folder, name))
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write(text)
                self.q.put(("result", (f, target, text)))
                self.q.put(("row", (f, "ok", "")))
                ok += 1
            except Exception as e:
                self.q.put(("row", (f, "err", str(e).replace("\n", " "))))
                fail += 1
            self.q.put(("prog", (i, len(files), True)))
        self.q.put(("finished", (ok, fail)))

    def poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "setup_key":
                    self.setup_key = data
                    self.update_controls()
                elif kind == "ready":
                    self.state = "idle"
                    self.update_controls()
                elif kind == "fatal":
                    self.state = "fatal"
                    self.update_controls()
                elif kind == "row":
                    self.row_state[data[0]] = (data[1], data[2])
                    self.apply_row_status(data[0])
                elif kind == "prog":
                    i, n, done = data
                    self.prog = (i, n)
                    self.progress_val = (i if done else i - 1) / max(n, 1)
                    self.update_controls()
                elif kind == "result":
                    self.results[data[0]] = (data[1], data[2])
                    self.last_target_dir = os.path.dirname(data[1])
                elif kind == "finished":
                    self.state = "idle"
                    self.last_done = data
                    self.progress_val = 1.0
                    self.request_render()
        except queue.Empty:
            pass
        self.tick += 1
        if self.tick % 20 == 0 and self.theme_pref == "auto":
            d = system_is_dark()
            if d != self.sys_dark:
                self.sys_dark = d
                self.request_render()
        self.root.after(100, self.poll)

    # ---- output / preview
    def open_output(self):
        d = self.out_dir or self.last_target_dir
        if d and os.path.isdir(d):
            if os.name == "nt":
                os.startfile(d)
            else:
                subprocess.run(["xdg-open", d])

    def open_preview(self):
        if not self.results:
            return
        T, S, px = self.T, self.S, self.px
        win = tk.Toplevel(self.root)
        win.title(S["preview"])
        win.geometry(f"{px(820)}x{px(540)}")
        win.configure(bg=T["bg"])
        self.apply_titlebar(win)
        top = tk.Frame(win, bg=T["bg"])
        top.pack(fill="x", padx=px(16), pady=px(12))
        body = tk.Frame(win, bg=T["bg"])
        body.pack(fill="both", expand=True, padx=px(16), pady=(0, px(16)))
        items = list(self.results.items())
        lb = tk.Listbox(body, width=26, bg=T["surface"], fg=T["text"], font=self.font(10),
                        selectbackground=T["soft"], selectforeground=T["accent_text"],
                        highlightthickness=1, highlightbackground=T["border"], highlightcolor=T["focus"],
                        relief="flat", bd=0, activestyle="none", exportselection=False)
        for src, _v in items:
            lb.insert("end", os.path.basename(src))
        lb.pack(side=self.lead, fill="y", padx=(px(10), 0) if self.rtl else (0, px(10)))
        tf = tk.Frame(body, bg=T["surface"], highlightbackground=T["border"], highlightthickness=1)
        tf.pack(side=self.lead, fill="both", expand=True)
        sb = ttk.Scrollbar(tf, orient="vertical", style="Vertical.TScrollbar")
        sb.pack(side=self.trail, fill="y")
        txt = tk.Text(tf, wrap="word", bg=T["surface"], fg=T["text"], insertbackground=T["text"],
                      relief="flat", bd=0, padx=px(12), pady=px(10), yscrollcommand=sb.set,
                      font=("Consolas", 10) if os.name == "nt" else "TkFixedFont",
                      selectbackground=T["soft_hover"], selectforeground=T["text"])
        txt.pack(side=self.lead, fill="both", expand=True)
        sb.config(command=txt.yview)

        def show(_e=None):
            sel = lb.curselection()
            if sel:
                txt.config(state="normal")
                txt.delete("1.0", "end")
                txt.insert("1.0", items[sel[0]][1][1])
                txt.config(state="disabled")
        lb.bind("<<ListboxSelect>>", show)
        lb.selection_set(0)
        show()

        def do_copy():
            sel = lb.curselection()
            if sel:
                win.clipboard_clear()
                win.clipboard_append(items[sel[0]][1][1])
                cbtn.set_text(S["copied"])
                win.after(1500, lambda: cbtn.winfo_exists() and cbtn.set_text(S["copy"]))
        cbtn = Btn(top, self, S["copy"], do_copy, kind="tint", h=36, bg=T["bg"])
        cbtn.pack(side=self.trail)
        win.bind("<Escape>", lambda e: win.destroy())


def main():
    if os.name == "nt":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    ensure_fonts()  # must run before Tk starts so the font is visible to it
    root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
