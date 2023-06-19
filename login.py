import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from pathlib import Path
from main import main
import streamlit_authenticator as stauth
from PIL import Image

#asda

st.set_page_config(page_title="Relatório Placas",
                   page_icon="tk_logo_1.png", layout = 'centered')

# Load the image
image = Image.open("tk_logo_1.png")
# Define CSS styles
st.markdown(
    """
    <style>
    .center-top-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
        background-color: #f2f2f2;
    }
    .center-image {
        max-width: 100%;
        max-height: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the image in the top left corner
st.image(image, caption="", use_column_width=False, output_format="auto", width=150,
          clamp=False, channels="RGB")


headerSection = st.container()
mainSection = st.container()
loginSection = st.container()

df_usuarios = pd.DataFrame({
    'username': ['tkmonitoramento', 'analisededados'],
    'password': ['tkrelatorio', 'dadosrelatorio']})

def login_usuario(username, password):
    if username in df_usuarios['username'].values:
        index = df_usuarios[df_usuarios['username'] == username].index[0]
        if password == df_usuarios.loc[index, 'password']:
            return True
    return False

def click_login(usuario,senha):
    if login_usuario(usuario, senha):
        st.session_state['logado'] = True
    else:
        st.session_state['logado'] = False
        st.error("Usuário/Senha incorretos.")

placeholder = st.empty()

def pagina_login():
    with loginSection:
        if st.session_state['logado'] == False:
            st.title("Relatórios de Placas")
            usuario = st.text_input('Usuário')
            senha = st.text_input('Senha',type='password')
            st.button('Login', on_click=click_login, args=(usuario, senha))
    return usuario

with headerSection:
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        pagina_login()
    else:
        if st.session_state['logado']:
            main()
        else:
            pagina_login()
 

    
    
