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
@st.cache
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
    if st.checkbox("1. Atividades"):
        st.markdown("## Aprovisionamento e comercialização")
        col1, col2, col3, col4 = st.columns(4)
        opcao = col1.selectbox(
            "Escolha uma opção vara visualizar", ("Importacao", "Vendas", "Existencias")
        )
        moeda = col2.selectbox("Selecione a moeda", ("Usd", "Std"))
        tipo_dados = col3.selectbox(
            "Escolha o tipo de visualização", ("Gráficos","Tabela")
        )
        #texto_report(opcao, 0)
        if tipo_dados == "Tabela":
            df_cols = [
                "Descriçao",
                "QtdAnt",
                "QtdAct",
                "VarQtd",
                f"AnoAnt{moeda}",
                f"AnoAct{moeda}",
                f"Var{moeda}",
            ]
            st.markdown(f"##### {tipo_dados} de {opcao} em {moeda.upper()}".upper())
            df = gcp[gcp["Mapa"] == opcao].reset_index(drop=True)
            titulo_quadro(df)
            st.table(df[df_cols].iloc[2:])
        elif tipo_dados == "Gráficos":
            familia = col4.selectbox("Escolha uma familia ", ("Combustíveis", "Outros"))
            st.markdown(
                f"##### {tipo_dados} de {opcao} de {familia} em {moeda.upper()}".upper()
            )
            df_grf = grf_gcp[(grf_gcp["Mapa"] == opcao) & (grf_gcp["Familia"] == familia)]
            gcp_qtd_val = [['Descriçao','QtdAnt','QtdAct'],['Descriçao',f'AnoAnt{moeda}',f'AnoAct{moeda}']]
            gcp_ttlo_mda = ['.',f'em {moeda.upper()}.']
            ttlo_qtd_val = ['Quantidades de','Valor de ']
            def grafico_gcp(id_tipo):
                gcp_df =df_grf[gcp_qtd_val[id_tipo]]
                gcp_df = gcp_df.rename(columns={'AnoAntStd':data.AnoAnt, 'AnoActStd':data.AnoAct,'QtdAnt':data.AnoAnt, 'QtdAct':data.AnoAct})
                gcp_df =gcp_df.T
                gcp_df.columns = gcp_df.iloc[0]
                gcp_df = gcp_df[1:].reset_index()
                y=gcp_df.columns[1:]
                
                for i in y:
                    gcp_df[i] = pd.to_numeric(gcp_df[i])
                fig = px.bar(gcp_df, x="index", y=y, title=f"{ttlo_qtd_val[id_tipo]} {opcao} de {familia} {gcp_ttlo_mda[id_tipo]}", barmode='group')
                fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                return fig
            col1, col2 = st.columns(2)
            col1.plotly_chart(grafico_gcp(0), use_container_width=True)
            col2.plotly_chart(grafico_gcp(1), use_container_width=True)
            
            
            
            
            # -----------------------------------------------------------------------------
            
            
            if st.checkbox("Dataframe"):
                st.dataframe(df_grf)
            # -----------------------------------------------------------------------------
        else:
            st.warning("Em construção")
        if st.checkbox("Texto"):
            texto_report(opcao, 0)
            texto_report(opcao, 1)
        st.markdown("---")
    mapas_financ = ["Indicadores", "Balanço", "D_Resultados", "FluxoCaixa"]
    # -------------------------------------------------------------------------------
    if st.checkbox("2. Demonstrações financeiras"):
        st.markdown("## Demonstrações financeiras")
        col1, col2, col3, col4 = st.columns(4)
        opcao = col1.selectbox("Mapa:", mapas_financ)
        moeda = col2.selectbox("Moeda:", ("Std", "Usd"))
        df_cols = [
            "Descriçao",
            "Notas",
            f"AnoAnt{moeda}",
            f"Var{moeda}",
            f"AnoAct{moeda}",
            f"VarOrc{moeda}",
            f"Orc{moeda}",
        ]
        df_columns = df_cols if opcao in orc_mapa else df_cols[0:-2]
        df = cbl.fillna("")
        df = df[df["Mapa"] == opcao].reset_index(drop=True)
        col3.markdown(f"#### {opcao} em {moeda.upper()}")
        
        
        titulo_quadro(df)
        st.table(df[df_columns].iloc[2:])

        if st.checkbox("Descrição"):
            texto_report(opcao, 0)
            texto_report(opcao, 1)
        st.markdown("---")
    # -------------------------------------------------------------------------------
    if st.checkbox("3. Análise das Demonstrações Financeiras"):
        st.markdown("## Análise das Demonstrações Financeiras")
        col1, col2, col3, col4 = st.columns(4)
        tipo_mapa = col1.selectbox("Tipo:", tipo_mapa_cbl[1:])
        cbl = cbl[cbl["Tipo"] == tipo_mapa]
        cbl_mapas = cbl["Mapa"].unique().tolist()
        mapas_aux = [x for x in cbl_mapas if x not in mapas_financ]
        mapa = col2.selectbox("Mapa:", mapas_aux)
        moeda = col3.selectbox("Moedas:", ("Usd", "Std"))
        tipo_dados = col4.selectbox("Mostrar:", ("Gráfico","Tabela"))
        #st.markdown(f"#### {mapa} em {moeda.upper()}")
        
        if tipo_dados == "Tabela":
            df_cols = [
                "Descriçao",
                "Notas",
                f"AnoAnt{moeda}",
                f"Var{moeda}",
                f"AnoAct{moeda}",
                f"VarOrc{moeda}",
                f"Orc{moeda}",
            ]
            df_columns = df_cols if mapa in orc_mapa else df_cols[0:-2]
            df = cbl.fillna("")
            df = df[df["Mapa"] == mapa].reset_index(drop=True)[df_columns]
            titulo_quadro(df)
            st.table(df.iloc[2:])
        elif tipo_dados == "Gráfico":
            grf_gcp = data.get_xls_data(id_src=0, formated=False).dropna().reset_index(drop=True)
            df_grf = grf_gcp[(grf_gcp["Mapa"] == mapa)]
            gcp_qtd_val = ['Descriçao',f'AnoAnt{moeda}',f'AnoAct{moeda}',f'Orc{moeda}']
            gcp_ttlo_mda = f'em {moeda.upper()}.'

            def grafico_gcp():
                gcp_df =df_grf[gcp_qtd_val]
                gcp_df = gcp_df.rename(columns={f'AnoAnt{moeda}':str(data.AnoAnt), f'AnoAct{moeda}':str(data.AnoAct), f'Orc{moeda}':f'Orçamento {data.AnoAct}'})
                gcp_df =gcp_df.T
                gcp_df.columns = gcp_df.iloc[0]
                gcp_df = gcp_df[1:].reset_index()
                y=gcp_df.columns[1:]

                for i in y:
                    gcp_df[i] = pd.to_numeric(gcp_df[i])
                fig = px.bar(gcp_df, x="index", y=y, title=f"{mapa}  {gcp_ttlo_mda}", barmode='group')
                fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                return fig
            st.plotly_chart(grafico_gcp(), use_container_width=True)
            
            
        else:
            st.warning("Em construção")
        if st.checkbox("Redação"):
            texto_report(mapa, 0)
            texto_report(mapa, 1)
        st.markdown("---")

    df_cp = profits_losts
    df_cp = df_cp[df_cp['Ocultar'] == False]
    lst_ctas_sel = df_cp.Cta.unique().tolist()
    if st.checkbox("4. Análise das Contas"):
        x1, x2, x3, x4,x5,x6 = st.columns(6)
        rubricas = x1.selectbox('Rubricas:',grupo_de_contas)
        id_cust_prov = ''.join([x for x,y in data.grupo_de_contas.items() if y == rubricas])
        grupo_conta = [x for x in lst_ctas_sel if str(x).startswith(id_cust_prov)]
        grp_contas = x2.selectbox('Grupo de Contas:',grupo_conta) #lst_ctas_sel )
        lst_contas_sel = df_cp[df_cp['Cta'] == grp_contas].Conta.unique().tolist() 
        contas = x3.selectbox('Contas de Movimento:',lst_contas_sel )

        a, b, c = st.columns(3)
        mes= crit['MesFim']
        res = df_cp[df_cp['Conta'] == contas ].reset_index(drop=True)
        tipos = res.Tipo.tolist()
        resx = res.transpose()
        pasta = f'pyGraphics/{resx[3:-1].iloc[0].tolist()[0]}'
        titulo = f'{resx[0:1].iloc[0].tolist()[0]} - {resx[1:2].iloc[0].tolist()[0]}'
        columns = resx[2:3].iloc[0].tolist()
        result = resx[4:-1]
        st.info(titulo)
        chart = Line(titulo)
        chart.set_options(labels=result.index.tolist()[:mes], x_label='Mês', y_label='STD')
        meses = [int(x) for x in result.index.tolist()[:mes]]
        xyz = [go.Line(name=tipos[x], x=meses, y=result[x]) for x in range(len(tipos))]
        fig = go.Figure(data=xyz)
        fig.update_layout(barmode='group')
        a.plotly_chart(fig, use_container_width=True)
        
        grp_res = res[['Tipo','Descricao','Total']]
        fig_res_cta = px.bar(
        grp_res,
        x="Tipo",
        y= "Total",
        text="Total",
        orientation="v",
        barmode='group',
        title=f"<b>{grp_res['Descricao'][0]} (Total Acumulado)</b>",
        color='Tipo',
        color_continuous_scale=["red", "yellow", "green"],
        template="plotly_white")
        fig_res_cta.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_res_cta.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        b.plotly_chart(fig_res_cta, use_container_width=True)



        raz = str(contas)[:2]
        res_raz =df_cp[df_cp['Cta'] == int(raz) ].iloc[:-1,2:].groupby(by=['Tipo'], as_index=False).sum()#.reset_index(drop=True)
    
        
        fig_raz_cta = px.bar(
        res_raz,
        x="Tipo",
        y= "Total",
        text="Total",
        orientation="v",
        barmode='group',
        title=f"<b>Total {rubricas}.</b>",
        color='Tipo',
        color_continuous_scale=["red", "yellow", "green"],
        template="plotly_white")
        fig_raz_cta.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_raz_cta.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        c.plotly_chart(fig_raz_cta, use_container_width=True)

        st.markdown("---") 
        if st.checkbox("Dataframe"):
            st.dataframe(res)
            st.dataframe(res_raz)


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
st.markdown(hide_st_style, unsafe_allow_html=True)

# if __name__ == '__main__':
# main()
