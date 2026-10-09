import random
from datetime import date, timedelta
import pandas as pd
from faker import Faker


def generate_fraud_dataset(
    num_records: int = 1000,
    num_vendors: int = 30,
    anomaly_rate: float = 0.08,
    seed: int = 42
) -> pd.DataFrame:
    """
    Erstellt ein DataFrame mit synthetischen Rechnungsdaten und kontrollierten Anomalien.
    """
    # 1. Seeds für vollständige Reproduzierbarkeit setzen
    random.seed(seed)
    Faker.seed(seed)
    fake = Faker('de_DE')

    # Feste Datumsspanne für konsistente Ergebnisse
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    max_days = (end_date - start_date).days

    # 2. Lieferanten-Stammdaten mit eindeutigen IDs erzeugen
    categories = [
        'IT Services', 'Office Supplies', 'Marketing', 'Consulting',
        'Logistics', 'Facility Management', 'Legal & Tax'
    ]
    
    vendors = []
    for idx in range(1, num_vendors + 1):
        vendors.append({
            'vendor_id': f"VND-{idx:04d}",
            'vendor_name': fake.company(),
            'category': random.choice(categories),
            'default_iban': fake.iban()
        })

    invoices = []

    # 3. Rechnungsdaten generieren
    for i in range(1, num_records + 1):
        invoice_id = f"RE-2025-{i:05d}"
        vendor = random.choice(vendors)
        
        vendor_id = vendor['vendor_id']
        vendor_name = vendor['vendor_name']
        category = vendor['category']
        iban = vendor['default_iban']

        # Grundlegende Betragsverteilung (typische Rechnungsbeträge zwischen 50€ und 5.000€)
        amount = round(random.uniform(50.0, 5000.0), 2)

        # Basisdatum ziehen
        random_days = random.randint(0, max_days)
        invoice_date = start_date + timedelta(days=random_days)

        # Normale Rechnungen strikt auf Werktage (Mo-Fr) legen
        if invoice_date.weekday() >= 5:  # 5 = Samstag, 6 = Sonntag
            # Auf den folgenden Montag verschieben
            days_to_add = 7 - invoice_date.weekday()
            invoice_date += timedelta(days=days_to_add)
            if invoice_date > end_date:
                invoice_date = end_date - timedelta(days=(end_date.weekday() - 4))

        is_suspicious = 0
        anomaly_type = "KEINE"

        # Prüfen, ob für diese Zeile eine Anomalie erzeugt werden soll
        if random.random() < anomaly_rate:
            is_suspicious = 1
            
            # Mögliche Anomalie-Typen zusammenstellen
            anomaly_choices = ['outlier_amount', 'changed_iban', 'weekend_booking']
            
            # 'duplicate_invoice' nur zulassen, wenn bereits Vorlagen existieren
            if len(invoices) > 0:
                anomaly_choices.append('duplicate_invoice')

            chosen_anomaly = random.choice(anomaly_choices)
            anomaly_type = chosen_anomaly

            if chosen_anomaly == 'outlier_amount':
                # Ungewöhnlich hoher Betrag (15.000€ bis 95.000€)
                amount = round(random.uniform(15000.0, 95000.0), 2)
                anomaly_type = "HOHER_BETRAG"

            elif chosen_anomaly == 'changed_iban':
                # Abweichende IBAN (z. B. Phishing / gefälschte Stammdaten)
                iban = fake.iban()
                anomaly_type = "IBAN_ABWEICHUNG"

            elif chosen_anomaly == 'weekend_booking':
                # Datum gezielt auf Samstag oder Sonntag verschieben
                target_weekday = random.choice([5, 6])  # 5 = Sa, 6 = So
                days_diff = target_weekday - invoice_date.weekday()
                
                new_date = invoice_date + timedelta(days=days_diff)
                
                # Sicherstellen, dass das Datum im erlaubten Bereich bleibt
                if new_date > end_date:
                    new_date = invoice_date - timedelta(days=(7 - days_diff))
                
                invoice_date = new_date
                anomaly_type = "WOCHENEND_BUCHUNG"

            elif chosen_anomaly == 'duplicate_invoice':
                # Vorherige Rechnung komplett duplizieren (inkl. IBAN & Betrag)
                prev_inv = random.choice(invoices)
                
                # Betrag & Stammdaten der Originalrechnung übernehmen
                amount = prev_inv['amount_eur']  # Korrigierter Schlüssel
                vendor_id = prev_inv['vendor_id']
                vendor_name = prev_inv['vendor_name']
                category = prev_inv['category']
                iban = prev_inv['iban']  # IBAN mitkopieren für sauberes Duplikat
                
                anomaly_type = "DOPPELTE_RECHNUNG"

        invoices.append({
            'invoice_id': invoice_id,
            'invoice_date': invoice_date,  # Nativer date-Typ
            'vendor_id': vendor_id,
            'vendor_name': vendor_name,
            'category': category,
            'amount_eur': amount,
            'iban': iban,
            'ist_anomalie': is_suspicious,
            'anomalie_typ': anomaly_type
        })

    # DataFrame erzeugen
    df = pd.DataFrame(invoices)
    return df


if __name__ == '__main__':
    print("Starte Generierung der synthetischen Rechnungsdaten...")
    
    # Datensatz generieren (1.000 Datensätze, Seed 42)
    df_invoices = generate_fraud_dataset(num_records=1000, anomaly_rate=0.08, seed=42)

    # In CSV-Datei exportieren
    output_filename = 'rechnungen_anomalien.csv'
    df_invoices.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"Erfolgreich {len(df_invoices)} Datensätze in '{output_filename}' gespeichert.\n")

    # Zusammenfassung der Datensatz-Statistiken anzeigen
    print("=== Übersicht der generierten Anomalien ===")
    summary = df_invoices['anomalie_typ'].value_counts()
    print(summary)
    
    print("\n=== Anomalie-Quote ===")
    total_anomalies = df_invoices['ist_anomalie'].sum()
    print(f"Gesamtanzahl Anomalien: {total_anomalies} ({total_anomalies / len(df_invoices):.1%})")