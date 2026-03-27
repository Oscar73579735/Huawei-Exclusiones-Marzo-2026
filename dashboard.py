import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
plt.style.use("dark_background")

# =========================
# ⚙️ CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #ffffff;
}
h1, h2, h3 {
    color: #00c8ff;
}
.stMetric {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #00c8ff;
}
.stDownloadButton button {
    background-color: #00c8ff;
    color: black;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 📥 CARGA DE DATOS (LO MÁS IMPORTANTE)
# =========================
df = pd.read_excel("DATA_MARZO_2026_IA.xlsx")

# =========================
# 🧹 LIMPIEZA
# =========================
df["EXCLUIDO"] = df["EXCLUIDO"].astype(str).str.upper()
df["TIEMPO_FALLA"] = pd.to_numeric(df["TIEMPO_FALLA"], errors="coerce")

# =========================
# 🎯 TÍTULO
# =========================
st.title("📊 Dashboard Huawei - Exclusiones Marzo 2026")

# =========================
# 🎛️ FILTROS
# =========================
col1, col2 = st.columns(2)

with col1:
    filtro_clasificacion = st.selectbox(
        "Clasificación",
        ["Todos"] + list(df["Clasificación"].dropna().unique())
    )

with col2:
    filtro_categoria = st.selectbox(
        "Categoría MINTIC",
        ["Todos"] + list(df["Categoría MINTIC"].dropna().unique())
    )

if filtro_clasificacion != "Todos":
    df = df[df["Clasificación"] == filtro_clasificacion]

if filtro_categoria != "Todos":
    df = df[df["Categoría MINTIC"] == filtro_categoria]

# =========================
# 📊 KPIs
# =========================
total = len(df)
excluidos = df[df["EXCLUIDO"] == "SI"].shape[0]
no_excluidos = df[df["EXCLUIDO"] == "NO"].shape[0]
porcentaje = (excluidos / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Registros", total)
col2.metric("Excluidos", excluidos)
col3.metric("% Exclusión", f"{porcentaje:.2f}%")

# =========================
# 🚨 ALERTA
# =========================
if porcentaje > 70:
    st.error("🔴 CRÍTICO: Nivel muy alto de exclusiones")
elif porcentaje > 40:
    st.warning("🟡 ALERTA: Nivel medio de exclusiones")
else:
    st.success("🟢 Nivel controlado")

# =========================
# 📊 GRÁFICOS PRINCIPALES
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución de Exclusiones")
    conteo = df["EXCLUIDO"].value_counts()

    fig, ax = plt.subplots()
    conteo.plot(kind="bar", ax=ax, color="#00c8ff")
    fig.patch.set_facecolor("#0e1117")
    st.pyplot(fig)

with col2:
    st.subheader("Proporción de Exclusiones")

    fig1, ax1 = plt.subplots()
    df["EXCLUIDO"].value_counts().plot.pie(
        autopct='%1.1f%%',
        colors=["#00c8ff", "#ff4b4b"],
        textprops={'color': "white"},
        ax=ax1
    )
    fig1.patch.set_facecolor("#0e1117")
    st.pyplot(fig1)

# =========================
# 🔍 ANÁLISIS NO EXCLUIDOS
# =========================
st.subheader("🧠 Análisis de casos NO excluidos")

df_no = df[df["EXCLUIDO"] == "NO"]

if len(df_no) > 0:

    col1, col2 = st.columns(2)

    # 📊 Clasificación
    with col1:
        st.write("📌 Clasificación más frecuente (NO excluidos)")
        clasif_no = df_no["Clasificación"].value_counts().head(5)
        st.bar_chart(clasif_no)

    # 📊 Categoría
    with col2:
        st.write("📌 Categorías más frecuentes (NO excluidos)")
        cat_no = df_no["Nombre Categoría"].value_counts().head(5)
        st.bar_chart(cat_no)

    # 📊 Región
    st.write("🌍 Regiones con más NO excluidos")
    region_no = df_no["Regional"].value_counts()
    st.bar_chart(region_no)

    # ⏱️ Tiempo promedio
    tiempo_no = df_no["TIEMPO_FALLA"].mean()
    st.metric("⏱️ Tiempo promedio NO excluidos", round(tiempo_no, 2))

else:
    st.info("No hay registros NO excluidos en el filtro actual.")

# =========================
# 🤖 INSIGHT AUTOMÁTICO
# =========================
st.subheader("Conclusiones sobre NO excluidos")

if len(df_no) > 0:

    top_clasif_no = df_no["Clasificación"].value_counts().idxmax()
    top_cat_no = df_no["Nombre Categoría"].value_counts().idxmax()
    top_region_no = df_no["Regional"].value_counts().idxmax()

    st.write(f"""
    - La mayoría de casos NO excluidos pertenecen a la clasificación: **{top_clasif_no}**
    - La categoría más frecuente es: **{top_cat_no}**
    - La región con más casos NO excluidos es: **{top_region_no}**

    👉 Esto puede indicar oportunidades de mejora en criterios de exclusión o gestión operativa.
    """)

else:
    st.write("No hay datos suficientes para generar conclusiones.")

# =========================
# 📊 ANÁLISIS
# =========================
st.subheader("Exclusiones por Clasificación")
st.bar_chart(df[df["EXCLUIDO"] == "SI"]["Clasificación"].value_counts())

st.subheader("Top 10 Categorías con más Exclusiones")
st.bar_chart(df[df["EXCLUIDO"] == "SI"]["Nombre Categoría"].value_counts().head(10))

st.subheader("Exclusiones por Región")
st.bar_chart(df[df["EXCLUIDO"] == "SI"]["Regional"].value_counts())

st.subheader("Exclusiones por Municipio")
st.bar_chart(df[df["EXCLUIDO"] == "SI"]["MUNICIPIO"].value_counts().head(10))

# =========================
# ⏱️ TIEMPO PROMEDIO
# =========================
promedio = df["TIEMPO_FALLA"].mean()
st.metric("⏱️ Tiempo promedio (min)", round(promedio, 2))

# =========================
# 📊 GESTIÓN
# =========================
st.subheader("Gestión de casos")
st.bar_chart(df["GESTION"].value_counts())

# =========================
# 📋 TABLA
# =========================
st.subheader("Detalle de datos")
st.dataframe(df)

# =========================
# 📤 EXPORTAR
# =========================
st.subheader("Descargar reporte")

output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Reporte')

st.download_button(
    label="📥 Descargar Excel",
    data=output.getvalue(),
    file_name="reporte_exclusiones.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =========================
# 🧠 CONCLUSIONES
# =========================
st.subheader("Conclusiones automáticas")

if excluidos > 0:
    top_categoria = df[df["EXCLUIDO"] == "SI"]["Nombre Categoría"].value_counts().idxmax()
    top_region = df[df["EXCLUIDO"] == "SI"]["Regional"].value_counts().idxmax()

    st.write(f"""
    - Categoría más crítica: **{top_categoria}**
    - Región más afectada: **{top_region}**
    - Recomendación: priorizar estas áreas.
    """)
else:
    st.write("No hay exclusiones en los datos filtrados.")

fig, ax = plt.subplots()

# Fondo oscuro
fig.patch.set_facecolor("#0e1117")
ax.set_facecolor("#0e1117")

# Barras
conteo.plot(
    kind="bar",
    ax=ax,
    color=["#00c8ff", "#ff4b4b"]
)

# Texto blanco
ax.set_title("Distribución de Exclusiones", color="white")
ax.set_xlabel("EXCLUIDO", color="white")
ax.set_ylabel("Cantidad", color="white")

# Ejes en blanco
ax.tick_params(colors="white")

# Quitar bordes feos
for spine in ax.spines.values():
    spine.set_color("#444")

st.pyplot(fig)

fig1, ax1 = plt.subplots()

fig1.patch.set_facecolor("#0e1117")
ax1.set_facecolor("#0e1117")

df["EXCLUIDO"].value_counts().plot.pie(
    autopct='%1.1f%%',
    colors=["#00c8ff", "#ff4b4b"],
    textprops={'color': "white", 'fontsize': 12},
    wedgeprops={'edgecolor': '#0e1117'},
    ax=ax1
)

ax1.set_ylabel("")  # quitar "count" feo

st.pyplot(fig1)
