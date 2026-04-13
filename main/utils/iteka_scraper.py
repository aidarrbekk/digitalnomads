"""
Batch scraper for i-teka.kz — Kazakhstan pharmacy price aggregator.

Fetches medication data and stores it in the local database.
Designed to run periodically (every 12 hours) via scheduler.

Provides:
    sync_iteka_data(app) — main entry point: scrape and upsert DB records
    search_medications(query, city) — search via JSON API
    get_medication_detail(slug, city) — per-pharmacy pricing from HTML
"""

import logging
import re
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TIMEOUT = 15
_BASE = "https://i-teka.kz"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

CITY_SLUGS = {
    "almaty": "almaty",
    "astana": "astana",
    "shymkent": "shymkent",
    "karaganda": "karaganda",
    "aktobe": "aktobe",
    "atyrau": "atyrau",
    "aktau": "aktau",
    "pavlodar": "pavlodar",
    "kostanai": "kostanai",
    "semei": "semei",
    "oral": "oral",
    "taldykorgan": "taldykorgan",
    "kokshetau": "kokshetau",
    "kyzylorda": "kyzylorda",
    "taraz": "taraz",
    "petropavlovsk": "petropavlovsk",
    "temirtau": "temirtau",
    "turkestan": "turkestan",
    "ekibastuz": "ekibastuz",
    "rudny": "rudny",
    "zhanaozen": "zhanaozen",
    "balkhash": "balkhash",
    "jezkazgan": "jezkazgan",
    "zhetysai": "zhetysai",
}

# Common medication search terms for batch scraping
SEARCH_TERMS = [
    "парацетамол", "ибупрофен", "аспирин", "амоксициллин", "цефтриаксон",
    "омепразол", "метформин", "лоратадин", "цетиризин", "диклофенак",
    "нурофен", "но-шпа", "мезим", "смекта", "активированный уголь",
    "валидол", "корвалол", "анальгин", "супрастин", "фуразолидон",
    "левомеколь", "хлоргексидин", "йод", "бинт", "пластырь",
    "витамин с", "витамин д", "кальций", "железо", "магний",
    "ренни", "фестал", "линекс", "энтеросгель", "полисорб",
    "називин", "аквамарис", "гриппферон", "арбидол", "тамифлю",
    "амброксол", "бромгексин", "мукалтин", "ацц", "лазолван",
    "нафтизин", "отривин", "снуп", "ксилен", "риностоп",
]


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": _UA})
    return s


def search_medications(query: str, city: str = "almaty") -> dict:
    """Search medications via i-teka.kz global search API."""
    city = city.lower()
    if city not in CITY_SLUGS:
        city = "almaty"

    try:
        s = _session()
        s.cookies.set("new_city_id", city, domain="i-teka.kz")

        r = s.get(
            f"{_BASE}/global-search/run",
            params={"query": query},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        if not data.get("result") or not data.get("data", {}).get("status"):
            return {"ok": True, "results": [], "error": None}

        soup = BeautifulSoup(data["data"]["html"], "html.parser")
        items = soup.select(".multi-item")

        results = []
        for item in items:
            link = item.select_one("a[href*=medicaments]")
            name_el = item.select_one(".multi-content a")
            price_el = item.select_one(".multi-price")

            if not link or not name_el:
                continue

            href = link.get("href", "")
            slug_match = re.search(r"/medicaments/([^?]+)", href)
            slug = slug_match.group(1) if slug_match else ""

            results.append({
                "name": name_el.get_text(strip=True),
                "price_text": price_el.get_text(strip=True) if price_el else "",
                "slug": slug,
                "url": f"{_BASE}/{city}/medicaments/{slug}",
            })

        return {"ok": True, "results": results, "error": None}

    except requests.RequestException as e:
        return {"ok": False, "results": [], "error": str(e)}
    except (ValueError, KeyError) as e:
        return {"ok": False, "results": [], "error": f"Parse error: {e}"}


def get_medication_detail(slug: str, city: str = "almaty") -> dict:
    """Get detailed medication info with per-pharmacy pricing."""
    city = city.lower()
    if city not in CITY_SLUGS:
        city = "almaty"

    try:
        s = _session()
        r = s.get(f"{_BASE}/{city}/medicaments/{slug}", timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        name_el = soup.select_one(".container-drug-item .name")
        med_name = name_el.get_text(strip=True) if name_el else slug

        price_stats = {}
        stat_table = soup.select_one(".price-statistic")
        if stat_table:
            rows = stat_table.select("tr")
            for row in rows:
                text = row.get_text(strip=True)
                price_match = re.search(r"([\d\s\u2009\u00a0]+)\s*тг", text)
                price_val = re.sub(r'\D', '', price_match.group(1)) if price_match else None
                if "Самая низкая" in text and price_val:
                    price_stats["min"] = int(price_val)
                elif "Самая высокая" in text and price_val:
                    price_stats["max"] = int(price_val)
                elif "Средняя" in text and price_val:
                    price_stats["avg"] = int(price_val)
                elif "Продают аптек" in text:
                    count_match = re.search(r"(\d+)", text)
                    if count_match:
                        price_stats["pharmacy_count"] = int(count_match.group(1))

        pharmacies = []
        rows = soup.select(".list-item.gtm_block_apteka")
        for row in rows:
            title_el = row.select_one(".title")
            addr_el = row.select_one(".address")
            status_el = row.select_one(".status")
            price_el = row.select_one(".price")

            pharmacy_name = title_el.get_text(strip=True) if title_el else ""
            address = addr_el.get_text(strip=True) if addr_el else ""
            status = status_el.get_text(strip=True) if status_el else ""

            price = None
            if price_el:
                pm = re.search(r"([\d\s\u2009\u00a0]+)\s*тг", price_el.get_text(strip=True))
                if pm:
                    price = int(re.sub(r'\D', '', pm.group(1)))

            if pharmacy_name:
                pharmacies.append({
                    "name": pharmacy_name,
                    "address": address,
                    "status": status,
                    "price": price,
                })

        # --- Characteristics table (from .feature-modal) ---
        characteristics = {}
        feat_table = soup.select_one(".feature-modal table")
        if feat_table:
            for tr in feat_table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) >= 2:
                    characteristics[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)

        # --- Instruction sections (from .instruction-full) ---
        instruction_sections = {}
        instr_el = soup.select_one(".instruction-full")
        if instr_el:
            parts = re.split(r"<strong[^>]*>(.*?)</strong>", str(instr_el))
            for i in range(1, len(parts) - 1, 2):
                heading = BeautifulSoup(parts[i], "html.parser").get_text(strip=True)
                content = BeautifulSoup(parts[i + 1], "html.parser").get_text(separator=" ", strip=True)
                if heading and content:
                    instruction_sections[heading] = content

        # Map to structured fields
        med_info = _extract_med_info(characteristics, instruction_sections)

        return {
            "ok": True,
            "medication": med_name,
            "slug": slug,
            "city": city,
            "url": f"{_BASE}/{city}/medicaments/{slug}",
            "price_stats": price_stats,
            "pharmacies": pharmacies,
            "med_info": med_info,
            "error": None,
        }

    except requests.RequestException as e:
        return {"ok": False, "medication": None, "pharmacies": [], "price_stats": {}, "error": str(e)}
    except (ValueError, KeyError) as e:
        return {"ok": False, "medication": None, "pharmacies": [], "price_stats": {}, "error": f"Parse error: {e}"}


def _extract_med_info(characteristics: dict, instruction_sections: dict) -> dict:
    """Map i-teka characteristics table + instruction sections to Medication model fields."""
    info = {}

    # Active ingredient from characteristics table (МНН) or instruction
    mnn = characteristics.get("МНН", "")
    if not mnn or mnn == "-":
        mnn = _find_section(instruction_sections, "Международное непатентованное название")
    if mnn and mnn != "-":
        info["active_ingredient"] = mnn

    # Dosage form from characteristics or instruction
    form = characteristics.get("Лекарственная форма", "")
    if not form:
        form = _find_section(instruction_sections, "Лекарственная форма")
    if form:
        info["dosage_forms"] = form

    # Dosage / strengths from characteristics
    dosage = characteristics.get("Дозировка", "")
    if dosage:
        info["available_strengths"] = dosage

    # Description = indications (Показания к применению)
    indications = _find_section(instruction_sections, "Показания к применению")
    if indications:
        info["description"] = indications[:1000]

    # Contraindications
    contra = _find_section(instruction_sections, "Противопоказания")
    if contra:
        info["contraindications"] = contra[:1000]

    # Side effects
    side = _find_section(instruction_sections, "Описание нежелательных реакций")
    if not side:
        side = _find_section(instruction_sections, "Побочные действия")
    if not side:
        side = _find_section(instruction_sections, "Нежелательные реакции")
    if side:
        info["side_effects"] = side[:1000]

    # Storage instructions
    storage = _find_section(instruction_sections, "Условия хранения")
    if not storage:
        storage = _find_section(instruction_sections, "Хранить")
    if storage:
        info["storage_instructions"] = storage[:500]

    # Manufacturer
    mfr = _find_section(instruction_sections, "Сведения о производителе")
    if not mfr:
        mfr = _find_section(instruction_sections, "Держатель регистрационного удостоверения")
    if mfr:
        info["manufacturer"] = mfr[:255]

    return info


def _find_section(sections: dict, prefix: str) -> str:
    """Find instruction section by heading prefix (case-insensitive startswith)."""
    prefix_lower = prefix.lower()
    for key, val in sections.items():
        if key.lower().startswith(prefix_lower):
            return val
    return ""


def _clean_med_name(name: str) -> str:
    """Strip city price suffixes like ' - цена в Алматы' from medication names."""
    return re.sub(r'\s*-\s*цена в\s+\S+$', '', name).strip()


def _parse_price_text(text: str):
    """Extract numeric price from text like 'от 255 тг.' or '1 200 тг.'"""
    if not text:
        return None
    m = re.search(r'([\d\s\u2009\u00a0]+)\s*тг', text)
    if m:
        return int(re.sub(r'\D', '', m.group(1)))
    return None


# Well-known medication slugs that are guaranteed to have pharmacy data on i-teka.kz
_POPULAR_SLUGS = [
    "paracetamol-tabletki-500-mg-10",
    "ibuprofen-akos-tabletki-200-mg-20",
    "analjgin-tabletki-500-mg-50",
    "no-shpa-forte-tabletki-80-mg-20",
    "smekta-poroshok-3-gr-30",
    "ugolj-aktivirovannyy-kapsuly-20",
    "mezim-forte-20-000-tabletki-20",
    "suprastin-tabletki-25-mg-40",
    "loratadin-tabletki-10-mg-30",
    "omeprazol-adzhio-kapsuly-20-mg-30",
    "diklofenak-tabletki-50-mg-20",
    "ambroksol-tabletki-30-mg-20",
    "nazivin-sensitiv-sprey-22-5-mkg-doza-10-ml",
    "lineks-forte-kapsuly-28",
    "enterosgelj-pasta-dlya-priema-vnutrj-22-5-gr-10",
    "hlorgeksidina-rastvor-0-05-100-ml",
    "cetirizin-tabletki-10-mg-10",
    "validol-tabletki-60-mg-10",
    "korvalol-kapli-25-ml",
    "naftizin-kapli-0-1-15-ml",
]


def sync_iteka_data(app, max_details_per_term=0):
    """Batch-sync medication data from i-teka.kz into the local database.

    Phase 1: Search API (fast) — adds medication names from all search terms.
    Phase 2: Detail pages (slow) — fetches pharmacy data for popular slugs only.
    """
    from main.models import db, Medication, Pharmacy, PharmacyStock, MedicationCategory

    city = "almaty"
    seen_names = set()
    total_meds = 0
    total_stocks = 0

    with app.app_context():
        # Get or create a category for i-teka medications
        iteka_cat = MedicationCategory.query.filter_by(name="i-teka.kz").first()
        if not iteka_cat:
            iteka_cat = MedicationCategory(name="i-teka.kz", name_ru="i-teka.kz", name_kz="i-teka.kz")
            db.session.add(iteka_cat)
            db.session.commit()

        # ---- Phase 1: Fast search to populate medication names ----
        print("=== Phase 1: Searching medication names ===")
        for idx, term in enumerate(SEARCH_TERMS, 1):
            try:
                print(f"[{idx}/{len(SEARCH_TERMS)}] {term}...", end=" ")
                result = search_medications(term, city)
                if not result.get("ok") or not result.get("results"):
                    print("0 results")
                    continue

                count = 0
                for item in result["results"]:
                    med_name = _clean_med_name(item.get("name", ""))
                    if not med_name or med_name in seen_names:
                        continue
                    seen_names.add(med_name)

                    if not Medication.query.filter_by(name=med_name).first():
                        price = _parse_price_text(item.get("price_text", ""))
                        db.session.add(Medication(
                            name=med_name,
                            category_id=iteka_cat.id,
                            is_otc=True,
                        ))
                        total_meds += 1
                        count += 1

                db.session.commit()
                print(f"{len(result['results'])} found, {count} new")

            except Exception as e:
                print(f"ERROR: {e}")
                db.session.rollback()

        # ---- Phase 2: Detail pages for popular medications ----
        print(f"\n=== Phase 2: Fetching pharmacy data for {len(_POPULAR_SLUGS)} popular medications ===")
        for idx, slug in enumerate(_POPULAR_SLUGS, 1):
            try:
                print(f"[{idx}/{len(_POPULAR_SLUGS)}] {slug}...", end=" ")
                detail = get_medication_detail(slug, city)
                if not detail.get("ok") or not detail.get("medication"):
                    print("FAILED")
                    continue

                med_name = _clean_med_name(detail["medication"])
                pharmacies = detail.get("pharmacies", [])
                print(f"{med_name} ({len(pharmacies)} pharmacies)")

                # Upsert Medication
                med = Medication.query.filter_by(name=med_name).first()
                if not med:
                    med = Medication(name=med_name, category_id=iteka_cat.id, is_otc=True)
                    db.session.add(med)
                    db.session.flush()
                    total_meds += 1

                # Process pharmacies
                for pharm_data in pharmacies:
                    pharm_name = pharm_data.get("name", "").strip()
                    pharm_addr = pharm_data.get("address", "").strip()
                    if not pharm_name:
                        continue

                    # Upsert Pharmacy by name + address
                    pharm = Pharmacy.query.filter_by(name=pharm_name, address=pharm_addr).first()
                    if not pharm:
                        pharm = Pharmacy(
                            name=pharm_name,
                            name_ru=pharm_name,
                            address=pharm_addr,
                            city=city.capitalize(),
                            city_ru=city.capitalize(),
                        )
                        db.session.add(pharm)
                        db.session.flush()

                    # Upsert PharmacyStock
                    stock = PharmacyStock.query.filter_by(
                        pharmacy_id=pharm.id, medication_id=med.id
                    ).first()
                    price = pharm_data.get("price")
                    if stock:
                        stock.price = price
                        stock.quantity = 1 if price else 0
                    else:
                        stock = PharmacyStock(
                            pharmacy_id=pharm.id,
                            medication_id=med.id,
                            quantity=1 if price else 0,
                            price=price,
                            currency="KZT",
                        )
                        db.session.add(stock)
                        total_stocks += 1

                db.session.commit()

            except Exception as e:
                print(f"  ERROR: {e}")
                db.session.rollback()
                continue

        print(f"\ni-teka sync complete: {total_meds} new medications, {total_stocks} new stock entries")
        logger.info(f"i-teka sync complete: {total_meds} new medications, {total_stocks} new stock entries")
