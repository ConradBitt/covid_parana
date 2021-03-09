import streamlit as st
import datetime


def main():
    hoje = datetime.date.today()
    st.title('Covid no Estado do Paraná e região')
    st.text(f'{hoje.day}/{hoje.month}/{hoje.year}',)


if __name__ == '__main__':
    main()

