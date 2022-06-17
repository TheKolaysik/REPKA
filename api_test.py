from requests import get, post, delete
import json

print(get('http://localhost:5000/api/comps/1').json())
print(delete('http://localhost:5000/api/comps/1').json())
print(post('http://localhost:5000/api/comps', json={'title': 'IRF3205',
                                                    "type": "MOSFET",
                                                    'about': 'Подходит для создания линейного блока питания',
                                                    "datasheet": "http://irf.ru/pdf/irf3205.pdf"}).json())
