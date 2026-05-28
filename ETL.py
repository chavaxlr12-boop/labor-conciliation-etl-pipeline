import os
import sqlite3
import pandas as pd

def iniciar_pipeline_etl():
    print("[INFO] Iniciando Pipeline de Ingeniería de Datos...")
    
    #EXTRACCIÓN
    ruta_datos = '2025_2026_registros_conciliaciones_laborales.csv'
    if not os.path.exists(ruta_datos):
        print(f"[ERROR] No se encontró el archivo {ruta_datos}")
        return
        
    df_raw = pd.read_csv(ruta_datos, encoding='latin1')
    print(f"[INFO] Datos extraídos exitosamente. Registros: {df_raw.shape[0]}")
    
    print("[INFO] Transformando y limpiando datos...")
    df_clean = df_raw.copy()
    
    df_clean.columns = df_clean.columns.str.strip()

    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).str.strip()
            
    # Estandarizar valores numéricos
    df_clean['monto_pago'] = pd.to_numeric(df_clean['monto_pago'], errors='coerce').fillna(0.0)
    df_clean['total_trabajadores'] = pd.to_numeric(df_clean['total_trabajadores'], errors='coerce').fillna(0).astype(int)
    df_clean['total_hombres'] = pd.to_numeric(df_clean['total_hombres'], errors='coerce').fillna(0).astype(int)
    df_clean['total_mujeres'] = pd.to_numeric(df_clean['total_mujeres'], errors='coerce').fillna(0).astype(int)
    df_clean['total_no_especificado'] = pd.to_numeric(df_clean['total_no_especificado'], errors='coerce').fillna(0).astype(int)
    
    print("[INFO] Creando Modelo en Estrella (Dimensiones y Hechos)...")
    
    dim_ubicacion = df_clean[['entidad_registro', 'municipio_registro', 'ubicacion_establecimiento']].drop_duplicates().reset_index(drop=True)
    dim_ubicacion['id_ubicacion'] = dim_ubicacion.index + 1
    
    # Dimensión: Contrato
    dim_contrato = df_clean[['modalidad_contrato', 'clase_contrato']].drop_duplicates().reset_index(drop=True)
    dim_contrato['id_contrato'] = dim_contrato.index + 1

    dim_actividad = df_clean[['actividad_economica']].drop_duplicates().reset_index(drop=True)
    dim_actividad['id_actividad'] = dim_actividad.index + 1
    
    print("[INFO] Asociando llaves foráneas a la Tabla de Hechos...")
    df_fact = df_clean.merge(dim_ubicacion, on=['entidad_registro', 'municipio_registro', 'ubicacion_establecimiento'], how='left')
    df_fact = df_fact.merge(dim_contrato, on=['modalidad_contrato', 'clase_contrato'], how='left')
    df_fact = df_fact.merge(dim_actividad, on=['actividad_economica'], how='left')
    
    fact_conciliaciones = df_fact[[
        'id_ubicacion', 'id_contrato', 'id_actividad',
        'mes_registro', 'periodo_registro', 'motivo_convenio',
        'total_trabajadores', 'total_hombres', 'total_mujeres',
        'total_no_especificado', 'monto_pago', 'estatus_expediente'
    ]].copy()
    
    fact_conciliaciones.insert(0, 'id_conciliacion', fact_conciliaciones.index + 1)
    
    db_name = "dw_conciliaciones_laborales.db"
    print(f"[INFO] Cargando datos en el Data Warehouse local ({db_name})...")
    
    conexion = sqlite3.connect(db_name)
    
    #Guardamos cada DataFrame
    dim_ubicacion.to_sql('dim_ubicacion', conexion, if_exists='replace', index=False)
    dim_contrato.to_sql('dim_contrato', conexion, if_exists='replace', index=False)
    dim_actividad.to_sql('dim_actividad', conexion, if_exists='replace', index=False)
    fact_conciliaciones.to_sql('fact_conciliaciones', conexion, if_exists='replace', index=False)
    
    conexion.close()
    print("[SUCCESS] ¡Pipeline ejecutado con éxito! El archivo 'dw_conciliaciones_laborales.db' ha sido creado.")

if __name__ == "__main__":
    iniciar_pipeline_etl()