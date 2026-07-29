# Telegram ↔ Antigravity PC 2-Way Bridge Specification

Dokumen ini mendokumentasikan spesifikasi arsitektur, mekanisme injeksi, bypass CDP, dan aturan core untuk integrasi 2-arah antara Telegram (HP) dan Antigravity (PC).

---

## 📌 Core Rules & Technical Architecture

### 1. Zero-Coordinate CDP Navigation & Tab Switching
- **Aturan**: Jangan mengandalkan koordinat mouse piksel statis (`X, Y`) atau OS mouse click untuk navigasi tab sidebar Antigravity.
- **Solusi**: Gunakan Chrome DevTools Protocol (CDP) DOM execution via `element.click()` pada selector target (misal `div.flex.flex-col.gap-px.mb-1` untuk `Wahyu's PC`).
- **Alasan**: Electron memblokir OS mouse input ketika Antigravity berada dalam kondisi BUSY (sedang generate respon AI). CDP JS injection dapat mengeksekusi navigasi tab secara instan tanpa terhalang UI input lock.

### 2. CDP Raw Socket WebSocket Bypass (403 Forbidden Fix)
- **Aturan**: Jangan memakai library WebSocket standar yang mengirimkan header `Origin: ...` saat menyambung ke CDP port Electron.
- **Solusi**: Sambungkan via raw TCP socket (`socket.socket()`) dan kirimkan HTTP Upgrade Request tanpa `Origin` header.
- **Detail Teknis**:
  - **CDP Listener**: `127.0.0.1:<PORT>` (Auto-detected via `psutil` & `/json/version`)
  - **Handshake**: Handshake HTTP raw `GET /devtools/page/... HTTP/1.1`
  - **Bypass Result**: Mengembalikan `101 Switching Protocols` (memutus blokir 403 Forbidden).

### 3. Single-Shot Single-Exec Prompt Injection
- **Aturan**: Prompt dari Telegram HP harus terinjeksi dan ter-submit dalam 1x pengiriman tanpa membutuhkan pesan kedua (`?`) atau enter manual.
- **Solusi**: 
  1. Fokuskan editor `div[contenteditable="true"]`.
  2. Eksekusi `document.execCommand('insertText', false, text)` via CDP.
  3. Berikan penundaan 200ms `await new Promise(r => setTimeout(r, 200))` agar React merender tombol submit.
  4. Klik tombol submit via `button[aria-label*="Send"]`.

### 4. Input Area Exclusion (No Drafting Spam)
- **Aturan**: Scraper mirror DOM di PC tidak boleh membaca elemen di dalam `[contenteditable="true"]` atau container `inputArea`.
- **Alasan**: Mencegah draf ketikan di PC terkirim sebagai pesan spam ke Telegram HP sebelum pengguna menekan tombol Submit.

### 5. Presisi MD5 Hash Duplicate Prevention & Message ID Deduplication
- **Aturan**: Setiap pesan dari Telegram HP harus dicatat hash MD5-nya di `injected_hashes.json` dan `injected_prompts.txt` (mencakup raw text & formatted prompt) dengan newlines yang dinormalisasi (`\r\n` → `\n`).
- **Telegram Message ID Deduplication**: Setiap `message_id` Telegram dilacak di memory buffer. Jika paket jaringan duplikat/retry masuk dari HP, paket duplikat tersebut dibuang secara instan (`is_dup_msg`).
- **Hasil**: Ketika pesan terbaca di DOM PC, mirror memverifikasi hash tersebut. Jika cocok, pesan `You (PC):` LANGSUNG DI-SKIP sehingga tidak pernah ter-echo balik ke Telegram HP.
- **Compare Activity Logging**: Seluruh keputusan recorded di `G:\Antigravity_Server\compare_activity.log`.

### 6. Rich Markdown Formatting & Compact Spacing
- **Aturan**: Teks dari PC dikonversi menggunakan parser `domToMD`.
- **Format**: Mempertahankan `*Bold*`, `_Italic_`, `code blocks`, dan poin list `•`.
- **Spacing**: Menggunakan single-newline (`\n`) untuk bullet list dan paragraf agar tampilan di Telegram HP compact, rapat, dan tidak berjauhan.

### 7. Busy-Aware Full Untruncated AI Response Mirroring & Smart Text Cleaner
- **Aturan**: Jangan menscrape atau mengunci hash jawaban AI saat AI masih mengetik (parsial).
- **Smart Text Cleaner**: Fungsi `clean_ai_text()` memotong bagian artefak teknis internal (`📌 Catatan Penting`, `📋 Task List`) di bagian paling bawah jawaban, sambil mempertahankan 100% seluruh kesimpulan utama AI sampai kalimat paling akhir.
- **Solusi**:
  - Periksa indikator `isBusy` via CDP (`.animate-spin`, `Stop button`).
  - Saat `isBusy` bernilai `false` (AI selesai mengetik 100%), ambil seluruh teks jawaban.
  - Kirimkan seluruh teks jawaban tanpa batas `substring` menggunakan multi-chunk 3.500 karakter Python.

### 8. Popover Model Switcher & Interactive Telegram Keyboard (`/models`)
- **Aturan**: Pergantian model AI (Gemini Flash, Gemini Pro, Claude Sonnet, Claude Opus, GPT-OSS) dilakukan via CDP tanpa menyentuh mouse fisik PC.
- **Exclusion Filter**: Selector CDP memfilter container chat (`.prose`, `div.leading-relaxed`), menyasar murni menu popover model toolbar di bagian atas PC.
- **Telegram UI**: Menyediakan tombol menu interaktif `🤖 Pilih Model AI` dan slash command shortcut (`/flash`, `/pro`, `/sonnet`, `/opus`, `/gpt`).

### 9. Tray Restore, Chat Activation & Auto-Minimize Flow
- **Aturan**: Tombol `🖥️ Buka Antigravity` memulihkan jendela dari System Tray (`SW_RESTORE`) tanpa menjalankan ulang file `.exe` jika aplikasi sudah berjalan.
- **Flow**:
  1. Restore & Show Window.
  2. Switch tab ke `Wahyu's PC` via CDP (`cdp_click_wahyu()`).
  3. Minimize kembali secara otomatis ke taskbar (`SW_MINIMIZE`) agar tidak mengganggu layar PC.

### 10. Safe Daemon Hot-Reload & Queue Isolation Workflow
- **Aturan**: Seluruh pembaruan script kritis harus diuji terlebih dahulu sebelum melakukan restart daemon secara tertib.
- **Command Isolation**: Rute tombol kontrol bot diisolasi dari antrean `msg_queue` sehingga aktivitas percakapan pengguna yang sedang berjalan di queue tidak pernah terganggu atau terputus saat terjadi pembaruan script.

---

## 🛠️ Service & Daemon Map

| Component | Script Path | Task Scheduler Name |
| :--- | :--- | :--- |
| **Receiver & Queue Worker** | `G:\Antigravity_Server\Bot_Scripts\telegram_bot.py` | `AGY_Bot_Receiver` |
| **DOM Scraper & Mirror** | `G:\Antigravity_Server\Bot_Scripts\dom_mirror_final.py` | `AGY_Bot_Mirror` |
| **CDP Master Controller** | `G:\Antigravity_Server\Bot_Scripts\antigravity_cdp_master.py` | On-demand CLI / Script |
| **Model Switcher Module** | `G:\Antigravity_Server\Bot_Scripts\model_switcher.py` | Standalone CDP Module |
| **Compare Activity Log** | `G:\Antigravity_Server\compare_activity.log` | Real-time Audit Trail |

---

*Dokumen ini diperbarui dan dikonfirmasi pada 24 Juli 2026.*
