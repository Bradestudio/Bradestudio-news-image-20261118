# BUILD REPORT — news-image-20261118

Bounty: **"Sum up 18 November's world news in one image"**
(slug `news-image-20261118`, sponsor make.fun)
Hadiah: **$250 total, 50 entry teratas** ($50 juara 1, $30 juara 2,
$15 juara 3, $5 untuk 4–10, $3 untuk 11–50).
Deadline: **20 Nov 2026 07:00 WIB** (2026-11-20T00:00:00Z).
Status saat build: open, 0 submissions. Escrow $250 sudah terkunci
di Solana (program escrow make.fun) — submit butuh tanda tangan
wallet Solana yang ter-link ke akun Andi.

Repo yang disarankan (Public, dibuat Andi setelah bounty dibuka):
**Bradestudio-news-image-20261118**.
History git lokal di folder ini sudah siap di-push ke repo itu
(commit pertama dibuat 18 Nov 2026 ~00:14 UTC, setelah bounty dibuka
00:00 UTC).

## Berita yang dicakup gambar (5 cerita)

Cakupan berita: **sampai ~00:10 UTC / 07:10 WIB, Rabu 18 Nov 2026**
(awal hari). Peristiwa-peristiwa ini terjadi atau pertama kali
dilaporkan pada 18 Nov di zona waktu Asia (malam 17 Nov UTC) —
sesuai aturan bounty: "events that happened, or were first reported,
on 18 November 2026 in any time zone".

1. **Trump mendarat di Manila** — Quad talks, lalu kunjungan ke China.
   (AP; The Washington Post; headline 18 Nov di berbagai media.)
2. **Ukraina menghantam Jembatan Crimea hari kedua berturut-turut** —
   Rusia membalas menghantam jembatan-jembatan di Kyiv; Zelensky
   memaparkan roadmap perdamaian 5 poin. (DW; The Independent;
   South China Morning Post.)
3. **AS–Iran saling serang di Selat Hormuz** — jet AS menghantam
   situs peluncuran rudal IRGC di Pulau Qeshm setelah drone Iran
   menargetkan radar AS di Bahrain (dicegat, tanpa korban/kerusakan).
   (Al Jazeera live; CBS via AP; US CENTCOM.)
4. **Siklon Akvan** menguat di Teluk Benggala, diperkirakan jadi badai
   parah pada 19 Nov. (IMD via media India.)
5. **Kanada–China memperpanjang kerja sama dagang** — Xi bertemu PM
   Carney menjelang KTT APEC. (Jagran Josh; Education Times.)

Yang sengaja TIDAK dipakai: kecelakaan pesawat An-12 Rusia di Siberia
dan pensiunnya Dhoni dari IPL — keduanya terjadi/dilaporkan 17 Nov,
bukan 18 Nov.

## Cara pembuatan

- `main.py` (Python 3.13, **stdlib only**: struct + zlib + math + os)
  menggambar koran satu halaman 1024×1024 secara programatik:
  masthead "THE WORLD TODAY / WEDNESDAY 18 NOVEMBER 2026", 1 lead
  story (Manila) + 4 panel bergambar, masing-masing dengan headline
  dan sub-line singkat, plus footer "THE DAY IN 5 STORIES".
- Teks memakai font bitmap 5×7 yang ditulis di dalam `main.py`
  (tanpa file font, tanpa Pillow — sandbox grader hanya sediakan
  stdlib, jadi Pillow TIDAK boleh dipakai).
- Tidak ada network saat program jalan; semua konstanta fixed —
  output deterministik.
- Starter kit resmi diunduh dan dipakai sebagai acuan
  (`news-image-20261118-kit/`, `RULES.txt` dibaca). Entry ini TIDAK
  menyalin file starter (gambar + kode ditulis sendiri dari nol);
  hanya `LICENSE` (MIT) yang diambil dari starter.

## Hasil cek

Validasi lokal (dijalankan 2x, 18 Nov 2026 ~00:14 UTC):
- Run 1 dan run 2 **byte-identik**:
  sha256 `a1dc7b4d5c2d4b47a657ea9a6dbbc71f39b59e44557f61b0d679adca761ddc1c`
- Ukuran: **47.293 byte** (batas 1.048.576) — lolos
- Dimensi: **1024×1024** (batas 1024×1024) — lolos
- Format: PNG valid (magic bytes + IHDR 1024×1024 RGB)
- Waktu jalan: ~0,2 detik (batas 60 detik)
- Gambar dicek visual: semua headline terbaca, tidak ada teks
  terpotong/tertutup. Dua revisi visual dilakukan sebelum final:
  ledakan di panel Crimea dibuat bergerigi (sebelumnya terlalu
  bulat seperti target) dan panel dagang dirapikan (bendera
  sebelumnya bertumpuk; globe sempat menutupi headline).

Cek kit resmi
(`node cli/makefun.mjs check --kit . --repo <entry>`):
- **4 passed**: competition_open, snapshot (3 file, 25.082 byte),
  license_osi (MIT), entrypoint (main.py → python3.13, diterima)
- **1 failed**: `transcripts_present` — tidak ada transkrip yang
  di-upload. Ini wajar di tahap build: transkrip dibundel dari sesi
  agent yang terekam saat submit (oleh main agent, pakai
  `makefun bundle`). Jangan memalsukan transkrip.
- **5 "at submission"** (dicek situs saat submit, semuanya masih
  menunggu langkah Andi): repo_public, repo_owner, repo_created_after_open,
  commit_in_repo, duplicate_snapshot.

## Rencana refresh SEBELUM submit final — PENTING

Gambar ini mencerminkan berita **sampai pagi 18 Nov saja**.
Hari masih berjalan; sebelum deadline, lakukan ini:

1. **Siang/sore 18 Nov WIB**: cek lagi berita hari itu
   (hasil KTT Manila/Quad, perkembangan Hormuz, Akvan, dan
   cerita besar lain yang muncul siang hari UTC).
2. Bila ada cerita yang lebih besar dari salah satu dari 5 ini,
   ganti panelnya: edit headline/sub-line (dan bila perlu gambar
   panelnya) di `main.py`, jalankan ulang 2x, bandingkan hash,
   commit baru.
3. **Submit final paling lambat 19 Nov malam WIB** (deadline
   20 Nov 07:00 WIB) — jangan submit versi pagi ini sebagai final
   bila refresh menghasilkan perubahan. Submit terakhir sebelum
   deadline adalah entry final.
4. Bila tidak ada berita besar baru, versi ini sudah bisa
   disubmit apa adanya.

## Yang masih kurang sebelum submit

- [ ] Andi membuat repo GitHub Public **Bradestudio-news-image-20261118**
      (dibuat setelah 18 Nov 00:00 UTC) dan push history dari folder ini.
- [ ] `.makefun/owner.json` — hanya bila owner repo GitHub bukan akun
      GitHub Andi; bila repo milik Bradestudio, tidak perlu.
- [ ] Transkrip sesi build dibundel (`makefun bundle`) oleh main agent
      dan di-upload bersama submit.
- [ ] Submit via makefun CLI + tanda tangan entry dengan wallet Solana
      Andi (escrow aktif — hadiah diklaim dari escrow bila menang).
- [ ] Refresh berita (lihat rencana di atas) sebelum submit final.

Tidak ada repo yang dibuat dan tidak ada submit yang dilakukan
dalam sesi build ini.
