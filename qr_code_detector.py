import cv2
from pyzbar.pyzbar import decode
import winsound
import tkinter as tk
from PIL import Image, ImageTk
import csv

cap = cv2.VideoCapture(0)
qr_codes = []

root = tk.Tk()
root.title("QR Code Detector")

canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

label = tk.Label(root, text="QR Codes:")
label.pack()

listbox = tk.Listbox(root, width=50)
listbox.pack()

def update_listbox():
    listbox.delete(0, tk.END)
    for code in qr_codes:
        listbox.insert(tk.END, code)

def update_frame():
    _, frame = cap.read()
    decodedObjects = decode(frame)
    for obj in decodedObjects:
        if obj.data.decode() not in qr_codes:
            qr_codes.append(obj.data.decode())
            print("Data:", obj.data.decode())
            winsound.Beep(1000, 200)
            update_listbox()
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    root.after(10, update_frame)

def save_to_csv():
    with open('qr_codes.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['QR Codes'])
        for code in qr_codes:
            writer.writerow([code])

button = tk.Button(root, text="Save to CSV", command=save_to_csv)
button.pack()

root.after(10, update_frame)
root.mainloop()

cap.release()
cv2.destroyAllWindows()