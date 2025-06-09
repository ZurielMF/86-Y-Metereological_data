import limpiar_datos as ld
import datascraper as ds
import tkinter as tk
from tkinter import filedialog
from tkinter import *

#Este array se puede cambiar luego por algo menos hard-coded
estaciones_scrapeables = [ 
    '25001', '25003', '25009', '25014', '25015', '25019', '25021', '25022', '25023', '25025',
    '25050', '25062', '25064', '25074', '25077', '25078', '25080', '25081', '25087', '25093',
    '25030', '25033', '25036', '25037', '25038', '25041', '25042', '25044', '25045', '25046',
    '25100', '25102', '25103', '25105', '25106', '25107', '25110', '25115', '25119', '25150',
    '25155', '25158', '25161', '25171', '25172', '25173', '25176', '25178', '25183', '25186'
    ]

if __name__ == "__main__":
    # Crear la ventana
    ventana = tk.Tk()
    ventana.title("Limpiar Datos")
    ventana.geometry("400x400")
    
    espacio = tk.Label(ventana, text="")
    espacio.pack()
    
    def scrapear_datos():
        carpeta = tk.filedialog.askdirectory()
        if not carpeta:
            return
        else:
            print(carpeta)
            etiqueta_scraper = tk.Label(ventana, text="Scrapeando datos")
            etiqueta_scraper.pack()
            ds.bulk_download(estaciones_scrapeables, carpeta)
            etiqueta_scraper.destroy()
            etiqueta_final = tk.Label(ventana, text="Datos scrapeados")
            etiqueta.after(1000, lambda: etiqueta_final.pack())
            etiqueta_final.after( 2000, lambda: etiqueta_final.destroy())
            print("Datos scrapeados")
    
    boton_scrapear = tk.Button(ventana, text="Scrapear datos", command=scrapear_datos)
    boton_scrapear.pack()
    
    espacio = tk.Label(ventana, text="")
    espacio.pack()
    
    label_umbral = tk.Label(ventana, text="Introduce el % máximo de datos faltantes aceptable")
    label_umbral.pack()
    porcentaje = tk.StringVar()
    porcentaje.set("100")
    entrada_umbral = tk.Entry(ventana, textvariable=porcentaje, width=4)
    entrada_umbral.pack()
    
    espacio = tk.Label(ventana, text="")
    espacio.pack()
    
    
    espacio = tk.Label(ventana, text="")
    espacio.pack()
    
    # Crear la etiqueta
    etiqueta = tk.Label(ventana, text="Selecciona la carpeta con los datos a limpiar")
    etiqueta.pack()    
    
    # Crear la entrada mediante un botón que deje seleccionar una carpeta
    def seleccionar_carpeta():
        carpeta = tk.filedialog.askdirectory()
        if not carpeta:
            return
        else:
            print(carpeta)
            etiqueta_txt_csv = tk.Label(ventana, text="Limpiando archivos .txt a .csv")
            etiqueta_txt_csv.pack()
            # Validar que el porcentaje sea un número
            try:
                porcentaje = int(entrada_umbral.get())
            except ValueError:
                etiqueta_error = tk.Label(ventana, text="Porcentaje no válido")
                etiqueta_error.pack()
                etiqueta_error.after( 1000, lambda: etiqueta_error.destroy())
                return
            #ld.procesar_lote_txt_a_csv(carpeta, porcentaje)
            ld.procesar_lote_txt_a_csv(carpeta, porcentaje)
            etiqueta_txt_csv.destroy()
            etiqueta_concentrados = tk.Label(ventana, text="Generando concentrados mensuales")
            etiqueta_concentrados.pack()
            ld.generar_concentrados_diarios(carpeta)
            ld.generar_concentrados_mensuales(carpeta)
            ld.generar_concentrados_anuales(carpeta)
            ld.concatenar_concentrados(carpeta)
            etiqueta_concentrados.destroy()
            etiqueta_concatenados = tk.Label(ventana, text="Concatenando concentrados")
            etiqueta_concatenados.pack()
            etiqueta_concatenados.after( 1000, lambda: etiqueta_concatenados.destroy())
            etiqueta_final = tk.Label(ventana, text="Datos limpiados")
            etiqueta.after(1000, lambda: etiqueta_final.pack())
            etiqueta_final.after( 2000, lambda: etiqueta_final.destroy())
            print("Datos limpiados")
    
    boton = tk.Button(ventana, text="Seleccionar carpeta", command=seleccionar_carpeta)
    boton.pack()

    # Mostrar la ventana
    ventana.mainloop()