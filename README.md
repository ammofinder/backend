# ammofinder backend

Backend for scraping information from stores. It's not even alpha :)

Scraped products:
- Ammunition
    - 9x19
    - 22 LR
    - 223 Rem
    - 7.62x39

Supported stores:
- DixiePomerania
- GardaArms
- Rusznikarnia
- Arel
- Tarcza

# Setup

Create database, e.g. mariadb instance:

```SQL
DESCRIBE table_name;
```

```SQL
CREATE DATABASE database_name;
USE database_name;

CREATE TABLE table_name (
    id INT AUTO_INCREMENT PRIMARY KEY,
    caliber VARCHAR(50),
    shop VARCHAR(255),
    link VARCHAR(255),
    product_name VARCHAR(255),
    price VARCHAR(255),
    available VARCHAR(255),
    date_updated timestamp
);
```


Create `config.yaml` file in main catalog with following content:

```yaml
database:
  host: database_ip_address
  port: port
  user: username
  password: password
  db: database_name
  table: table_name
```

# Run

```bash
venv\bin\activate

python -m pip install -r requirements.txt

python run.py --config config.yaml
```

More info: [ammofinder/frontend](https://github.com/ammofinder/frontend)