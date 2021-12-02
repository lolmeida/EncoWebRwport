import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cutecharts.charts import Line
from PIL import Image

import report_data as data
import streamlit as st

# -------------------------------------------------------------------------------
st.set_page_config(page_title="ENCO Monthly Report", layout="wide")
#@st.cache
def getData():
    gcp = (
        data.get_xls_data(id_src=1, formated=True).dropna().reset_index(drop=True)
    )  
    cbl = (
        data.get_xls_data(id_src=0, formated=True).dropna().reset_index(drop=True)
    )  

    grf_gcp = (
        data.get_xls_data(id_src=1, formated=False).dropna().reset_index(drop=True)
    )

    grf_cbl = (
        data.get_xls_data(id_src=0, formated=False).dropna().reset_index(drop=True)
    )
    crit = data.getCriterios()
    txt = data.getTxt()
    orc_mapa = data.get_orc_mapa()
    #rhp = data.get_Rhp()
    profits_losts = data.get_ProfitsAndLosts() 
    users = data.get_users_dict()
    
    return gcp, cbl, grf_gcp, grf_cbl, crit, txt, orc_mapa, profits_losts,users
gcp, cbl, grf_gcp, grf_cbl, crit, txt, orc_mapa, profits_losts,users = getData()
grupo_de_contas = data.grupo_de_contas.values()
cod_grp_contas = data.grupo_de_contas.keys()

col_esq, col_mei, col_dta = st.columns(3)

# -------------------------------------------------------------------------------
with col_esq:
    st.header(f"Análise de Gestao do exercício de  {crit['AnoAct']}")
    user = st.text_input('insira o seu codigo de acesso',type='password',)

# -------------------------------------------------------------------------------
with col_mei:
    if user in users.keys():
        st.markdown(f'#### Utilizador:')
        st.markdown(users[user])
# -------------------------------------------------------------------------------
with col_dta:
    img = Image.open("logo.png")
    st.image(img, width=200)  # , caption='O nosso orgulho')
    st.subheader(f"Período : {crit['Periodo']}")
    st.text(f"Data/Hora: {datetime.datetime.now()}")
# -------------------------------------------------------------------------------
def texto_report(mapa, x=0):
    posicao = ["TextoAntes", "TextoDepois"]
    result = txt[(txt["Mapa"] == mapa) & (txt[posicao[x]] != "")][posicao[x]]
    texto = result.tolist()
    return st.write(texto)


# -------------------------------------------------------------------------------
def titulo_quadro(df):
    titulo = "".join(df["Descriçao"][1:2].tolist())
    return st.info(titulo)
# -------------------------------------------------------------------------------
tipo_mapa_cbl = cbl["Tipo"].unique().tolist()
if user in users.keys():
    st.markdown("---")
    st.markdown("## SUMÁRIO:")
    # -------------------------------------------------------------------------------


    if st.checkbox("Nota Prévia"):
        st.markdown("## Nota Prévia")
        opcao = "txt_nota"
        if st.checkbox("Redação"):
            texto_report(opcao, 0)
            texto_report(opcao, 1)
        st.markdown("---")
    
    # -------------------------------------------------------------------------------
    st.markdown("---")

#st.dataframe(grf_gcp)
# Hide Streamlit Style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden}
            footer {visibility: hidden}
            header {visibility: hidden}
            </style>
"""
#st.markdown(hide_st_style, unsafe_allow_html=True)

# if __name__ == '__main__':
# main()
