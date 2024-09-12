import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno
import os
from tkinter import messagebox
import numpy as np
import cv2
from PIL import Image, ImageTk

largeur = 500
hauteur = 480

largeurImage = 450
hauteurImage = 440

# Créer la fenêtre principale
window = tk.Tk()
window.title("Segmentation Image - CROISSANCE D'UNE REGION")
window.geometry("1380x660")
window.minsize(600, 350)

# Changer la couleur de fond
window.configure(bg='lightblue')

# Variables globales
imageOriginale = None
imageBinaireGris = None
seed_point = None


# Fonction pour ouvrir l'image
def open_image(label):
    global imageOriginale
    file_path = askopenfilename()
    if file_path:
        img = Image.open(file_path)
        img = img.resize((largeurImage, hauteurImage), Image.LANCZOS)
        imgpil = ImageTk.PhotoImage(img)
        imageOriginale = cv2.imread(file_path)  # Lire l'image en niveaux de gris
        imageOriginale = cv2.resize(imageOriginale, (largeurImage, hauteurImage))
        image_pil = Image.fromarray(imageOriginale)
        label.config(image=imgpil)
        label.image = imgpil


# Fonction pour quitter l'application
def quit_app():
    if askyesno('Message', 'Êtes-vous sûr de vouloir quitter le programme?'):
        window.destroy()


def viderCases():
    global image_label1, image_label2

    # Vider les images dans les labels
    image_label1.config(image="", text="")
    image_label2.config(image="", text="")

    # Réinitialiser les références d'image pour éviter les fuites de mémoire
    image_label1.image = None
    image_label2.image = None

    # Vider les textefield
    text_X.delete(0, tk.END)
    text_Y.delete(0, tk.END)


def SegmenterRegion(image, seed_point, threshold=10):
    # Convertir l'image en niveaux de gris si elle est en couleur
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rows, cols = image.shape[:2]
    output = np.zeros((rows, cols), np.uint8)
    to_explore = [seed_point]
    start_value = image[seed_point[0], seed_point[1]]  # Extraire la valeur du pixel de départ

    while to_explore:
        x, y = to_explore.pop(0)
        output[x, y] = 255

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if output[nx, ny] == 0 and abs(int(image[nx, ny]) - int(start_value)) < threshold:
                    to_explore.append((nx, ny))
                    output[nx, ny] = 127

    return output


def enregistrer_images():
    global image_label1, image_label2
    save_directory = tk.filedialog.askdirectory()
    if not save_directory:
        return

    if image_label1.image is None:
        messagebox.showerror("Erreur", "Aucun image n'est ajouté.")
    else:
        if image_label1.image:
            image_pil1 = ImageTk.getimage(image_label1.image)
            image_path1 = os.path.join(save_directory, "image1.png")
            image_pil1.save(image_path1)
            print(f"Image 1 enregistrée à {image_path1}")

        if image_label2.image:
            image_pil2 = ImageTk.getimage(image_label2.image)
            image_path2 = os.path.join(save_directory, "image2.png")
            image_pil2.save(image_path2)
            print(f"Image 2 enregistrée à {image_path2}")

        # Confirmation
        messagebox.showinfo("Enregistrement", "Les images ont été enregistrées avec succès.")
        viderCases()


def on_mouse_click(event):
    global seed_point
    seed_point = (event.y, event.x)
    print(f"Point de départ sélectionné : {seed_point}")
    text_X.delete(0, tk.END)
    text_X.insert(0, str(seed_point[1]))
    text_Y.delete(0, tk.END)
    text_Y.insert(0, str(seed_point[0]))


def on_mouse_move(event):
    image_label1.config(text=f"Coordonnées : ({event.x}, {event.y})")


def segment_image():
    global imageOriginale, seed_point
    if imageOriginale is not None:
        try:
            x = int(text_X.get())
            y = int(text_Y.get())
            seed_point = (y, x)
            print(f"Point de départ défini à partir du formulaire : {seed_point}")
        except ValueError:
            if seed_point is None:
                messagebox.showerror("Erreur",
                                     "Veuillez entrer des coordonnées valides ou sélectionner un point de départ avec la souris.")
                return

        # Vérifier si les coordonnées sont dans les limites de l'image
        if seed_point[0] >= imageOriginale.shape[0] or seed_point[1] >= imageOriginale.shape[1]:
            messagebox.showerror("Erreur", "Les coordonnées du point de départ sont en dehors des limites de l'image.")
            return

        segmented_image = SegmenterRegion(imageOriginale, seed_point)
        image_pil = Image.fromarray(segmented_image)
        image_pil = image_pil.resize((largeurImage, hauteurImage), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image_pil)
        image_label2.config(image=photo)
        image_label2.image = photo
    else:
        messagebox.showerror("Erreur", "Veuillez d'abord ajouter une image.")


# Boucle pour les frames
for ligne in range(1):
    for colonne in range(2):
        image_frame1 = tk.Frame(window, bg='white', bd=2, relief='sunken', width=largeur, height=hauteur)
        image_frame1.grid(row=2, column=0, padx=0, pady=6)
        image_frame1.grid_propagate(False)  # Empêcher le cadre de se redimensionner

        image_frame2 = tk.Frame(window, bg='white', bd=2, relief='sunken', width=largeur, height=hauteur)
        image_frame2.grid(row=2, column=1, padx=0, pady=6)
        image_frame2.grid_propagate(False)

# Créer des labels pour afficher les images dans les cadres de chaque frames
image_label1 = tk.Label(image_frame1, bg='white', bd=2, relief='solid', cursor="cross")
image_label1.pack(expand=True, fill='both')
image_label1.bind("<Button-1>", on_mouse_click)
image_label1.bind("<Motion>", on_mouse_move)

image_label2 = tk.Label(image_frame2, bg='white', bd=2, relief='solid')
image_label2.pack(expand=True, fill='both')

frame_titre = tk.Frame(window, bg='lightblue', relief='sunken', width=1000, height=50)
frame_titre.grid(row=0, column=0, padx=0, pady=5)

frame_commande = tk.Frame(window, bg='lightblue', relief='sunken', width=1000, height=50)
frame_commande.grid(row=0, column=1, padx=0, pady=5)

# Ajouter le grand titre
title_label = tk.Label(frame_titre, text="APPLICATION SEGMENTATION IMAGE - Croissance d'une region",
                       font=("Berlin sans FB", 18, "bold"), fg='blue', bg='lightblue')
title_label.grid(row=0, column=0, columnspan=3, pady=5, padx=10)

label_X = tk.Label(frame_commande, text="X:", font=("Berlin sans FB", 12), fg='blue', bg='lightblue')
label_X.grid(row=0, column=0, padx=5, pady=0)
text_X = tk.Entry(frame_commande, width=40)
text_X.grid(row=0, column=1, padx=5, pady=0)

label_Y = tk.Label(frame_commande, text="Y:", font=("Berlin sans FB", 12), fg='blue', bg='lightblue')
label_Y.grid(row=1, column=0, padx=5, pady=0)
text_Y = tk.Entry(frame_commande, width=40)
text_Y.grid(row=1, column=1, padx=5, pady=0)

# Créer des boutons
button1 = tk.Button(window, text="Ajouter image", font=("Berlin sans FB", 14), bg='#5187ec', fg="white",
                    command=lambda: open_image(image_label1), width=30, height=1)
button1.grid(row=4, column=0, padx=20, pady=3)

button2 = tk.Button(window, text="Segmenter l'image", font=("Berlin sans FB", 14), bg='#5187ec', fg="white",
                    command=segment_image, width=30, height=1)
button2.grid(row=4, column=1, padx=20, pady=3)

button4 = tk.Button(window, text="Enregistrer image", font=("Berlin sans FB", 14), bg='#5187ec', fg="white",
                    command=enregistrer_images, width=30, height=1)
button4.grid(row=5, column=0, padx=40, pady=3)

button4 = tk.Button(window, text="Vider les cases", font=("Berlin sans FB", 14), bg='#5187ec', fg="white",
                    command=viderCases, width=30, height=1)
button4.grid(row=5, column=1, padx=40, pady=3)

# Créer un menu
menu = tk.Menu(window, bg="lightblue", fg="black", font=("Berlin sans FB", 14))
window.config(menu=menu)

# Ajouter des éléments au menu
file_menu = tk.Menu(menu, tearoff=0, bg="lightblue", fg="black", font=("Berlin sans FB", 14))
menu.add_cascade(label="Fichier", menu=file_menu, font=("Berlin sans FB", 14))
file_menu.add_command(label="Ajouter image", command=lambda: open_image(image_label1))
file_menu.add_command(label="Segmenter image", command=segment_image)
file_menu.add_command(label="Enregistrer image", command=enregistrer_images)
file_menu.add_command(label="Vider les cases", command=viderCases)
file_menu.add_command(label="Quitter", command=quit_app)

# Lancer la boucle principale de l'interface graphique
window.mainloop()
