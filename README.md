# 🏠 Immo Eliza - Data Collection

A data collection project for **Immo Eliza**, a Belgian real estate company developing a **machine learning model** to predict property prices.
This stage focuses on **scraping property data** from (https://www.immovlan.be/en) and building a clean, structured dataset for future analysis.

---

## 🎯 Objectives

* Scrape and collect property data from Immovlan using Python
* Build a dataset with **at least 10,000 properties** from all over Belgium
* Work collaboratively with Git and Trello
* Prepare data for future price prediction modeling

---

## 🧠 Learning Outcomes

By completing this project, you’ll:

* Be able to scrape dynamic websites using `requests`, `BeautifulSoup`, or `Selenium`
* Build and clean datasets from raw web data
* Manage teamwork using **Trello** and **Git**
* Apply Pythonic best practices in a collaborative project

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Fred-git121/immo-eliza-scraping
   cd immo-eliza-scraping
   ```

2. **Create and activate a virtual environment**

   python immo-venv
   


3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```


## 🚀 Usage




Run the main scraper:

python main.py


The scraper will collect data from Immovlan and save it into the `data/` folder:

* `data/raw/` – unprocessed scraped data
* `data/cleaned/` – cleaned and formatted dataset ready for analysis

The final dataset will be a CSV file with at least the following columns:

* "Property ID",
    "city-line","Price","State of the property","Availability","Number of bedrooms","Livable surface","Furnished", "Surface of living room","Attic","Garage","Number of garages","Kitchen equipment","Kitchen type","Number of bathrooms","Number of showers","Number of toilets","Type of heating","Type of glazing","Elevator","Number of facades","Garden","Surface garden","Terrace","Surface terrace",
    "Total land surface","Swimming pool"

---

## 🧩 Project Structure

```
immo-eliza-scraping/
│
├── scraper/           # Scraping modules
├── data/
│   ├── raw/           # Raw data
│   └── cleaned/       # cleaned data
├── main.py            # Main entry point
├── requirements.txt   # Dependencies
├── .gitignore
└── README.md
```

---

## 📚 Sources

* [Immovlan](https://immovlan.be/en) — primary data source
* [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Selenium Documentation](https://www.selenium.dev/documentation/)

---

## 👥 Contributors

* [Astha] – Project Lead / https://www.linkedin.com/in/asthagudgilla/
* [Frédéric] – Repo Manager 
* [Brigi] – Data Engineer / https://www.linkedin.com/in/brigi-bodi/
* [Esra] – Documentation & QA / https://www.linkedin.com/in/esra-mogulkoc-865b683a/

---

## 🗓️ Timeline

* **Day 1–2:** Setup & small-scale scraping test
* **Day 3–4:** Full scraping + cleaning dataset
* **Day 5:** Dataset validation & final touches
* **Friday 4 PM:** Project presentation 🎤






