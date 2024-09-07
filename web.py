import pandas as pd
import streamlit as st
import plotly.express as px

# Cargar los datos desde un archivo de Excel
data = pd.read_excel("https://github.com/nmonterroza/webN/blob/main/cargarap.xlsx")

# Mostrar las columnas disponibles en el DataFrame
print(data.columns)

# Configuración de la barra lateral para seleccionar facultad y programa
with st.sidebar:
    # Selección de facultades
    facultad_seleccionada = st.multiselect('Facultad', sorted(data['facultad'].unique()))

    # Filtrar programas basados en la facultad seleccionada
    if facultad_seleccionada:
        programas_disponibles = data[data['facultad'].isin(facultad_seleccionada)]['programa'].unique()
        programa_seleccionado = st.multiselect('Programa', sorted(programas_disponibles))
    else:
        programa_seleccionado = st.multiselect('Programa', sorted(data['programa'].unique()))

# Función para filtrar los datos según las selecciones de facultad y programa
def filter_data(df, facultad_seleccionada, programa_seleccionado):
    df_copy = df.copy()

    if len(facultad_seleccionada) > 0:
        df_copy = df_copy[df_copy['facultad'].isin(facultad_seleccionada)]

    if len(programa_seleccionado) > 0:
        df_copy = df_copy[df_copy['programa'].isin(programa_seleccionado)]

    # Eliminar duplicados por profesor y programa
    df_copy = df_copy.drop_duplicates(subset=['idusuario', 'programa'])
    
    return df_copy

# Aplicar el filtro a los datos
df_filtrado = filter_data(data, facultad_seleccionada, programa_seleccionado)

# Mostrar título de la aplicación
st.title("Ingreso a Cintia")

# Calcular métricas de interés
ingreso_medio = df_filtrado['accesos_plataforma'].mean()
profesores = len(df_filtrado['idusuario'].unique())

# Mostrar métricas en columnas
col1, col2 = st.columns(2)
col1.metric('Ingreso Medio', f"{ingreso_medio:,.0f}")
col2.metric('Profesores', f"{profesores:,.0f}")

# Verificar si hay datos filtrados antes de crear los gráficos
if not df_filtrado.empty:
    # Crear el boxplot usando Plotly y agregar idusuario como hover_data
    fig_boxplot = px.box(
        df_filtrado,
        x='facultad',
        y='accesos_plataforma',
        color='programa',  # Colorear por programa para mayor diferenciación
        title='Distribución de Accesos por Facultad y Programa',
        labels={'accesos_plataforma': 'Accesos a Plataforma', 'facultad': 'Facultad'},
        points='all',  # Mostrar todos los puntos para más detalle
        hover_data=['idusuario']  # Mostrar el ID del profesor al pasar el cursor
    )

    # Mostrar el boxplot en la aplicación
    st.plotly_chart(fig_boxplot, use_container_width=True)

    # Crear histogramas de accesos por programa
    fig_histogram = px.histogram(
        df_filtrado,
        x='accesos_plataforma',
        color='programa',
        nbins=20,
        title='Histograma de Accesos por Programa',
        labels={'accesos_plataforma': 'Accesos a Plataforma'},
        marginal='rug',  # Agregar líneas marginales para más detalle
        hover_data=['idusuario']  # Mostrar el ID del profesor al pasar el cursor
    )

    # Mostrar el histograma debajo del boxplot
    st.plotly_chart(fig_histogram, use_container_width=True)

    # Eliminar duplicados por facultad y profesor para el diagrama de barras
    df_unicos = df_filtrado.drop_duplicates(subset=['idusuario', 'facultad'])

    # Crear un diagrama de barras para mostrar los ingresos por facultad
    ingresos_por_facultad = df_unicos.groupby('facultad')['accesos_plataforma'].sum().reset_index()

    fig_bar = px.bar(
        ingresos_por_facultad,
        x='facultad',
        y='accesos_plataforma',
        title='Total de Ingresos por Facultad (Sin Duplicados)',
        labels={'accesos_plataforma': 'Total de Accesos', 'facultad': 'Facultad'},
        color='facultad',  # Colorear por facultad para mayor diferenciación
        text='accesos_plataforma'  # Mostrar el total de accesos en las barras
    )

    # Mostrar el diagrama de barras debajo de los otros gráficos
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.warning("No hay datos para los filtros seleccionados.")
