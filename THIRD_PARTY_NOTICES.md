# Third-party notices

MarkGUI is an independent project. It is **not affiliated with, endorsed by, or
sponsored by Microsoft Corporation**. "MarkItDown" and "Microsoft" are names and
trademarks of their respective owners and are used here only to describe what
this program works with.

MarkGUI uses or can bundle the following software.

---

## MarkItDown

- Project: https://github.com/microsoft/markitdown
- License: MIT
- Used as: the conversion engine (installed with pip, and bundled inside the
  .exe release builds)

```
MIT License

Copyright (c) Microsoft Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Tajawal (font)

- Designed by Boutros Fonts. Copyright (c) 2017 by Boutros International.
- License: SIL Open Font License 1.1 (https://openfontlicense.org)
- Used as: the Arabic interface font. It is **downloaded at first run** from the
  Google Fonts repository and is not included in this repository. If you ever
  bundle the font files, include the full OFL text with them.

## tkinterdnd2

- Project: https://pypi.org/project/tkinterdnd2/
- License: MIT (see the project page for the exact copyright line)
- Used as: drag-and-drop support.

## Build-time tool

- PyInstaller (https://pyinstaller.org) is used only to build the .exe.

---

## Other Python dependencies

`markitdown[all]` installs additional packages (PDF, Word, PowerPoint, Excel,
ONNX runtime, and others), each under its own license. Before publishing an
.exe release, generate the full list and append it here:

```
py -m pip install pip-licenses
py -m piplicenses --format=markdown --with-urls
```
