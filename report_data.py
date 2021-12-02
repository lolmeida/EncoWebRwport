import numpy as np
import pandas as pd
import pyodbc




def get_users_dict():
    users = pd.read_csv('users.txt')
    users_dict = {}
    for i in range(users.shape[0]):
        users_dict [str(users.iloc[i,0])] = users.iloc[i,1]
    return users_dict

def _criarConecaoPrimavera():
    SERVER = "ENCO-SRV02\PRIMAVERAV9"
    DATABASE = "PRIENCO"
    USERNAME = "SA"
    PASSWORD = "Enco#2016"
    DRIVER = "SQL Server"
    # =================================================================================
    string_connexao = "DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}".format(
        DRIVER, SERVER, DATABASE, USERNAME, PASSWORD
    )
    return string_connexao


_string_connexao = _criarConecaoPrimavera()


def _selecionar(query, headers=None):
    """
    Seleciona dados da base de dados PRIENCO
    Parámetros:
    - query - > Obrigatório
    - headers - > facultativo: Quando fornecido, retorna DataFrame
    """
    with pyodbc.connect(_string_connexao) as conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
    if headers == None:
        return data
    else:
        res = np.array(data)
        df = pd.DataFrame(res, columns=headers)
        for column in df.columns:
            df[column] = df[column].fillna(0)  # Fill NaN values with ''
        return df


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
    v = t[0:x]
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


def get_Rhp():
    # -------------------------PESSOAL---------------------------------------------------------
    rhp = f"usp_RecursosHumanos '28-{msf}-{ano}'"
    rhp_cols = [
        "codigo",
        "nome",
        "sexo",
        "idade",
        "tempo_servico",
        "anos_casa",
        "anos_idade",
        "literacia",
        "categoria",
        "qtd",
    ]
    return _selecionar(rhp, rhp_cols)


def get_Exi():
    # ----------------------------EXISTENCIAS------------------------------------------------------
    exi = "usp_Peah_ExistenciaEmFecho"
    exi_cols = ["ano", "mes", "data", "familia", "stock"]
    sexi = _selecionar(exi, exi_cols)
    sexi["artigo"] = [_tipo_prod[i][0] for i in sexi["familia"]]
    sexi["grupo"] = [_tipo_prod[i][1] for i in sexi["familia"]]
    sexi["mes"] = [int(i) for i in sexi["mes"]]
    sexi = sexi[sexi["mes"] <= msf]
    return sexi.sort_values(["grupo", "familia"])
    # ----------------------------------------------------------------------------------


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
    lins, cols = dft.shape
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

    

    int_cbl = [
        [
            "AnoAntStd",
            "VarStd",
            "AnoActStd",
            "VarOrcStd",
            "OrcStd",
            "PerStd",
            "ExtStd",
            "AnoAntUsd",
            "VarUsd",
            "AnoActUsd",
            "VarOrcUsd",
            "OrcUsd",
            "PerUsd",
            "ExtUsd",
        ],
        [
            "QtdAnt",
            "QtdAct",
            "VarQtd",
            "AnoAntStd",
            "AnoActStd",
            "VarStd",
            "AnoAntUsd",
            "AnoActUsd",
            "VarUsd",
        ],
    ]

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