# Arquitetura

A CLI é uma camada fina. Regras ficam em módulos puros e testáveis. Escrita, remoção e subprocessos passam por fronteiras explícitas. Não existe execução por shell. Evidência é separada do payload e verificada por SHA-256.
