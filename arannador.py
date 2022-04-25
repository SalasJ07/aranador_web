from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import requests

HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

def obtener_recursos():
    URL = "https://www.amazon.es/gp/bestsellers/books/"
    origen = requests.get(URL, headers=HEADERS)
    menu = BeautifulSoup(origen.content, "lxml")
    links_recursos = []
    elementos = menu.find_all('div', class_='_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf')
    
    for elemento in elementos:
            for link in elemento.find_all('a', href=True):
                links_recursos.append('amazon.es'+link['href'])
    
    return links_recursos

def obtener_enlaces(contenedor):
    lista_enlaces = []
    
    for elemento in contenedor:
        enlaces = elemento.find_elements(by=By.XPATH, value='.//a[@class="a-link-normal"]')
        for enlace in enlaces:
            if enlace.get_attribute('tabindex') == "-1":
                lista_enlaces.append(enlace.get_attribute('href'))

    return lista_enlaces

def procesar_enlaces(controlador):
    
    contenedor = WebDriverWait(controlador, 5).until(EC.presence_of_all_elements_located((By.XPATH, 
                        '//div[contains(@class, "p13n-gridRow _cDEzb_grid-row_3Cywl")]')))
    enlaces = obtener_enlaces(contenedor)
    
    return enlaces
    
    
def procesar_libros(enlaces):
    #for i in range(len(enlaces)):
    libro = requests.get(enlaces[4], headers=HEADERS)
    pagina_libro = BeautifulSoup(libro.content, 'lxml')
    
    info_no_filtrada = pagina_libro.find('div', id='bookDescription_feature_div')
    
    descripcion_libro = ""
    for parrafo in info_no_filtrada.find_all('span'):
        if parrafo.get('class') == None:
            descripcion_libro += parrafo.text + "\n\n"
        else:
            if not any(item in ['a-list-item', 'a-expander-prompt'] for item in parrafo.get('class')):
                descripcion_libro += parrafo.text + "\n\n"
        
    print(descripcion_libro)
    
def procesar_categorias(lista_categorias):
    
    opciones = webdriver.FirefoxOptions()
    opciones.add_argument("--headless")
    
    controlador = webdriver.Firefox(options=opciones, service=Service(GeckoDriverManager().install()))
    
    controlador.get('https://www.'+lista_categorias[0])
    
    sleep(1)
    cookies= controlador.find_element(by=By.ID, value='sp-cc-accept')
    cookies.click()
    
    for _ in range(3):
        sleep(1)
        controlador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    sleep(2)
    enlaces = procesar_enlaces(controlador)
    
    controlador.quit()
    
    procesar_libros(enlaces)

def principal():
    lista_categorias = obtener_recursos()
    procesar_categorias(lista_categorias)

if __name__ == "__main__":
    principal()
    

