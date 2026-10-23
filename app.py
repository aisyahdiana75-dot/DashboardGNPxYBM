"""
Dashboard Persiapan GNP x YBM
Jalankan: streamlit run app.py
Semua pengunjung membaca file status yang sama di server,
dan tampilan menyegarkan diri tiap 10 detik.
"""

import json
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

DATA_FILE = "status_gnp_ybm.json"
WIB = timezone(timedelta(hours=7))

# (kode PIC, nama PIC, [(tugas, sudah selesai?)])
TASKS = [
    ("rama", "Bang Rama", [
        ("Pengajuan desain rompi", True),
        ("Pengajuan list rompi", False),
        ("Pembayaran DP rompi", True),
    ]),
    ("zidni", "Zidni", [
        ("Pesan goodie bag desain baru (560 pcs)", False),
        ("Persiapan ATK Batch 37", False),
        ("Cetak banner GNP", False),
        ("Cetak mock up GNP", False),
    ]),
    ("rani", "Kak Rani", [
        ("Pengajuan DP ke ASP", False),
        ("Invoice 4 batch dari ASP ke YBM Brilian", False),
        ("Memastikan semua peserta ada di grup Batch 37", False),
    ]),
    ("dian", "Dian", [
        ("Draft impact report", False),
        ("Konversi listing ukuran rompi peserta GNP", False),
        ("Minta arahan finance untuk laporan keuangan ke YBM Brilian", False),
        ("Template berita acara", False),
    ]),
    ("irvan", "Irvan", [
        ("Template story + logo YBM", False),
        ("Brief testimoni", False),
        ("Flyer GNP Batch 37 + logo YBM untuk dibagikan ke grup Batch 37", False),
        ("Backdrop", False),
    ]),
]


def load_status():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_status(status):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def on_toggle(task_id):
    """Dipanggil saat checkbox diubah: baca file terbaru, ubah satu tugas, simpan."""
    status = load_status()
    status[task_id] = {
        "done": st.session_state[f"cb_{task_id}"],
        "by": st.session_state.get("nama", "") or "Anonim",
        "at": datetime.now(WIB).strftime("%d %b %Y %H:%M"),
    }
    save_status(status)


st.set_page_config(page_title="Persiapan GNP x YBM", page_icon="📖", layout="wide")
st.title("📖 Persiapan GNP x YBM")
st.caption("Ceklis bersama tim. Tampilan menyegarkan diri tiap 10 detik.")

with st.sidebar:
    st.text_input("Nama Anda (dicatat saat mencentang)", key="nama")
    st.download_button(
        "Unduh cadangan status (JSON)",
        json.dumps(load_status(), ensure_ascii=False, indent=2),
        "status_gnp_ybm.json",
        "application/json",
    )


@st.fragment(run_every=10)
def board():
    status = load_status()
    rows = []

    for pic_id, pic_name, tugas in TASKS:
        for i, (nama_tugas, default) in enumerate(tugas):
            tid = f"{pic_id}_{i}"
            s = status.get(tid)
            done = s["done"] if s else default
            rows.append({
                "id": tid, "PIC": pic_name, "Tugas": nama_tugas, "done": done,
                "Diperbarui": f'{s["at"]} oleh {s["by"]}' if s else "",
            })

    df = pd.DataFrame(rows)
    total, selesai = len(df), int(df["done"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Progres total", f"{selesai / total:.0%}")
    c2.metric("Tugas selesai", f"{selesai}/{total}")
    c3.metric("Tugas tersisa", total - selesai)
    st.progress(selesai / total)

    cols = st.columns(2)
    for n, (pic_id, pic_name, tugas) in enumerate(TASKS):
        sub = df[df["PIC"] == pic_name]
        with cols[n % 2].container(border=True):
            st.subheader(f"{pic_name}  ({int(sub['done'].sum())}/{len(sub)})")
            st.progress(float(sub["done"].mean()))
            for _, r in sub.iterrows():
                # set nilai dari file sebelum widget dibuat, agar sinkron dengan perubahan orang lain
                st.session_state[f"cb_{r['id']}"] = bool(r["done"])
                st.checkbox(r["Tugas"], key=f"cb_{r['id']}", on_change=on_toggle, args=(r["id"],))
                if r["Diperbarui"] and r["done"]:
                    st.caption(f"Diperbarui {r['Diperbarui']}")

    st.divider()
    out = df.assign(Status=df["done"].map({True: "Selesai", False: "Belum"}))[["PIC", "Tugas", "Status", "Diperbarui"]]
    st.dataframe(out, use_container_width=True, hide_index=True)
    st.download_button("Unduh CSV", out.to_csv(index=False).encode("utf-8"), "persiapan_gnp_ybm.csv", "text/csv")


board()
