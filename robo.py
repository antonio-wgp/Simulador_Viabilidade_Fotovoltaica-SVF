from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

valores = [num for num in range(100,1000)]
alternativas = [num for num in ['a','b','c','d','e']]

perguntas = []
ids = ["potencia_modulo", "Cidade", "rede", "cosip", "Concessionaria", "ano_instalação", "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "sep", "out", "nov", "dez", "media_kwh", "Enviar"]
alternativa = ""
botao = ""
driver = webdriver.Chrome()
driver.get("http://127.0.0.1:5000/")
time.sleep(2)


def coletar_botoes():
    global perguntas, alternativa, botao
    for i in range(len(ids) - 1):
        perguntas.append(driver.find_element("id", ids[i]))
        if ids[i] == "Cidade":
            perguntas[i].send_keys("Criciúma")
        elif ids[i] == "rede":
            perguntas[i].send_keys("Trifásico")
        elif ids[i] == "Concessionaria":
            perguntas[i].send_keys("Celes")
        elif ids[i] == "ano_instalação":
            perguntas[i].send_keys("2023")
        elif ids[i] == "cosip":
            perguntas[i].send_keys("5")
        else:
            perguntas[i].send_keys(random.choice(valores))
        time.sleep(0.1)
    botao = driver.find_element("xpath", "//input[@type='submit' and @value='Enviar']")
    botao.click()
    time.sleep(10)
coletar_botoes()