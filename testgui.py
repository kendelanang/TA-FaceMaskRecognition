from PIL import ImageTk, Image
import tkinter as tk

from detect_mask_video import absensiWajah

def daftar():
	entry1 = tk.Entry (root, font="Montserrat")
	canvas.create_window(457, 170, height=25, width=411, window=entry1)
	label1 = tk.Label(root, text="Nama ", font="Montserrat", fg="white", bg="black")
	canvas.create_window(90,170, window=label1)
	Daftar_text = tk.StringVar()
	Daftar_btn = tk.Button(root, textvariable=Rekam_text, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15, command=daftar)
	Daftar_text.set("Submit")
	Daftar_btn.place(x = 252, y = 210)

root = tk.Tk()
root.title("Deteksi Penggunaan Masker GUI")
root.geometry("700x400")
# mengatur canvas (window tkinter)
canvas = tk.Canvas(root, width=700, height=400)
canvas.grid(columnspan=3, rowspan=8)
canvas.configure(bg="black")
# judul
judul = tk.Label(root, text="Deteksi Penggunaan Masker", font=("Montserrat",34),bg="#242526", fg="white")
canvas.create_window(350, 80, window=judul)
#credit
made = tk.Label(root, text="Dikembangkan Oleh Rafael Alferdyas Putra", font=("Montserrat",13), bg="black",fg="white")
canvas.create_window(360, 20, window=made)

global intructions

# tombol untuk Daftarkan data wajah
intructions = tk.Label(root, text="Selamat Datang", font=("Montserrat",15),fg="white",bg="black")
canvas.create_window(370, 300, window=intructions)
Rekam_text = tk.StringVar()
Rekam_btn = tk.Button(root, textvariable=Rekam_text, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15, command=daftar)
Rekam_text.set("Daftarkan Wajah")
Rekam_btn.grid(column=0, row=7)

# tombol untuk training wajah
Rekam_text1 = tk.StringVar()
Rekam_btn1 = tk.Button(root, textvariable=Rekam_text1, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15,)
Rekam_text1.set("Training Wajah")
Rekam_btn1.grid(column=1, row=7)

# tombol deteksi penggunaan masker
Rekam_text2 = tk.StringVar()
Rekam_btn2 = tk.Button(root, textvariable=Rekam_text2, font="Montserrat", bg="#20bebe", fg="white", height=1, width=20,)
Rekam_text2.set("Mulai Deteksi")
Rekam_btn2.grid(column=2, row=7)

root.mainloop()