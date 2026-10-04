import os

# Importado antes de qualquer teste: chave de sessão própria dos testes.
os.environ.setdefault("ASSURA_CHAVE_DA_SESSAO", "chave-de-sessao-dos-testes-com-32-bytes-ou-mais")
