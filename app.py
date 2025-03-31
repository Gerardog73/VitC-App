
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Vitamina C Personalizada", layout="centered")
st.title("🧬 Calculadora Personalizada de Vitamina C")
st.markdown("Calculá tu dosis ortomolecular ideal de ácido ascórbico basada en tu genética, peso, edad y estilo de vida.")

# ==== INPUTS ====
st.subheader("🔍 Ingresá tu información genética y clínica")
snp_inputs = {
    'SLC23A1_rs33972313': st.selectbox("SLC23A1_rs33972313 (TT, TG, GG):", ['TT', 'TG', 'GG']),
    'SLC23A2_rs12479919': st.selectbox("SLC23A2_rs12479919 (GG, AG, AA):", ['GG', 'AG', 'AA']),
    'GSTT1_null_variant': st.selectbox("GSTT1 (del/del, ins/del, ins/ins):", ['del/del', 'ins/del', 'ins/ins']),
    'GSTM1_null_variant': st.selectbox("GSTM1 (del/del, ins/del, ins/ins):", ['del/del', 'ins/del', 'ins/ins']),
    'GPX1_rs1050450': st.selectbox("GPX1_rs1050450 (TT, CT, CC):", ['TT', 'CT', 'CC'])
}

edad = st.slider("📅 Edad", min_value=10, max_value=100, value=35)
peso = st.number_input("⚖️ Peso corporal (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
fuma = st.checkbox("🚬 ¿Fumás?")
estres = st.checkbox("😰 ¿Tenés estrés físico o emocional elevado?")
infeccion = st.checkbox("🤒 ¿Tenés una infección o enfermedad crónica activa?")

# ==== PARÁMETROS GENÉTICOS ====
snp_data = {
    'SLC23A1_rs33972313': {'beta': -0.4, 'description': '↓ transporte de vitamina C', 'is_risk': True},
    'SLC23A2_rs12479919': {'beta': -0.3, 'description': '↓ absorción intestinal', 'is_risk': True},
    'GSTT1_null_variant': {'beta': -0.5, 'description': '↓ defensa antioxidante', 'is_risk': True},
    'GSTM1_null_variant': {'beta': -0.3, 'description': '↓ detoxificación de radicales libres', 'is_risk': True},
    'GPX1_rs1050450': {'beta': -0.2, 'description': '↓ eficiencia de glutatión peroxidasa', 'is_risk': True},
}

genotype_to_count = {
    'TT': 2, 'TG': 1, 'GG': 0,
    'AA': 0, 'AG': 1,
    'del/del': 2, 'ins/del': 1, 'ins/ins': 0,
    'CC': 0, 'CT': 1
}

# ==== CÁLCULOS ====
prs_score = 0
risk_snps = 0
prs_details = []

for snp, params in snp_data.items():
    geno = snp_inputs[snp]
    count = genotype_to_count.get(geno, 0)
    effect = count * params['beta']
    prs_score += effect
    if params['is_risk'] and count > 0:
        risk_snps += 1
    prs_details.append({
        'SNP': snp,
        'Genotipo': geno,
        'Efecto': round(effect, 2),
        'Descripción': params['description']
    })

# ==== INTERPRETACIÓN ====
if prs_score <= -1:
    interpretation = "❌ Baja respuesta esperada al ácido ascórbico"
elif -1 < prs_score <= 0.5:
    interpretation = "⚠️ Respuesta moderada esperada al ácido ascórbico"
else:
    interpretation = "✅ Buena respuesta esperada al ácido ascórbico"

# ==== AJUSTE DOSIS ====
dosis_base = 2000  # mg/día
factor_gen = 1 + 0.25 * risk_snps
factor_peso = peso / 70
factor_edad = 1.2 if edad >= 60 else 1.0
factor_fumador = 1.2 if fuma else 1.0
factor_estres = 1.3 if estres else 1.0
factor_infeccion = 1.5 if infeccion else 1.0

recom_dosis = round(dosis_base * factor_gen * factor_peso * factor_edad * factor_fumador * factor_estres * factor_infeccion, 2)

# ==== RESULTADOS ====
st.subheader("📊 Resultados personalizados")
st.markdown(f"**PRS total:** {prs_score:.2f}")
st.markdown(f"**Interpretación clínica:** {interpretation}")
st.markdown(f"**SNPs de riesgo detectados:** {risk_snps}")
st.markdown(f"**💊 Dosis personalizada recomendada:** `{recom_dosis} mg/día` (fraccionada)")

# ==== GRÁFICO ====
plot_df = pd.DataFrame(prs_details)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(plot_df['SNP'], plot_df['Efecto'], color='orange')
ax.axvline(0, color='black', linestyle='--')
ax.set_xlabel('Contribución al PRS')
ax.set_title('Impacto genético por SNP')
st.pyplot(fig)

# ==== EXPORTACIÓN ====
st.subheader("📥 Exportar resultado")
result_df = plot_df.copy()
result_df.loc[len(result_df.index)] = ['Total PRS', '', prs_score, interpretation]
result_df.loc[len(result_df.index)] = ['SNPs de riesgo', '', risk_snps, '']
result_df.loc[len(result_df.index)] = ['Dosis recomendada (mg/día)', '', recom_dosis, 'Ajuste según genética, peso y condiciones']

csv = result_df.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Descargar CSV con resultados", csv, "vitamina_c_webapp.csv", "text/csv")
