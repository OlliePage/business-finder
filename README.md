

# Directory Structure 

```bash
business-finder/
│
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── .gitignore
│
├── business_finder/          
│   ├── __init__.py             
│   ├── cli.py                 
│   ├── config.py              
│   ├── api/                    
│   │   ├── __init__.py
│   │   ├── places.py          
│   │   └── geocoding.py       
│   │
│   └── exporters/             
│       ├── __init__.py
│       ├── csv_exporter.py     
│       └── json_exporter.py    
│
├── web/                        
│   ├── index.html              
│   ├── css/                   
│   │   └── style.css           
│   ├── js/                     
│   │   ├── map-widget.js       
│   │   └── integration.js      
│   └── assets/                 
│
├── examples/                  
│   ├── __init__.py
│   ├── basic_search.py        
│   ├── advanced_search.py      
│   └── sample_data/            
│
└── tests/                      
    ├── __init__.py
    ├── test_api.py            
    ├── test_exporters.py      
    └── fixtures/
```