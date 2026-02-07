import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Awal
st.set_page_config(page_title="VetCare Pro", layout="wide", page_icon="🐾")

# Inisialisasi Database di Session State (agar data tidak hilang saat pindah menu)
if 'data_obat' not in st.session_state:
    st.session_state.data_obat = pd.DataFrame(columns=["Nama Obat", "Stok", "Harga"])

if 'data_pasien' not in st.session_state:
    st.session_state.data_pasien = pd.DataFrame(columns=["ID", "Pemilik", "Nama Hewan", "Spesies"])

if 'transaksi' not in st.session_state:
    st.session_state.transaksi = pd.DataFrame(columns=["Tanggal", "Pasien", "Item", "Total"])

# --- UI SIDEBAR ---
st.sidebar.title("🐾 VetCare Pro")
menu = st.sidebar.selectbox("Pilih Menu:", ["Dashboard", "Data Pasien", "Manajemen Obat", "Kasir & Pembayaran"])

# --- LOGIKA DASHBOARD ---
if menu == "Dashboard":
    st.header("Ringkasan Klinik")
    col1, col2, col3 = st.columns(3)
    
    total_pendapatan = st.session_state.transaksi["Total"].sum()
    total_pasien = len(st.session_state.data_pasien)
    
    col1.metric("Total Pendapatan", f"Rp {total_pendapatan:,}")
    col2.metric("Jumlah Pasien", total_pasien)
    col3.metric("Jenis Obat", len(st.session_state.data_obat))

    st.subheader("Riwayat Transaksi Terakhir")
    st.table(st.session_state.transaksi.tail(5))

# --- LOGIKA DATA PASIEN ---
elif menu == "Data Pasien":
    st.header("Registrasi Pasien Baru")
    with st.form("form_pasien"):
        c1, c2 = st.columns(2)
        nama_p = c1.text_input("Nama Pemilik")
        nama_h = c2.text_input("Nama Hewan")
        spesies = st.selectbox("Spesies", ["Kucing", "Anjing", "Burung", "Reptil", "Lainnya"])
        submit_p = st.form_submit_button("Simpan Data Pasien")
        
        if submit_p:
            new_id = f"VET-{len(st.session_state.data_pasien) + 101}"
            new_pasien = pd.DataFrame([[new_id, nama_p, nama_h, spesies]], 
                                     columns=["ID", "Pemilik", "Nama Hewan", "Spesies"])
            st.session_state.data_pasien = pd.concat([st.session_state.data_pasien, new_pasien], ignore_index=True)
            st.success(f"Pasien {nama_h} berhasil didaftarkan!")

    st.subheader("Daftar Pasien Terdaftar")
    st.dataframe(st.session_state.data_pasien, use_container_width=True)

# --- LOGIKA MANAJEMEN OBAT ---
elif menu == "Manajemen Obat":
    st.header("Inventori Obat & Alkes")
    with st.expander("➕ Tambah Stok/Obat Baru"):
        with st.form("form_obat"):
            n_obat = st.text_input("Nama Obat/Layanan")
            s_obat = st.number_input("Stok", min_value=0)
            h_obat = st.number_input("Harga Jual (Rp)", min_value=0, step=1000)
            submit_o = st.form_submit_button("Update Stok")
            
            if submit_o:
                new_obat = pd.DataFrame([[n_obat, s_obat, h_obat]], 
                                       columns=["Nama Obat", "Stok", "Harga"])
                st.session_state.data_obat = pd.concat([st.session_state.data_obat, new_obat], ignore_index=True)
                st.success("Data Obat diperbarui!")

    st.dataframe(st.session_state.data_obat, use_container_width=True)

# --- LOGIKA KASIR ---
elif menu == "Kasir & Pembayaran":
    st.header("Pembayaran Kasir")
    
    if st.session_state.data_pasien.empty or st.session_state.data_obat.empty:
        st.warning("Pastikan data pasien dan data obat sudah terisi terlebih dahulu.")
    else:
        with st.form("form_bayar"):
            # Pilih Pasien
            opsi_pasien = st.session_state.data_pasien["Nama Hewan"] + " (Pemilik: " + st.session_state.data_pasien["Pemilik"] + ")"
            pilih_pasien = st.selectbox("Pilih Pasien", opsi_pasien)
            
            # Pilih Obat
            pilih_obat = st.selectbox("Pilih Obat/Layanan", st.session_state.data_obat["Nama Obat"])
            jumlah = st.number_input("Jumlah", min_value=1)
            
            # Hitung Harga
            harga_satuan = st.session_state.data_obat.loc[st.session_state.data_obat["Nama Obat"] == pilih_obat, "Harga"].values[0]
            total_harga = harga_satuan * jumlah
            
            st.subheader(f"Total Tagihan: Rp {total_harga:,}")
            
            bayar = st.form_submit_button("Proses Pembayaran & Cetak")
            
            if bayar:
                new_trx = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), pilih_pasien, pilih_obat, total_harga]], 
                                      columns=["Tanggal", "Pasien", "Item", "Total"])
                st.session_state.transaksi = pd.concat([st.session_state.transaksi, new_trx], ignore_index=True)
                st.balloons()
                st.success("Transaksi Berhasil Dicatat!")
