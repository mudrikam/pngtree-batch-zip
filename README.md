[![Downloads](https://img.shields.io/github/downloads/mudrikam/pngtree-batch-zip/total?style=for-the-badge&logo=github)](https://github.com/mudrikam/pngtree-batch-zip/releases) [![Release](https://img.shields.io/github/v/release/mudrikam/pngtree-batch-zip?style=for-the-badge&logo=github)](https://github.com/mudrikam/pngtree-batch-zip/releases) ![WhatsApp Group](https://img.shields.io/badge/Join%20WhatsApp-Group-25D366?logo=whatsapp&style=for-the-badge&link=https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3) 

# PNGTREE ZIPPER

Ini alat simpel buat ngezip file aset kayak PSD, AI, EPS, PNG, JPG buat submit ke Pngtree. File yang namanya sama otomatis digabung jadi satu zip. Gampang banget buat para desainer yang mau kirim asset ke sana.

## Fitur

Apa aja yang bisa dilakukan nih tool?
- **Drag and Drop Import**: Seret aja file-file nya langsung ke aplikasi, gak ribet pilih satu-satu.
- **Pengelompokan Otomatis**: File dengan nama sama (misal "logo.psd" dan "logo.png") bakal digabung otomatis ke satu zip. Hemat waktu!
- **Pilih Direktori Output**: Tentuin folder mana yang mau dipake buat nyimpen zip hasilnya.
- **Progress Tracking**: Ada progress bar buat liat seberapa jauh prosesnya, overall dan per file.
- **Menu Aksi**: Import file, pilih folder, set output directory, atau clear data kalau mau mulai ulang.
- **Cross-Platform**: Jalan di Windows, Linux, dan Mac. Gak pilih-pilih OS.
- **UI Sederhana**: UI yang clean dan intuitif, gampang banget dipake tanpa ribet navigasi atau settingan aneh-aneh.

## Instalasi

Cara installnya gini ya, ada dua opsi tergantung platform kamu.

### Opsi 1: Download Executable (Windows & Linux)
Kalau kamu di Windows atau Linux, tinggal download file executable terbaru dari tabel di bawah ini. Download, double-click, dan langsung jalan. Gak perlu install apa-apa lagi.

| Platform | Link Download |
|----------|---------------|
| Windows  | [Download Pngtree_Zipper.exe](https://github.com/mudrikam/pngtree-batch-zip/releases/latest/download/Pngtree_Zipper.exe) |
| Linux    | [Download Pngtree_Zipper](https://github.com/mudrikam/pngtree-batch-zip/releases/latest/download/Pngtree_Zipper) |

### Opsi 2: Clone Repo (Mac & Manual)
Buat yang di Mac atau kalau mau jalanin dari source code (misal buat develop atau customize):

1. Clone repository ini dulu:
   ```
   git clone https://github.com/mudrikam/pngtree-batch-zip.git
   cd pngtree-batch-zip
   ```

2. Pastiin Python 3.10+ udah terinstall. Kalau belum, install dulu. Trus install dependencies:
   ```
   pip install PySide6 qtawesome
   ```

3. Jalankan aplikasi:
   ```
   python pngtree_zipper.py
   ```
   (atau `python3 pngtree_zipper.py` kalau di Mac python defaultnya versi 2).

## Cara Jalankan

Ngejalaninnya simpel banget:
- **Dari Executable**: Tinggal double-click file yang udah didownload. Boom, langsung buka aplikasi. Kalau di Linux, mungkin perlu `chmod +x Pngtree_Zipper` dulu buat bikin executable, trus run via terminal `./Pngtree_Zipper` kalau double-click gak jalan. Kalau kamu pengguna Linux, pasti udah paham dan suka oprek gini kan?
- **Dari Source**: Setelah clone dan install dependencies, jalanin `python pngtree_zipper.py`. Siap pakai!