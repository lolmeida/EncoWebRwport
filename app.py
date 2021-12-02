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


def get_users_dict():
    '''Get users as a Dictionary'''
    users = pd.read_csv('users.txt')
    users_dict = {}
    for i in range(users.shape[0]):
        users_dict [str(users.iloc[i,0])] = users.iloc[i,1]
    return users_dict

def _criar_conecao_primavera():
    '''Create connection to Primavera Database'''
    server = r"ENCO-SRV02/PRIMAVERAV9"
    database = "PRIENCO"
    username = "SA"
    password = "Enco#2016"
    driver = "SQL Server"
    # =================================================================================
    string_connexao = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return string_connexao


_string_connexao = _criar_conecao_primavera()

_my_file = "dadosRelatorioGestao.xlsm"


def _parteDecimal(numero):
    t = str(numero).replace(",", ".")
    decimal = t.find(".")
    if decimal == -1:
        return ".00"
    else:
        decimal = t[decimal:]
        larg = len(decimal)

        if larg >= 3:
            return decimal[0:3]
        elif larg == 2:
            return decimal + "0"
        elif larg == 1:
            return decimal + "00"
        else:
            return ".00"


# =================================================================================
def _parteInteira(numero):
    t = str(numero).replace(",", ".")
    decimal = t.find(".")
    x = len(t) if decimal == -1 else decimal
    #v = t[0:x]
    res = ""
    pos = 0
    for i in range(x, 0, -1):
        if pos % 3 == 0:
            res = "." + res
        res = t[i - 1] + res
        pos = pos + 1
    return res.replace("-.", "-")


# =================================================================================
def formatarNumeros(numero):
    num = str(_parteInteira(numero)) + str(_parteDecimal(numero))
    res = num.replace("..", ",")
    return None if numero in ("", "0") else res


# =================================================================================
def formatarNumerosInt(numero):
    res = str(_parteInteira(numero))
    return None if numero in ("", "0") else res[:-1]


# =================================================================================
def formatarNumerosPerc(valor):
    numero = valor * 100
    num = str(_parteInteira(numero)) + str(_parteDecimal(numero))
    res = num.replace("..", ",")
    return None if numero in ("", "0") else res + "%"


# =================================================================================
def get_orc_mapa():
    df = (
        pd.read_excel(_my_file, sheet_name="pyConfig", index_col=None, usecols="A:F")
        .fillna("")
        .reset_index(drop=True)
    )
    orc_mapa = df[df["Orcamento"] == True].reset_index(drop=True)["Mapa"].tolist()
    return orc_mapa


def getCriterios():
    xls = {}
    with pd.ExcelFile(_my_file) as f:
        xls["pyConfig"] = pd.read_excel(f, "pyConfig", index_col=None)
        data = xls["pyConfig"]
        crit = data[["Nome", "Valor"]].dropna().reset_index(drop=True)
        criterios = {}
        for i in range(crit.shape[0]):
            criterios[crit.loc[i][0]] = crit.loc[i][1]
    return criterios

_criterios = getCriterios()
msf = _criterios["MesFim"]
ano = _criterios["AnoAct"]
AnoAct = _criterios["AnoAct"]
AnoAnt = _criterios["AnoAnt"]
cambioAnt = _criterios["CambioAnt"]
cambioAct = _criterios["CambioAct"]
_PerAbrev = _criterios["PerAbrev"]
_tipo_prod = {
    "30126": ["Jet-A1", "Combustíveis"],
    "30170": ["Outros acessórios", "Outros"],
    "30110": ["Gás butano", "Outros"],
    "30137": ["Petróleo", "Combustíveis"],
    "30133": ["Gasolina", "Combustíveis"],
    "30144": ["Gasóleo", "Combustíveis"],
    "30150": ["Lubrificantes", "Outros"],
}

def _getFindReplace():
    dados = {}
    cbl_rep_val = pd.read_excel(
        _my_file, sheet_name="pyData", usecols="V,C:P", header=0, converters=fmt_cbl
    )
    gcp_rep_val = pd.read_excel(
        _my_file,
        sheet_name="pyMercadorias",
        usecols="M, C:K",
        header=0,
        converters=fmt_gcp,
    )
    cbl_rep_val = cbl_rep_val[cbl_rep_val["Marks"].str.len() > 0].reset_index(drop=True)
    gcp_rep_val = gcp_rep_val[gcp_rep_val["Marks"].str.len() > 0].reset_index(drop=True)

    dar = [cbl_rep_val, gcp_rep_val]
    for y in range(2):
        da = dar[y]
        cols = da.columns
        nu_lins, nu_cols = da.shape
        # ------------------------------------------------------------------
        for x in range(nu_lins):
            for i in range(nu_cols - 1):
                codigo = f"{da.loc[x][nu_cols-1]}_{cols[i]}".upper()
                valor = da.loc[x][i]
                dados[codigo] = valor
    # -----------------------------------------------------------------
    # find_replace = dfc[["Find", "Replace"]]
    # da = find_replace[find_replace["Find"].str.len() > 0].reset_index(drop=True)
    # cols = da.columns
    # nu_lins, nu_cols = da.shape
    # for i in range(nu_lins - 1):
    #    codigo = da.loc[i][0]
    #    valor = da.loc[i][1]
    #    dados[codigo] = valor
    # -------------------------------------------------------------
    for z in _criterios.keys():
        dados[z.upper()] = _criterios[z]
    return dados

def get_ProfitsAndLosts():
    return pd.read_excel(_my_file, sheet_name="pyCustosPreveitos", skiprows=1, )

# --------------------------------------------------------------------------------
grupo_de_contas = {
    #'1':'Capitais Permanentes',
    '2':'Valores Imobilizados',
    '3': 'Mercadorias',
    #'4': 'Terciros',
    '5':'Disponibilidades',
    '6': 'Custos e Perdas',
    '7': 'Proveitos e Ganhos'
}

def getTxt():
    find_replace = _getFindReplace()
    dft = pd.read_excel(_my_file, sheet_name="pyReportText").fillna("")
    texto_antes = dft["TextoAntes"]
    texto_depois = dft["TextoDepois"]
    lins= dft.shape[0]
    for n in range(lins):
        texto_antes = dft["TextoAntes"][n]
        texto_depois = dft["TextoDepois"][n]
        for i in find_replace.keys():
            texto_antes = texto_antes.replace(i, str(find_replace[i]))
            texto_depois = texto_depois.replace(i, str(find_replace[i]))
        dft["TextoAntes"][n] = texto_antes.strip()
        dft["TextoDepois"][n] = texto_depois.strip()
    return dft

# ----------------------------------------------------------------------------
fmt_gcp = {
    "AnoAntStd": formatarNumeros,
    "AnoActStd": formatarNumeros,
    "AnoAntUsd": formatarNumeros,
    "AnoActUsd": formatarNumeros,
    "QtdAnt": formatarNumerosInt,
    "QtdAct": formatarNumerosInt,
    "VarStd": formatarNumerosPerc,
    "VarUsd": formatarNumerosPerc,
    "VarQtd": formatarNumerosPerc,
}

fmt_cbl = {
    "AnoAntStd": formatarNumeros,
    "AnoActStd": formatarNumeros,
    "OrcStd": formatarNumeros,
    "AnoAntUsd": formatarNumeros,
    "AnoActUsd": formatarNumeros,
    "OrcUsd": formatarNumeros,
    "VarStd": formatarNumerosPerc,
    "VarOrcStd": formatarNumerosPerc,
    "PerStd": formatarNumerosPerc,
    "ExtStd": formatarNumerosPerc,
    "VarUsd": formatarNumerosPerc,
    "VarOrcUsd": formatarNumerosPerc,
    "PerUsd": formatarNumerosPerc,
    "ExtUsd": formatarNumerosPerc,
}

def get_xls_data(id_src=0, formated=True):
    """
    {0:'cbl', 1:'gcp'}
    """
    sheet_name = ["pyData", "pyMercadorias"]
    usecols = ["A:P, T:V, Y:AB", "B:P"]
    converters = [fmt_cbl, fmt_gcp] if formated else [{"a": ""}, {"a": ""}]
    sort_values = [["PrintOrder", "NewSort"], ["PrintOrder"]]

    

    
    df = pd.read_excel(
        _my_file,
        sheet_name=sheet_name[id_src],
        usecols=usecols[id_src],
        header=0,
        converters=converters[id_src],
    ).sort_values(sort_values[id_src], ignore_index=True)
    df["Descriçao"] = df["Descriçao"].str.capitalize()
    df = df [df["Ocultar"] == False].fillna('')
    marks =  [df[(df["Marks"] == "") &  (df["AnoActStd"] != "")
            & (df["AnoActStd"] != 0)
            & (df["Descriçao"] != "Total")], df[(df["Marks"] != "") ]]
    if formated == True:
        return df
    else:
        df = marks[id_src]
        return df
def getData():
    gcp = (
        get_xls_data(id_src=1, formated=True).dropna().reset_index(drop=True)
    )  
    cbl = (
        get_xls_data(id_src=0, formated=True).dropna().reset_index(drop=True)
    )  

    grf_gcp = (
        get_xls_data(id_src=1, formated=False).dropna().reset_index(drop=True)
    )

    grf_cbl = (
        get_xls_data(id_src=0, formated=False).dropna().reset_index(drop=True)
    )
    crit = getCriterios()
    txt = getTxt()
    orc_mapa = get_orc_mapa()
    #rhp = get_Rhp()
    profits_losts = get_ProfitsAndLosts() 
    users = get_users_dict()
    
    return gcp, cbl, grf_gcp, grf_cbl, crit, txt, orc_mapa, profits_losts,users
gcp, cbl, grf_gcp, grf_cbl, crit, txt, orc_mapa, profits_losts,users = getData()
grupo_de_contas = grupo_de_contas.values()
cod_grp_contas = grupo_de_contas.keys()

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
