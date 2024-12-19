import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ImageProcessor import ImageProcessor
from BinarizationMethods import BinarizationMethods

class BinarizationApp:

    def __init__(self, root):
        self.root = root
        self.root.title("binarization")

        self.root.geometry('1000x640')
        self.root.resizable(width=False,height=False)
        self.root.config(bg="cornsilk3")
        self.image_path = None
        self.image = None
        self.image_selected = False

        self.label_frame = tk.LabelFrame(root,bg="cornsilk3", relief="ridge")
        self.label_frame.place(x=10, y=10, height=615,)

        self.label_frame_2 = tk.LabelFrame(root,bg="cornsilk3",relief="ridge")
        self.label_frame_3 = tk.LabelFrame(root,bg="cornsilk3",relief="ridge")
        
        self.label_frame_4 = tk.LabelFrame(root,bg="cornsilk3",relief="ridge")
        self.label_frame_4.place(x=280, y=10, height=615,width=700)


        self.r_size = tk.Label(self.label_frame_3,text="r_size:",bg="cornsilk3",font=("Arial", 12))
        self.R_size = tk.Label(self.label_frame_3,text="R_size:",bg="cornsilk3",font=("Arial", 12))
        self.eps = tk.Label(self.label_frame_3,text="eps:",bg="cornsilk3",font=("Arial", 12)
                            )
        self.r_size.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.R_size.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.eps.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.r_size = tk.Entry(self.label_frame_3, font=("Arial", 12), width=15, background='cornsilk3')
        self.r_size.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.R_size = tk.Entry(self.label_frame_3, font=("Arial", 12), width=15,background='cornsilk3')
        self.R_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.eps = tk.Entry(self.label_frame_3, font=("Arial", 12), width=15,background='cornsilk3')
        self.eps.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.thresh_slider = tk.Scale(self.label_frame_2, from_=0, to_=255, orient="horizontal", label="пороговое значение", bg="cornsilk2", font=("Arial", 14), state="disabled",length=220)
        self.thresh_slider.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")
        self.thresh_slider.grid_forget()

        self.select_button = tk.Button(
            self.label_frame,
            text="Выбрать изображение",
            command=self.load_image,
            bg="cornsilk2",      
            fg="black",              
            font=("Arial", 14),  
            relief="raised",         
            activebackground="cornsilk2", 
            bd=4,
            width=20
        )
        self.select_button.grid(row=0, column=0, padx=10, pady=(10,20), sticky="nsew")
        self.select_button.bind("<Enter>", self.on_enter_select_button)
        self.select_button.bind("<Leave>", self.on_leave_select_button)

        self.method_var = tk.StringVar(self.label_frame)
        self.method_var.set("Выбрать метод")
        self.methods = ["Глобальный", "Бернсена", "Ниблэка", "Саувола", "Эйквеля", "Оцу"]
        self.method_menu = tk.OptionMenu(self.label_frame, self.method_var, *self.methods, command=self.on_method_change)
        self.method_menu.config(bg="cornsilk2", font=("Arial", 14), activebackground="cornsilk2", relief="raised", state=tk.DISABLED)
        self.method_menu.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.process_button = tk.Button(
            self.label_frame, 
            text="Обработать", 
            state=tk.DISABLED,
            command=self.process_image,
            bg="cornsilk2",      
            fg="black",              
            font=("Arial", 14),  
            relief="raised",         
            activebackground="cornsilk2", 
            bd=4
        )
        self.process_button.grid(row=3, column=0, padx=10, pady=(280, 10), sticky="nsew")

        self.save_button = tk.Button(
            self.label_frame, 
            text="Сохранить", 
            command=self.save_image, 
            state=tk.DISABLED,
            bg="cornsilk2",      
            fg="black",              
            font=("Arial", 14),  
            relief="raised",         
            activebackground="cornsilk2", 
            bd=4,
        )
        self.save_button.grid(row=4, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.exit_button = tk.Button(
            self.label_frame, 
            text="Выход", 
            command=self.root.quit, 
            bg="cornsilk2",      
            fg="black",              
            font=("Arial", 14),  
            relief="raised",         
            activebackground="cornsilk2", 
            bd=4,
        )
        self.exit_button.grid(row=5, column=0, padx=10, pady=(10, 10), sticky="nsew")

        
    def on_enter_select_button(self, event):
        if self.image_selected: self.select_button.config(text="Выбрать другое")
        
    def on_leave_select_button(self, event):
        if self.image_selected ==False: self.select_button.config(text="Выбрать изображение")
        else: self.select_button.config(text=self.image_path.split("/")[-1])

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.webp")])
        if file_path:
            self.image_path = file_path
            self.image = ImageProcessor.read_image(self.image_path, gray_scale=False)
            if self.image is not None:
                self.select_button.config(text=self.image_path.split("/")[-1])
                self.image_selected = True
                self.method_menu.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Не удалось загрузить изображение.")
                self.image_selected = False

    def on_method_change(self, selected_method):
        self.label_frame_2.place_forget()
        self.label_frame_3.place_forget()
        self.process_button.config(state=tk.NORMAL)

        if selected_method == "Глобальный":
            self.label_frame_2.place(x=14, y=170, height=115,width=250)
            self.thresh_slider.grid(row=0, column=0, padx=10, pady=20, sticky="nsew") 
            self.thresh_slider.configure(state="normal")

        elif selected_method == "Эйквеля":
            self.label_frame_3.place(x=14, y=170, height=115, width=250)
            self.process_button.config(state=tk.DISABLED)
            self.r_size.bind("<KeyRelease>", self.check_eikwel_params)
            self.R_size.bind("<KeyRelease>", self.check_eikwel_params)
            self.eps.bind("<KeyRelease>", self.check_eikwel_params)
        
    def check_eikwel_params(self, event=None):
        r_size_value = self.r_size.get()
        R_size_value = self.R_size.get()
        eps_value = self.eps.get()

        if r_size_value and R_size_value and eps_value:
            self.process_button.config(state=tk.NORMAL)  
        else:
            self.process_button.config(state=tk.DISABLED)

    def process_image(self):
        method = self.method_var.get()
        if method == "Глобальный":
            thresh = self.thresh_slider.get()
            self.result = BinarizationMethods.threshold_global(self.image.copy(), thresh=thresh)
        elif method == "Бернсена":
            self.result = BinarizationMethods.threshold_bernsen(self.image.copy(), window_size=15, contrast_threshold=15)
        elif method == "Ниблэка":
            self.result = BinarizationMethods.threshold_niblack(self.image.copy(), window_size=15, k=0.2)
        elif method == "Саувола":
            self.result = BinarizationMethods.threshold_sauvola(self.image.copy(), window_size=25)
        elif method == "Эйквеля":
            self.process_button.config(state=tk.DISABLED)
           
            r_size = int(self.r_size.get())
            R_size = int(self.R_size.get())
            eps = int(self.eps.get())
            self.result = BinarizationMethods.threshold_eikwel(self.image.copy(), r_size=r_size, R_size=R_size, eps=eps, count=0)
            
        elif method == "Оцу":
            self.result = BinarizationMethods.threshold_global(self.image.copy(), thresh='otsu')
    
        self.save_button.config(state=tk.NORMAL)
        self.show_image(self.result)
        
    def save_image(self):
        if self.result is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
            if file_path:
                ImageProcessor.save_image(self.result, file_path)

    def show_image(self, image=None):
        image_numpy = image
        image_pil = Image.fromarray(image_numpy)
        img_width, img_height = image_pil.size
        max_width = 670
        max_height = 585

        if img_width > max_width:
            aspect_ratio = img_height / img_width
            img_width = max_width
            img_height = int(max_width * aspect_ratio)
        if img_height > max_height:
            aspect_ratio = img_width / img_height
            img_height = max_height
            img_width = int(max_height * aspect_ratio)

        image_pil = image_pil.resize((img_width, img_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=image_pil)
        for widget in self.label_frame_4.winfo_children():
            widget.destroy()
        
        canvas = tk.Canvas(self.label_frame_4, width=img_width, height=img_height)
        canvas.place(relx=0.5, rely=0.5, anchor="center")  
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = BinarizationApp(root)
    root.mainloop()