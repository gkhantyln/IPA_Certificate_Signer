import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import requests

class IPA_Signer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IPA Certificate Signer [ api.starfiles.co ]")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.create_widgets()

    def create_widgets(self):
        self.file_frame = ttk.Frame(self, padding=(20, 10))
        self.file_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        tk.Label(self.file_frame, text="IPA Dosyası:").grid(row=0, column=0, sticky='w')
        self.entry_ipa = ttk.Entry(self.file_frame, width=50)
        self.entry_ipa.grid(row=0, column=1, padx=5, pady=5)
        self.button_browse_ipa = ttk.Button(self.file_frame, text="Dosya Seç", command=self.browse_ipa)
        self.button_browse_ipa.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.file_frame, text="P12 Dosyası:").grid(row=1, column=0, sticky='w')
        self.entry_p12 = ttk.Entry(self.file_frame, width=50)
        self.entry_p12.grid(row=1, column=1, padx=5, pady=5)
        self.button_browse_p12 = ttk.Button(self.file_frame, text="Dosya Seç", command=self.browse_p12)
        self.button_browse_p12.grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.file_frame, text="Mobileprovision Dosyası:").grid(row=2, column=0, sticky='w')
        self.entry_mobileprovision = ttk.Entry(self.file_frame, width=50)
        self.entry_mobileprovision.grid(row=2, column=1, padx=5, pady=5)
        self.button_browse_mobileprovision = ttk.Button(self.file_frame, text="Dosya Seç", command=self.browse_mobileprovision)
        self.button_browse_mobileprovision.grid(row=2, column=2, padx=5, pady=5)

        tk.Label(self.file_frame, text="Şifre:").grid(row=3, column=0, sticky='w')
        self.entry_password = ttk.Entry(self.file_frame, show='*', width=50)
        self.entry_password.grid(row=3, column=1, padx=5, pady=5)

        self.auto_fill_var = tk.IntVar()
        self.auto_fill_checkbox = ttk.Checkbutton(self.file_frame, text="Dosyaları Otomatik Seç", variable=self.auto_fill_var, command=self.auto_fill)
        self.auto_fill_checkbox.grid(row=4, column=0, columnspan=3, pady=5)

        self.button_sign = ttk.Button(self, text="Sign", command=self.sign)
        self.button_sign.grid(row=1, column=0, pady=10)

        self.result_label = ttk.Label(self, text="")
        self.result_label.grid(row=2, column=0, pady=10)

        self.alerts = []

    def browse_ipa(self):
        self.auto_fill_var.set(0)  # Otomatik seçimi devre dışı bırak
        filename = filedialog.askopenfilename(filetypes=[("IPA Files", "*.ipa")])
        self.entry_ipa.delete(0, tk.END)
        self.entry_ipa.insert(0, filename)

    def browse_p12(self):
        self.auto_fill_var.set(0)  # Otomatik seçimi devre dışı bırak
        filename = filedialog.askopenfilename(filetypes=[("P12 Files", "*.p12")])
        self.entry_p12.delete(0, tk.END)
        self.entry_p12.insert(0, filename)

    def browse_mobileprovision(self):
        self.auto_fill_var.set(0)  # Otomatik seçimi devre dışı bırak
        filename = filedialog.askopenfilename(filetypes=[("Mobileprovision Files", "*.mobileprovision")])
        self.entry_mobileprovision.delete(0, tk.END)
        self.entry_mobileprovision.insert(0, filename)

    def auto_fill(self):
        if self.auto_fill_var.get() == 1:
            ipa_files = [file for file in os.listdir("files") if file.endswith(".ipa")]
            p12_files = [file for file in os.listdir("files") if file.endswith(".p12")]
            mobileprovision_files = [file for file in os.listdir("files") if file.endswith(".mobileprovision")]

            if ipa_files:
                self.entry_ipa.delete(0, tk.END)
                self.entry_ipa.insert(0, os.path.join("files", ipa_files[0]))
            if p12_files:
                self.entry_p12.delete(0, tk.END)
                self.entry_p12.insert(0, os.path.join("files", p12_files[0]))
            if mobileprovision_files:
                self.entry_mobileprovision.delete(0, tk.END)
                self.entry_mobileprovision.insert(0, os.path.join("files", mobileprovision_files[0]))

            if os.path.exists("files/password.txt"):
                with open("files/password.txt", "r") as f:
                    password = f.read()
                    self.entry_password.delete(0, tk.END)
                    self.entry_password.insert(0, password)
        else:
            self.entry_ipa.delete(0, tk.END)
            self.entry_p12.delete(0, tk.END)
            self.entry_mobileprovision.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)

    def upload_file(self, file_path):
        if not file_path:
            return None
        try:
            url = 'https://api.starfiles.co/upload/upload_file'
            files = {'upload': open(file_path, 'rb')}
            response = requests.post(url, files=files)
            response.raise_for_status()  # HTTP hata durumunda istisna fırlatır
            data = response.json()
            return data['file']
        except requests.exceptions.RequestException:
            if "API sağlayıcınıza ulaşılamıyor. Lütfen daha sonra tekrar deneyiniz." not in self.alerts:
                self.alerts.append("API sağlayıcınıza ulaşılamıyor. Lütfen daha sonra tekrar deneyiniz.")
            return None
        except (KeyError, ValueError):
            self.alerts.append("Dosya yükleme hatası")
            return None

    def sign(self):
        self.alerts = []  # Uyarıları temizle
        ipa_path = self.entry_ipa.get()
        p12_path = self.entry_p12.get()
        mobileprovision_path = self.entry_mobileprovision.get()
        password = self.entry_password.get()

        if self.auto_fill_var.get() == 1:
            self.auto_fill()

        ipa_output = self.upload_file(ipa_path)
        p12_output = self.upload_file(p12_path)
        mobileprovision_output = self.upload_file(mobileprovision_path)

        if ipa_output and p12_output and mobileprovision_output:
            sign_url = f'https://sign.starfiles.co?ipa={ipa_output}&p12={p12_output}&mobileprovision={mobileprovision_output}&password={password}'
            os.system(f"start {sign_url}")
            self.result_label.config(text="İşlem başarılı, lütfen sonucu kontrol edin.", foreground="green")
        else:
            messagebox.showwarning("Uyarı", "\n".join(self.alerts))
            self.result_label.config(text="Api bağlantısı ve dosya yükleme hatası", foreground="red")

if __name__ == "__main__":
    app = IPA_Signer()
    app.mainloop()
