import streamlit as st
import pandas as pd 
from io import BytesIO


# data
from datetime import date
# banco de dados
import awswrangler as awr

def main():
    def execute_elt(nome_arquivo):

        try:
            df_sheets = pd.read_excel(uploaded_file)
            df_sheets = df_sheets[['Veículo','Data Evento','Endereço']]
            df_sheets.rename(columns={'Veículo':'placa','Endereço':'endereco','Data Evento':'data_evento'},inplace=True)
            df_sheets.drop_duplicates(['placa'])
            query_reboque = open(r'sql/extract_data_trailer.sql')
            query_reboque = query_reboque.read()
            df_reboque = awr.athena.read_sql_query(query_reboque,database='silver')
            st.write('Carregado dados...')
            query_veiculo = open(r'sql/extract_data_vehicle.sql')
            query_veiculo = query_veiculo.read()
            df_veiculo = awr.athena.read_sql_query(query_veiculo, database='silver')
            df_final_vei = pd.merge(df_sheets,df_veiculo, on=['placa'],how='left')
            df_final_reboque = pd.merge(df_sheets,df_reboque, on='placa', how='left')
            df_final = pd.concat([df_final_vei,df_final_reboque]).reset_index(drop=True)
            df_final['unidade'] = df_final['unidade'].fillna('N/D')
            df_final['email_2'] = df_final['email_2'].fillna('N/D')
            df_final['cooperado'] = df_final['cooperado'].fillna('N/D')
            df_final = df_final[['placa','data_evento','endereco','cooperado','email_2','unidade']]
            df_final = df_final.drop_duplicates()
            placas_com_valor = df_final.loc[(df_final['cooperado'] != 'N/D')]['placa'].unique()
            df_final = df_final[~((df_final['cooperado'] == 'N/D') & (df_final['placa'].isin(placas_com_valor)))]
            cooperado = df_final.groupby(['cooperado'])['placa'].count().reset_index()
            cooperado.rename(columns={'placa':'qtd_repeticao'},inplace=True)
            df_final_1 = pd.merge(df_final,cooperado)
            if len(nome_arquivo) < 1:
                nome_arquivo = 'planilha'
            else:
                pass
            file_path = f'{nome_arquivo}.xlsx'
            contador = 1
            st.write(f'A quantidade de registros do arquivo carregado: {len(df_sheets)}')
            st.write(f'A quantidade de registros do arquivo tratado: {len(df_final_1)}')
            st.write('Concluído.')
            return file_path, df_final_1, contador
            

        except Exception as e:
            st.write(f'Arquivo incorreto selecionado, tente novamente.')
            st.write('Se o erro persistir, entre em contato com a equipe de dados.')
        
            return None

    st.sidebar.title('Menu Relatórios')
    paginaSelecionada = st.sidebar.selectbox('Selecione a página', ['Conferência de Placas','Placas Ativas com Rastreador', 'FIPE veículos'])

    if paginaSelecionada == 'Conferência de Placas':
        st.title("Relatório Conferência de Placas")
        contador = 0
        with st.form(key="relatorio"):
            st.text("""
            É importante ressaltar que caso planilha não esteja no padrão 
            '[Veículo, Data Evento, Endereço]'. A planilha não será formatada corretamente 
            e o programa terá erro.""")
            uploaded_file = st.file_uploader("Upload do arquivo com os dados da planilha",
            type=["csv","xlsx","xls"])
            nome_arquivo = st.text_input("Escreva o nome do arquivo que deseja:")
            input_button_submit = st.form_submit_button('Enviar')

        if input_button_submit:
            file_path, df_final_1, contador = execute_elt(nome_arquivo)

        if contador == 1:
            st.write('Realizar Download:')
            output = BytesIO()
            df_final_1.to_excel(output, index=False)
            excel_data = output.getvalue()
            output.close()

            btn = st.download_button(
                label='Download',
                data=excel_data,
                file_name=file_path,
                mime="application/vnd.ms-excel")
            
    if paginaSelecionada == 'Placas Ativas com Rastreador':
        st.title("Relatório Placas Ativas com Rastreador")
        query_placas = open(r'sql/placas_ativas_com_rastreador.sql')
        query_placas = query_placas.read()
        st.write('Carregando tabela...')
        df_placas = awr.athena.read_sql_query(query_placas, database='silver')
        hoje = date.today()
        st.write('Tabela carregada.')

        st.write('Realizar Download:')
        output = BytesIO()
        df_placas.to_excel(output, index=False)
        excel_data = output.getvalue()
        output.close()

        btn = st.download_button(
            label='Download',
            data=excel_data,
            file_name=f'placas_ativas_rastreador_{hoje}.xlsx',
            mime="application/vnd.ms-excel")
        
    if paginaSelecionada == 'FIPE veículos':
        st.title('Relatório da Tabela FIPE Veículos')

        hoje = date.today()

        query_lm = open(r'sql/listagem_mestra.sql')
        query_lm = query_lm.read()
        listagem_mestra = awr.athena.read_sql_query(query_lm, database='gold')

        placas_lm = list(listagem_mestra['placa'])

        query_it = open(r'sql/insurance_trailer.sql')
        query_it = query_it.read()
        insurance_trailer = awr.athena.read_sql_query(query_it, database='silver')

        insurance_trailer = insurance_trailer.rename(columns = {'board':'placa', 'chassi':'chassi_trailer'})

        insurance_trailer = insurance_trailer[insurance_trailer['placa'].isin(placas_lm)]

        query_iv = open(r'sql/insurance_vehicle.sql')
        query_iv = query_iv.read()
        insurance_vehicle = awr.athena.read_sql_query(query_iv, database='silver')

        insurance_vehicle = insurance_vehicle.rename(columns={'board': 'placa', 'chassi': 'chassi_veiculo'})

        insurance_vehicle = insurance_vehicle[insurance_vehicle['placa'].isin(placas_lm)]

        df_fipe = listagem_mestra.merge(insurance_trailer, on='placa', how='left')

        df_merged = df_fipe.merge(insurance_vehicle[['placa', 'chassi_veiculo']], on='placa', how='left')

        df_merged['chassi'] = df_merged['chassi_veiculo'].fillna(df_merged['chassi_trailer'])
        df_merged = df_merged.drop(columns = ['chassi_trailer','chassi_veiculo'])

        st.write('Carregando tabela...')
        st.write('Tabela carregada.')

        st.write('Realizar Download:')
        output = BytesIO()
        df_merged.to_excel(output, index=False)
        excel_data = output.getvalue()
        output.close()

        btn = st.download_button(
            label='Download',
            data=excel_data,
            file_name=f'placas_fipe_{hoje}.xlsx',
            mime="application/vnd.ms-excel")
        

    return

