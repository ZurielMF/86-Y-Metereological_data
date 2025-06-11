# 86-Y-Metereological_data
This is a PYthon Script project, * ETL workflow 
A Python program that makes an ETL process trough data available at platforms: Servicio Metereologico Nacional (SMN) and Comision Nacional del Agua (CONAGUA)


## Overview
To reproduce ETL process, the script steps are described bellow:
### On datascraper.py
1) Scrap meteorological data from [Mexico's Meteorological Service site (Servicio Meteorológico Nacional)](https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica).
2) Download data locally
### On data_cleaning.py
1) Scan a selected folder for data files
2) Clean raw TXT files
3) Convert files to CSV
4) Add station, station name, state, municipality, status, longitude, latitude as columns on the CSV file
5) Fill missing numerical data with statistical artifices
6) Fill missing dates
7) Make daily group
8) Make yearly-monthly group
9) make yearly group

## Functions (datascraper.py)
 **download(url, filename)** - This function downloads a file from a specific URL and saves it to a determined filename.   

**Input**
* url: string with the URL of the file to download
* filename: string with the name of the file to save the downloaded file
   
**Output: None**

**explore_download(start, end, output_folder)** - This function explores every url in a given range and saves the existing .txt files into an output folder
      
**Input**
* start: a number associated with a file
* end: final number to search in a range
* output_folder: string with the name of the folder where the found files will be saved
* estado: string with the state code (default is 'sin')

**Output: None**

**bulk_download(output_folder)** - This function downloads a range of files from the SMN website.
    
**Input**
* output_folder: string with the name of the folder where the files will be saved
* stations: list of strings with the code of the stations to download
* estado: string with the state code (default is 'sin')
        
**Output: None**


## Functions (data_cleaning.py)

**procesar_lote_txt_a_csv(directorio_entrada)** - This function receives a directory, detects the .txt files in it and processes them using the limpiar_txt_a_csv function.

**Input**
* directorio_entrada (String): The directory where the .txt files are located.
* umbral_faltantes (int): Maximum percentage of missing dates allowed.

**Output: None**

**limpiar_txt_a_csv(archivo_txt, directorio_salida)** - This function receives a .txt file with a specific structure, then it cleans and processes it and saves it as a .csv file.

**Input**
* archivo_txt (File): A .txt file with a specific structure.
* directorio_salida (String): The directory where the .csv file will be saved.
**Output: None**

**rellenar_fechas_faltantes(archivo_csv)** - This function receives the processed csv file and fills in the missing dates by calculating the min-max date range.
        
**Input**
* archivo_csv (File): csv file with missing dates.
* umbral_faltantes (int): Maximum percentage of missing dates allowed.
        
**Output: None**

**generar_concentrados_diarios(directorio_entrada)** - This function receives the directory of the raw files, locates the clean files folder and generates a single file containing all the daily summaries.

**Input**
* directorio_entrada (String): Folder where the RAW files are located

**Output: None**

**generar_concentrados_mensuales(directorio_entrada)** - This function receives the directory of the raw files, then locates the processed files folder and generates monthly summaries for each station.

**Input**
* directorio_entrada (String): folder where the original files are located
**Output: None**

**concatenar_concentrados(directorio_entrada)** - This function receives the directory of the raw files, then locates the monthly summaries folder and concatenates them into a single .csv file.

**Input**
* directorio_entrada (String): folder where the raw files are located
**Output: None**

## Cite as:
Mora-Félix et al (2025) J86-Year Meteorological Datasets from 50 Meteorological Stations in Sinaloa, Mexico with Daily, Monthly, and Yearly Resolutions. DOI: 10.17632/gb8jp62vm5.1


## Cite as:
Mora-Félix et al (2025) J86-Year Meteorological Datasets from 50 Meteorological Stations in Sinaloa, Mexico with Daily, Monthly, and Yearly Resolutions. DOI: 10.17632/gb8jp62vm5.1
