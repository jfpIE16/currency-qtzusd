import scrapy
import re
import json
from scrapy_splash import SplashRequest

class CurrencySpider(scrapy.Spider):
    name = 'currencies'
    float_filter = r"[-+]?\d*\.\d+|\d+"

    def start_requests(self):
        start_urls = [
        'https://www.banrural.com.gt/',
        'https://www.corporacionbi.com/gt/',
        'https://www.bam.com.gt/',
        'https://www.banguat.gob.gt/cambio/',
        'https://www.chn.com.gt/',
        'https://www.ficohsa.com/gt/guatemala/tipo-cambio/',
        'https://www.bancoazteca.com.gt/BancoAztecaGua/',
        'https://www.interbanco.com.gt/wsIntegra/js/TipoCambio.js?_=1627797271430',
        'https://bpi.gytcontinental.com.gt/Transaction/ConsultaTasa.asp?refresh=1628477241806'
        ]
        for url in start_urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):

        page_title = str(response.css('title::text').get()).strip()

        if page_title == "Inicio":
            bral_compra = response.css('span#dnn_ctr617_br_tipodecambio_lblUSDCompra::text').extract_first()
            bral_venta = response.css('span#dnn_ctr617_br_tipodecambio_lblUSDVenta::text').extract_first()

            banrural_dict = {
                'Banco': 'Banrural',
                'Compra': re.findall(self.float_filter, bral_compra)[0],
                'Venta': re.findall(self.float_filter, bral_venta)[0]
            }
            yield banrural_dict

        elif page_title == "Bienvenido - Banco Industrial - Guatemala":
            bi_compra = response.css('span#agencia_purchase::text').extract_first()
            bi_venta = response.css('span#agencia_sell::text').extract_first()
            bi_dict = {
                'Banco': 'Banco Industrial',
                'Compra': re.findall(self.float_filter, str(bi_compra))[0],
                'Venta': re.findall(self.float_filter, str(bi_venta))[0]
            }
            yield bi_dict

        elif page_title == "Banco Agromercantil de Guatemala, S.A. - BAM":
            bam_compra = response.css('span.o-section-exchage-rate-item-precios_valor-compra::text')[1].get()
            bam_venta = response.css('span.o-section-exchage-rate-item-precios_valor::text')[1].get()
            bam_dict = {
                'Banco': 'Banco Agromercantil',
                'Compra': re.findall(self.float_filter, str(bam_compra))[0],
                'Venta': re.findall(self.float_filter, str(bam_venta))[0]
            }
            yield bam_dict

        elif page_title == "Tipo de Cambio - Banco de Guatemala":
            referencia = response.css('b::text').get().strip()
            yield {'Banco': 'Banguat',
                   'Compra': referencia,
                   'Venta': referencia}

        elif page_title == "Banco CHN | Guatemala":
            tasa = response.css('div.tasa')
            tasas = tasa.css('h5::text').get().strip()
            chn_dict = {
                'Banco': 'Credito Hipotecario Nacional',
                'Compra': re.findall(self.float_filter, tasas)[0],
                'Venta': re.findall(self.float_filter, tasas)[1]
            }
            yield chn_dict
            
        elif page_title == "Tipo de Cambio | Ficohsa":
            fic_compra = response.xpath('/html[1]/body[1]/div[2]/div[1]/article[1]/h3[2]/span[1]/text()').get().strip()
            fic_venta = response.xpath('/html[1]/body[1]/div[2]/div[1]/article[1]/h3[2]/span[2]/text()').get().strip()
            fic_dict = {
                'Banco': 'Banco Ficohsa',
                'Compra': re.findall(self.float_filter, fic_compra)[0],
                'Venta': re.findall(self.float_filter, fic_venta)[0]
            }
            yield fic_dict

        elif page_title == "Sitio Oficial | Banco Azteca Guatemala":
            azt_compra = response.xpath('/html[1]/body[1]/div[5]/div[1]/div[1]/p[1]/text()').get().strip()
            azt_venta = response.xpath('/html[1]/body[1]/div[5]/div[1]/div[1]/p[2]/text()').get().strip()
            azt_dict = {
                'Banco': 'Banco Azteca',
                'Compra': re.findall(self.float_filter, azt_compra)[0],
                'Venta': re.findall(self.float_filter, azt_venta)[0]
            }
            yield azt_dict
        else:
            ic_reformatted = response.css('pre::text').get()
            if not ic_reformatted == None:
                ic_json = json.loads(str(ic_reformatted).strip())
                ic_dict = {
                    'Banco': 'InterBanco',
                    'Compra': re.findall(self.float_filter, ic_json["CompraGeneral"])[0],
                    'Venta': re.findall(self.float_filter, ic_json["VentaGeneral"])[0]
                }
                yield ic_dict
            else:
                gtc_compra = str(response.css('p::text')[2].get()).strip()
                gtc_venta = str(response.css('p::text')[1].get()).strip()
                gtc_dict = {
                    'Banco': 'G&T Continental',
                    'Compra': re.findall(self.float_filter, gtc_compra)[0],
                    'Venta': re.findall(self.float_filter, gtc_venta)[0]
                }
                yield gtc_dict
