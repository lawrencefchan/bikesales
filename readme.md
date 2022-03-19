## Usage

```
pip install -r requirements.txt
py main.py
```

### main.py
Script to scrape, process, and save data from bikesales.com

### db schema
**listings_fact**
|Column | Description |
| ----- | ----------- |
|mileageFromOdometer | Distance travelled (km) |
|vehicleEngine | Engine size (cc) |
|offers | Listing price ($) |
|image | Number of pictures |
|modelId | Foreign key (model_dims)  |
|url_id | Unique string used in url (see: get_url) |
|year | Build Year - Year the vehicle was actually built |
|my | Model Year - Model cycle the vehicle is in |

**model_dims**
|Column | Description |
| ----- | ----------- |
|model | Model |
|brand | Brand |
|bodyType | Fairing stype |
|modelId | Primary key |
