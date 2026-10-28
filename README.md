# MarkGUI

**English** | [العربية](#العربية)

A simple desktop app for Windows that converts documents to Markdown. It puts a
friendly window on top of Microsoft's open-source
[MarkItDown](https://github.com/microsoft/markitdown) library, so you never have
to type a command.

> MarkGUI is an independent project. It is **not affiliated with, endorsed by, or
> sponsored by Microsoft**.

## Features

- Drag and drop files or whole folders, or pick them with a button
- PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, XML, EPUB, ZIP and more
- Saves next to the original file, or to a folder you choose
- Per-file status, retry for failed files only, preview and one-click copy
- Light, dark, and automatic (follows Windows) themes
- Arabic (right-to-left, Tajawal font) and English interface
- Installs what it needs automatically on first run

## Quick start (Windows)

1. Download or clone this repository.
2. Double-click **`Run_MarkGUI.bat`**.
   It installs Python (via winget) and the required packages if they are missing,
   then opens the app. The first run can take a few minutes.

Or from a terminal:

```powershell
py -m pip install -r requirements.txt
py markgui.py
```

## Build a standalone .exe

Double-click **`Build_EXE.bat`**. The program is created in `dist\MarkGUI\`.
Keep the whole folder together. The build is large (hundreds of MB) because it
includes Python and the conversion libraries. Unsigned PyInstaller programs are
sometimes flagged by antivirus software; this is a known false-positive issue.

## Notes

- The Arabic font (Tajawal) is downloaded once on first run and used only inside
  the app. Without internet the app falls back to Segoe UI.
- Settings are stored in `%APPDATA%\MarkGUI\settings.json`.
- Files are converted locally on your computer.

## License

MIT, see [LICENSE](LICENSE). Third-party software and licenses are listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

<a id="العربية"></a>

<div dir="rtl">

# MarkGUI

برنامج بسيط لويندوز يحوّل المستندات إلى نص ماركداون. يضع نافذة سهلة فوق مكتبة
[MarkItDown](https://github.com/microsoft/markitdown) مفتوحة المصدر من Microsoft،
فلا تحتاج إلى كتابة أي أمر.

> MarkGUI مشروع مستقل، **غير تابع لشركة Microsoft ولا مدعوم أو معتمد منها**.

## المزايا

- إفلات الملفات أو المجلدات بالسحب، أو اختيارها بزر
- يدعم PDF وWord وPowerPoint وExcel وHTML وCSV وغيرها
- الحفظ بجانب الملف الأصلي أو في مجلد تختاره
- حالة كل ملف، وإعادة المحاولة للفاشل فقط، ومعاينة ونسخ بنقرة
- مظهر فاتح وداكن وتلقائي (يتبع ويندوز)
- واجهة عربية (من اليمين إلى اليسار بخط تجوال) وإنجليزية
- يثبّت ما يحتاجه تلقائيًا عند أول تشغيل

## التشغيل السريع

1. نزّل المشروع.
2. اضغط مرتين على **`Run_MarkGUI.bat`**، فيثبّت Python والحزم المطلوبة إن لزم ثم يفتح البرنامج.

## بناء ملف exe

اضغط مرتين على **`Build_EXE.bat`**، وسيظهر البرنامج في `dist\MarkGUI\`. أبقِ المجلد كاملًا
معًا. حجمه كبير لأنه يحمل Python ومكتبات التحويل، وقد تعلّق عليه برامج الحماية أحيانًا تحذيرًا كاذبًا.

## ملاحظات

- خط تجوال يُحمَّل مرة واحدة في أول تشغيل ويُستخدم داخل البرنامج فقط.
- التحويل يتم محليًا على جهازك.

## الترخيص

MIT، انظر [LICENSE](LICENSE). البرمجيات الخارجية وتراخيصها في
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

</div>
