import pandas as pd
import re
import os
from numpy import nan

def procesar_lote_txt_a_csv(directorio_entrada, umbral_faltantes=100):
    """procesar_lote_txt_a_csv(directorio_entrada):
    
    This function receives a directory, detects the .txt files in it and processes them using the limpiar_txt_a_csv function.

    Input:
        directorio_entrada (String): The directory where the .txt files are located.
        umbral_faltantes (int): Maximum percentage of missing dates allowed.
    Return:
        None
    """
    directorio_salida = os.path.join(directorio_entrada, "limpio")
    os.makedirs(directorio_salida, exist_ok=True)
    for archivo in os.listdir(directorio_entrada):
        if archivo.endswith(".txt"):
            archivo_txt = os.path.join(directorio_entrada, archivo)
            limpiar_txt_a_csv(archivo_txt, directorio_salida)
            rellenar_fechas_faltantes(os.path.join(directorio_salida, f'NR_{archivo.replace(".txt", "")}.csv'), umbral_faltantes)

def limpiar_txt_a_csv(archivo_txt, directorio_salida):
    """limpiar_txt_a_csv(archivo_txt, directorio_salida):

    This function receives a .txt file with a specific structure, then it cleans and processes it and saves it as a .csv file.
    Input:
       - archivo_txt (File): A .txt file with a specific structure.
       - directorio_salida (String): The directory where the .csv file will be saved.
    Return: 
        None
    """

    codificacion = "utf-8"
    # REGEX para detectar la fecha en el formato YYYY-MM-DD
    regex = r'\d{4}-\d{2}-\d{2}'
    # Después de la línea 25 termina la cabecera, se espera que los datos comiencen
    linea_inicio = 25
    
    with open(archivo_txt, 'r', encoding=codificacion) as file:
        lineas = file.readlines()
    
    print(f'Procesando archivo {archivo_txt}')
    print(f'Número de líneas: {len(lineas)}')
    
    target_lines = [10, 11, 12, 13, 14, 16, 17, 18]
    etiquetas = []
    valores = []
    estacion = "Desconocida"
    
    for i in target_lines:
        if i < len(lineas) and ':' in lineas[i]:
            clave, valor = map(str.strip, re.split(r':\s*', lineas[i], maxsplit=1))
            valor = valor.replace('�', '').replace('°', '').replace('ｰ', '').replace("ï¿½", "")
            if clave == 'ALTITUD':
                valor = re.sub(r'\s*msnm', '', valor)
            etiquetas.append(clave)
            valores.append(valor)
        
        if "ESTACIÓN" in lineas[i]:  # Detección explícita de la estación
            match = re.search(r'ESTACIÓN\s*:\s*(\d+)', lineas[i])
            if match:
                estacion = match.group(1)
        if "ESTACION" in lineas[i]:
            match = re.search(r'ESTACION\s*:\s*(\d+)', lineas[i])
            if match:
                estacion = match.group(1)
    
    print(f'Estación detectada: {estacion}')
    datos = []
    
    for linea in lineas[linea_inicio:]:
        if re.match(regex, linea):
            valores_linea = re.split(r'\t+', linea.strip()) if '\t' in linea else re.split(r'\s+', linea.strip())
            if len(valores_linea) >= 5:
                datos.append(valores_linea[:5])
    
    if not datos:
        print("⚠️ Advertencia: No se encontraron datos climáticos en el archivo.")
        return
    
    columnas = ['FECHA', 'PRECIP', 'EVAP', 'TMAX', 'TMIN'] + etiquetas
    df = pd.DataFrame(datos, columns=columnas[:len(datos[0])])
    
    for i, etiqueta in enumerate(etiquetas):
        df[etiqueta] = valores[i] if i < len(valores) else ""
    
    df.replace('Nulo', None, inplace=True)
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y-%m-%d')
    df = df.dropna(subset=['FECHA'])
    df['MONTH'] = df['FECHA'].dt.month
    df['YEAR'] = df['FECHA'].dt.year
    
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df[column] = df.groupby(['YEAR', 'MONTH'])[column].transform(lambda x: x.fillna(x.mean() if not pd.isna(x.mean()) else nan))
    
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df[column] = df[column].astype(str).replace(nan, 'null')
    
    archivo_salida = os.path.join(directorio_salida, f'NR_{estacion}.csv')
    df.to_csv(archivo_salida, index=False, encoding='utf-8')
    print(f'Archivo CSV guardado como {archivo_salida}')

def rellenar_fechas_faltantes(archivo_csv, umbral_faltantes=100):
    
    """rellenar_fechas_faltantes(archivo_csv):

    This function receives the processed csv file and fills in the missing dates by calculating the min-max date range.
        
    Input:
       - archivo_csv (File): csv file with missing dates.
       - umbral_faltantes (int): Maximum percentage of missing dates allowed.
        
    Return: 
        None
    """
    
    df = pd.read_csv(archivo_csv, dayfirst=True)
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
    
    # Contar número de registros en el Dataframe df
    total_registros_original = df.shape[0]
    
    fecha_min = df['FECHA'].min()
    fecha_max = df['FECHA'].max()
    total_fechas = pd.date_range(start=fecha_min, end=fecha_max, freq='D')
    
    all_dates = pd.DataFrame({'FECHA': total_fechas})
    
    df_completo = all_dates.merge(df, on='FECHA', how='left')
    total_registros_generados = df_completo.shape[0]
    fechas_faltantes = total_registros_generados - total_registros_original
    porcentaje_faltante = (fechas_faltantes / total_registros_generados) * 100
    
    ## Si el porcentaje de fechas faltantes es mayor al umbral, se elimina el archivo y se detiene el proceso
    if porcentaje_faltante > umbral_faltantes:
        faltantes_msg = f"Entradas faltantes en {archivo_csv}\nTotal de entradas faltantes: {fechas_faltantes}\nPorcentaje de entradas faltantes: {porcentaje_faltante:.2f}%"
        print(faltantes_msg)
        print(f'El porcentaje de fechas faltantes es mayor al umbral permitido ({umbral_faltantes}%)')
        os.remove(archivo_csv)
        print(f'Archivo descartado: {archivo_csv}')
        return    
    else:
        df_completo['MONTH'] = df_completo['FECHA'].dt.month
        df_completo['YEAR'] = df_completo['FECHA'].dt.year
        
        if not df_completo.empty:
            if 'ESTACION' in df.columns:
                constantes = ['ESTACION', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            else:
                constantes = ['ESTACIÓN', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            for const in constantes:
                df_completo[const] = df[const].iloc[0] if const in df.columns and not df[const].isna().all() else "Desconocida"          
            for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
                df_completo[column] = df_completo[column].astype(str).replace(nan, 'null')
                df_completo[column] = df_completo[column].astype(str).replace('nan', 'null')
        df_completo = df_completo.astype(str).replace('nan', 'null')
        df_completo.to_csv(archivo_csv, index=False, encoding='utf-8')    
    log_msg = f"Entradas faltantes rellenadas en {archivo_csv}\nTotal de entradas faltantes: {fechas_faltantes}\nPorcentaje de entradas faltantes: {porcentaje_faltante:.2f}%"
    print(log_msg)

def generar_concentrados_diarios(directorio_entrada):
    """generar_concentrados_diarios(directorio_entrada):
    
    This function receives the directory of the raw files, locates the clean files folder and generates a single file containing all the daily summaries.

    Input:
        directorio_entrada (String): Folder where the RAW files are located
    Return: None
    """
    directorio_limpios = os.path.join(directorio_entrada, "limpio")
    archivos_csv = [os.path.join(directorio_limpios, f) for f in os.listdir(directorio_limpios) if f.endswith(".csv")]
    df_final = pd.concat([pd.read_csv(f) for f in archivos_csv], ignore_index=True)
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df_final[column] = df_final[column].astype(str).replace(nan, 'null')
        df_final[column] = df_final[column].astype(str).replace('nan', 'null')
    archivo_final = os.path.join(directorio_limpios, 'CD.csv')
    df_final.to_csv(archivo_final, index=False, encoding='utf-8')
    print(f'Archivo final de concentrado diario guardado como {archivo_final}')

def generar_concentrados_mensuales(directorio_entrada):
    """generar_concentrados_mensuales(directorio_entrada):
    
    This function receives the directory of the raw files, then locates the processed files folder and generates monthly summaries for each station.

    Input:
        directorio_entrada (String): folder where the original files are located
    Return:
        None
    """
    directorio_limpios = os.path.join(directorio_entrada, "limpio")
    directorio_concentrado = os.path.join(directorio_entrada, "CM")
    os.makedirs(directorio_concentrado, exist_ok=True)
    archivos_csv = [os.path.join(directorio_limpios, f) for f in os.listdir(directorio_limpios) if f.endswith(".csv")]
    
    for archivo in archivos_csv:
        df = pd.read_csv(archivo)
        
        df_mensual = df.groupby(['YEAR', 'MONTH']).agg({
            'PRECIP': 'sum',
            'EVAP': 'mean',
            'TMAX': 'max',
            'TMIN': 'min'
        }).reset_index()
        
        if not df_mensual.empty:
            if 'ESTACION' in df.columns:
                constantes = ['ESTACION', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            else:
                constantes = ['ESTACIÓN', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            for const in constantes:
                df_mensual[const] = df[const].iloc[0] if const in df.columns and not df[const].isna().all() else "Desconocida"
        
            for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
                df_mensual[column] = df_mensual[column].astype(str).replace(nan, 'null')
                df_mensual[column] = df_mensual[column].astype(str).replace('nan', 'null')

            if 'ESTACION' in df.columns:
                archivo_concentrado = os.path.join(directorio_concentrado, f'CM_{df["ESTACION"].iloc[0]}.csv')
            else:
                archivo_concentrado = os.path.join(directorio_concentrado, f'CM_{df_mensual["ESTACIÓN"].iloc[0]}.csv')
            df_mensual.to_csv(archivo_concentrado, index=False, encoding='utf-8')
            print(f'Archivo de concentrado mensual guardado como {archivo_concentrado}')


def generar_concentrados_anuales(directorio_entrada):
    """generar_concentrados_anuales(directorio_entrada):
    
    This function receives the directory of the raw files, then locates the processed files folder and generates yearly summaries for each station.

    Input:
        directorio_entrada (String): folder where the original files are located
    Return:
        None
    """
    directorio_limpios = os.path.join(directorio_entrada, "limpio")
    directorio_concentrado = os.path.join(directorio_entrada, "CA")
    os.makedirs(directorio_concentrado, exist_ok=True)
    archivos_csv = [os.path.join(directorio_limpios, f) for f in os.listdir(directorio_limpios) if f.endswith(".csv")]
    
    for archivo in archivos_csv:
        df = pd.read_csv(archivo)
        
        df_mensual = df.groupby(['YEAR']).agg({
            'PRECIP': 'sum',
            'EVAP': 'mean',
            'TMAX': 'max',
            'TMIN': 'min'
        }).reset_index()
        
        if not df_mensual.empty:
            if 'ESTACION' in df.columns:
                constantes = ['ESTACION', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            else:
                constantes = ['ESTACIÓN', 'NOMBRE', 'ESTADO', 'MUNICIPIO', 'SITUACIÓN', 'LATITUD', 'LONGITUD', 'ALTITUD']
            for const in constantes:
                df_mensual[const] = df[const].iloc[0] if const in df.columns and not df[const].isna().all() else "Desconocida"
        
            for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
                df_mensual[column] = df_mensual[column].astype(str).replace(nan, 'null')
                df_mensual[column] = df_mensual[column].astype(str).replace('nan', 'null')

            if 'ESTACION' in df.columns:
                archivo_concentrado = os.path.join(directorio_concentrado, f'CA_{df["ESTACION"].iloc[0]}.csv')
            else:
                archivo_concentrado = os.path.join(directorio_concentrado, f'CA_{df_mensual["ESTACIÓN"].iloc[0]}.csv')
            df_mensual.to_csv(archivo_concentrado, index=False, encoding='utf-8')
            print(f'Archivo de concentrado anual guardado como {archivo_concentrado}')

def concatenar_concentrados(directorio_entrada):
    """concatenar_concentrados(directorio_entrada):
    
    This function receives the directory of the raw files, then locates the monthly and yearly summaries folder and concatenates them into two csv files.

    Input:
        directorio_entrada (String): folder where the raw files are located
    Return:
        None
    """
    directorio_concentrado_mensual = os.path.join(directorio_entrada, "CM")
    directorio_concentrado_anual = os.path.join(directorio_entrada, "CA")
    directorio_final = os.path.join(directorio_entrada, "FINAL")
    
    os.makedirs(directorio_final, exist_ok=True)
    
    archivos_csv_mensual = [os.path.join(directorio_concentrado_mensual, f) for f in os.listdir(directorio_concentrado_mensual) if f.endswith(".csv")]
    
    df_final_mensual = pd.concat([pd.read_csv(f) for f in archivos_csv_mensual], ignore_index=True)
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df_final_mensual[column] = df_final_mensual[column].astype(str).replace(nan, 'null')
        df_final_mensual[column] = df_final_mensual[column].astype(str).replace('nan', 'null')
    archivo_final_mensual = os.path.join(directorio_final, 'FINAL_MENSUAL.csv')
    df_final_mensual.to_csv(archivo_final_mensual, index=False, encoding='utf-8')
    print(f'Archivo final concatenado guardado como {archivo_final_mensual}')
    
    archivos_csv_anual = [os.path.join(directorio_concentrado_anual, f) for f in os.listdir(directorio_concentrado_anual) if f.endswith(".csv")]
    
    df_final_anual = pd.concat([pd.read_csv(f) for f in archivos_csv_anual], ignore_index=True)
    for column in ['PRECIP', 'EVAP', 'TMAX', 'TMIN']:
        df_final_anual[column] = df_final_anual[column].astype(str).replace(nan, 'null')
        df_final_anual[column] = df_final_anual[column].astype(str).replace('nan', 'null')
    archivo_final_anual = os.path.join(directorio_final, 'FINAL_ANUAL.csv')
    df_final_anual.to_csv(archivo_final_anual, index=False, encoding='utf-8')
    print(f'Archivo final concatenado guardado como {archivo_final_anual}')   
