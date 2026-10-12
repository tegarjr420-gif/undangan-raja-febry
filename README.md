# Undangan Raja & Febri

Undangan pernikahan digital satu halaman. Dideploy otomatis oleh Cloudflare (wrangler.jsonc) setiap ada perubahan di branch utama.

- `public/index.html` — seluruh halaman (desain, animasi, data acara, rekening, WA)
- `public/couple.jpg`, `public/raja.jpg`, `public/febry.jpg` — foto
- Ucapan & RSVP disimpan di Supabase (project `undangan-raja-febry`, tabel `ucapan`)
- Domain: https://undanganrajafebry.site (custom domain di wrangler.jsonc)

Link tamu: tambahkan nama di akhir alamat, misalnya `/#Budi_Santoso`.
Tambahkan `-r` (tamu Raja) atau `-f` (tamu Febri) untuk menyorot tombol WA yang sesuai: `/#Budi_Santoso-r`.
