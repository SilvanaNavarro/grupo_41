import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta

ruta = 'src/data.csv'#Setear ruta a csv

# Configuracón básica de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Configuración simple para los gráficos
sns.set_style('whitegrid')

# Función para cargar datos con caché para mejorar rendimiento
@st.cache_data
def load_data(ruta):
    df = pd.read_csv(ruta)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df_ventas = df[['Total','Date']].groupby('Date').sum().reset_index()
    # df['Month'] = df['Date'].dt.month  # Número del mes (1-12)
    # df['Year'] = df['Date'].dt.year     # Año (ej. 2019)
    # df['Day'] = df['Date'].dt.day
    products = list(df['Product line'].unique())
    df_products = df_ventas
    for product in products:
        df_product = df[df['Product line']==product][['Date','Total']].groupby('Date').sum().reset_index()
        df_products = df_products.join(df_product.set_index('Date'),on='Date',validate='1:1',rsuffix=f'_{product}')
    return df,df_ventas,df_products

df,df_ventas,df_products = load_data(ruta)

min_date = df['Date'].min()
max_date = df['Date'].max()
default_init = max_date - timedelta(days=7)

st.sidebar.header('Filtros del dashboard') #Título de barra lateral
# Selector de rango de fechas
date_range = st.sidebar.date_input(
    'Selecciona un rango de fechas',
    value=(default_init, max_date),  # Rango inicial
    min_value=min_date,
    max_value=max_date
)

# Selector de línea de productos
linea_productos = st.sidebar.multiselect(
    'Línea de productos',
    options=list(set(df_products.columns) - {'Total','Date'}),
    default=list(set(df_products.columns) - {'Total','Date'}),
    help="Selecciona los componentes para visualizar las ventas por línea de producto deseada sólo para el gráfico de ventas por línea de productos"
)

### Título principal
st.title("💹 Análisis de ventas")
st.write("Análisis estratégico de ventas y comportamiento de clientes de una tienda de conveniencia")

##Gráficos
st.subheader("Total de ventas en el tiempo")
#Evolución de ventas totales


# Creamos una fila con dos gráficos: PIB y Variables Porcentuales
c1_f1, c2_f1 = st.columns(2)

# Diccionario para traducir nombres de variables
# nombres = {
#     'gdp': 'PIB', 
#     'unemp': 'Desempleo', 
#     'inflation': 'Inflación'
# }

with c1_f1:
    if len(date_range)==2:
        df_products = df_products[(df_products['Date'].dt.date >= date_range[0]) & (df_products['Date'].dt.date <= date_range[1])]
        df_ventas = df_products[['Date','Total']]
        st.write("### Evolución del total de ventas")
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Graficamos el PIB agrupado por año
        df_venta_productos = df_ventas
        sns.lineplot(
            data=df_venta_productos, 
            x='Date', 
            y='Total', 
            color="#0003ac",
            ax=ax
        )

        # Configuración del gráfico
        ax.set_ylabel('Total de ventas $')
        ax.set_title("Tendencia de ventas en el tiempo")
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("*El gráfico muestra la evolución de las ventas a lo largo del tiempo, permitiendo identificar volumen de ventas.*")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")

with c2_f1:
    if len(date_range)==2:
        st.write("### Detalle de ventas por linea de productos en el tiempo")
        if linea_productos:
            # Creamos un gráfico de área para mostrar la evolución temporal
            fig, ax = plt.subplots(figsize=(6, 3))
            
            # Graficamos los componentes seleccionados
            # Agrupamos por año para simplificar
            df_prod = df_products.groupby('Date')[linea_productos].sum()

            df_prod.plot.area(
                ax=ax
            )
            
            # Etiquetas y cuadrícula
            ax.set_ylabel("Total de ventas $")
            ax.set_title("Ventas por línea de productos")
            ax.grid(True, alpha=0.3)
            ax.legend(framealpha=0.6,
                    prop={'size': 5})
            
            # Mostramos el gráfico en Streamlit
            st.pyplot(fig)
            st.write("*El gráfico muestra la evolución de las ventas diferenciadas por producto a lo largo del tiempo, permitiendo identificar tipo de productos según su volumen de ventas.*")
        else:
            st.info("Selecciona al menos una línea de productos")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")

# Data para análisis de clasificación de clientes
df_clasificacion = df[['Date','Customer type','Gender','Rating','Product line']].groupby(['Date','Customer type','Gender','Product line']).mean().reset_index()

st.subheader("Distribución de la Calificación de Clientes")
c1_f2, c2_f2 = st.columns(2)

# 1. Procesar los datos
    # Calcular el promedio de rating por fecha y género
with c1_f2:
    if len(date_range)==2:
        st.write("### Calificaciones de ventas por género de clientes")
        df_promedio = df[(df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])].groupby(['Date', 'Gender'])['Rating'].mean().reset_index()

        # 2. Crear el gráfico
        fig, ax = plt.subplots(figsize=(10, 6))

        # Filtrar y graficar cada género por separado
        for genero in list(df['Gender'].unique()):
            datos_genero = df_promedio[df_promedio['Gender'] == genero]
            ax.plot(datos_genero['Date'], datos_genero['Rating'], 
                    label=genero, marker='o', linestyle='-')

        # 3. Personalizar el gráfico
        ax.set_title('Promedio de calificaciones diarias por Género a lo largo del tiempo')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Rating Promedio')
        ax.legend(title='Género', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.6)

        # Rotar etiquetas de fecha para mejor visualización
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 4. Mostrar en Streamlit
        st.pyplot(fig)
        st.write("*Muestra la distribución de las calificaciones de los clientes en el período seleccionado, mostrando su promedio diario por género.*")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")

# Histograma de Inflación
with c2_f2:
    if len(date_range)==2:
        st.write("### Distribución de las calificaciones")
        
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Crear histograma
        ax.hist(
            df['Rating'],
            bins=15,
            color="#0F0350",
            alpha=0.7,
            edgecolor='black'
        )
        
        # Configuración del gráfico
        ax.set_xlabel('Calificaciones')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Distribución de las calificaciones')
        ax.grid(True, alpha=0.3)
        
        # Mostrar línea vertical en la media
        media = df[(df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])]['Rating'].mean()
        ax.axvline(media, color='black', linestyle='dashed', linewidth=1, label=f'Media: {media:.2f}%')
        ax.legend()
        
        # Mostrar gráfico
        st.pyplot(fig)
        st.write("*Visualiza la distribución de las calificaciones de los clientes en el período seleccionado, monstrando la media del total de calificaciones.*")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")
#Gráfico de gasto por tipo de clientes
c1_f3, c2_f3 = st.columns([7,3])

with c1_f3:
    st.write("### Detalle de ventas por tipo de cliente en el tiempo")
    if len(date_range)==2:
        df_clients = df[(df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])]
        # Creamos un gráfico de área para mostrar la evolución temporal
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Graficamos los componentes seleccionados
        # Agrupamos por fecha
        for client in list(df['Customer type'].unique()):
            df_client = df_clients[df_clients['Customer type']==client][['Date','Total']].groupby('Date').sum()
            df_client = df_client.rename(columns={'Total':client})
            df_client.plot.area(
                ax=ax
            )
        
        # Etiquetas y cuadrícula
        ax.set_ylabel("Total de ventas $")
        ax.set_title("Ventas por tipo de cliente")
        ax.grid(True, alpha=0.3)
        ax.legend(framealpha=0.6,
                  prop={'size': 5})
        
        # Mostramos el gráfico en Streamlit
        st.pyplot(fig)
        st.write("*El gráfico muestra la distribución de las ventas diferenciadas por tipo de cliente a lo largo del tiempo.*")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")
with c2_f3:
    st.write("### Porcentaje de ventas por tipo de cliente")

    if len(date_range)==2:
        df_cl = df[(df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])]
        df_cl = df_cl.groupby('Customer type')['Total'].sum().reset_index()
        # Colores personalizados (opcional)
        colores = ["#0E005A", "#1587BB"]

        # Crear el pie chart
        ax.pie(df_cl['Total'],
            autopct='%1.1f%%',  # Muestra porcentajes con 1 decimal
            startangle=90,      # Ángulo inicial    # Colores personalizados
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'},  # Borde blanco
            textprops={'fontsize': 12})  # Tamaño de fuente

        # Título
        ax.set_title('Distribución de Ventas por tipo de cliente')
        
        # Mostramos el gráfico
        st.pyplot(fig)
        st.write("*El gráfico muestra el porcentaje del total de ventas por tipo de cliente.*")
    else:
        st.info("Selecciona inicio y fin de periodo a observar ")

#Gráfico 4 fila 
if len(date_range)==2:
    df_incomes = df[(df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])].groupby('Date')[['cogs','gross income']].sum().reset_index()
    df_incomes = df_incomes.rename(columns={'cogs':'Costo','gross income':'Ingreso bruto'})

    df_melted = df_incomes.melt(
        id_vars='Date', 
        value_vars=['Costo', 'Ingreso bruto'],
        var_name='Metric', 
        value_name='Monto'
    )

    # Crear gráfico
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_melted,
        x='Date',
        y='Monto',
        hue='Metric',
        palette=["#032C69", '#7FBFFF']
    )

    plt.title('Relación entre el costo de bienes vendidos y el ingreso bruto')
    plt.xlabel('Fecha')
    plt.ylabel('Monto')
    plt.xticks(rotation=45)
    ax.set_xticks(ax.get_xticks()[::2])  # Mostrar cada segunda etiqueta
    ax.set_xticklabels(ax.get_xticklabels()[::2])  # Aplicar a los labels
    plt.legend(title='Métrica')

    # Mostrar en Streamlit
    st.pyplot(plt.gcf())
else:
    st.info("Selecciona inicio y fin de periodo a observar ")





# Pie de página 
st.markdown("---")
st.caption("Dashboard Tendencia de Ventas | Datos: data.csv")

