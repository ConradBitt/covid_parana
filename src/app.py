import streamlit as st
import datetime



# Baixa base de dados do Governo do Paraná
hoje = datetime.date.today()


def main():
    st.title('Covid no Estado do Paraná e região')
    st.text(f'{hoje}')



if __name__ == '__main__':
    main()

