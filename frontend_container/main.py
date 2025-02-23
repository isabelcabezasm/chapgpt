import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(passwords=["password1", "password2"]).hash_list()
print(hashed_passwords)