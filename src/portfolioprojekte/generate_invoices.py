import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Seed für Reproduzierbarkeit setzen
fake = Faker('de_DE')
Faker.seed(42)
random.seed(42)

def generate_synthetic_invoices(num_records=1000, anomaly_rate=0.08):
    """
    Generiert einen synthetischen Datensatz für Rechnungsdaten inklusive
    gezielter Betrugsmuster und Anomalien für BI- & Analytics-Systeme.
    """
    
    # 1. Lieferanten-Stammdaten anlegen (Vendor Master Data)
    vendors = []
    for _ in range(30):
        vendors.append({
            'vendor_id': f"VND-{random.randint(1000, 9999)}",
            'vendor_name': fake.company(),
            'standard_iban': fake.iban()
        })

    invoices = []

    for i in range(1, num_records + 1):
        vendor = random.choice(vendors)
        
        # Normale Werte generieren
        invoice_id = f"INV-2026-{i:05d}"
        invoice_date = fake.date_between(start_date='-1y', end_date='today')
        # Normale Beträge zwischen 50 und 3.500 EUR
        amount = round(random.uniform(50.0, 3500.0), 2)
        iban = vendor['standard_iban']
        vendor_name = vendor['vendor_name']
        vendor_id = vendor['vendor_id']
        category = random.choice(['IT-Services', 'Bürobedarf', 'Beratung', 'Instandhaltung', 'Marketing'])
        
        # Anomalie-Typen initialisieren
        anomaly_type = "Normal"
        is_suspicious = 0

        # Zufällig festlegen, ob eine Anomalie eingebaut werden soll
        if random.random() < anomaly_rate:
            is_suspicious = 1
            anomaly_choice = random.choice([
                'duplicate_invoice', 
                'outlier_amount', 
                'changed_iban', 
                'weekend_booking'
            ])

            if anomaly_choice == 'duplicate_invoice':
                # Simulation einer Doppelerfassung oder doppelter Abrechnung
                anomaly_type = "Doppelte Rechnung"
                if invoices:
                    # Nimm eine vorherige Rechnung und kopiere ID & Betrag
                    prev_inv = random.choice(invoices)
                    invoice_id = prev_inv['invoice_id']
                    amount = prev_inv['amount_eur']
                    vendor_id = prev_inv['vendor_id']
                    vendor_name = prev_inv['vendor_name']

            elif anomaly_choice == 'outlier_amount':
                # Ungewöhnlich hoher Rechnungsbetrag (Ausreißer)
                anomaly_type = "Ungewöhnlich hoher Betrag"
                amount = round(random.uniform(25000.0, 150000.0), 2)

            elif anomaly_choice == 'changed_iban':
                # Abweichende IBAN für bekannten Lieferanten (Verdacht auf Identitätsdiebstahl/Phishing)
                anomaly_type = "Abweichende IBAN"
                iban = fake.iban()

            elif anomaly_choice == 'weekend_booking':
                # Buchung/Rechnungsdatum fällt auf ein Wochenende
                anomaly_type = "Wochenend-Buchung"
                # Nächsten Samstag oder Sonntag berechnen
                days_ahead = 5 - invoice_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                invoice_date = invoice_date + timedelta(days=days_ahead)

        # Datensatz hinzufügen
        invoices.append({
            'invoice_id': invoice_id,
            'vendor_id': vendor_id,
            'vendor_name': vendor_name,
            'invoice_date': invoice_date.strftime('%Y-%m-%d'),
            'amount_eur': amount,
            'iban': iban,
            'category': category,
            'is_suspicious': is_suspicious,
            'anomaly_type': anomaly_type
        })

    return pd.DataFrame(invoices)

if __name__ == "__main__":
    print("Erstelle synthetische Rechnungsdaten...")
    
    # Datensatz generieren (1000 Rechnungen, ca. 8% Anomalien)
    df_invoices = generate_synthetic_invoices(num_records=1000, anomaly_rate=0.08)
    
    # Als CSV-Datei speichern
    output_file = "invoices_fraud_dataset.csv"
    df_invoices.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Erfolgreich gespeichert unter: {output_file}")
    
    # Kurze Vorschau & Statistik ausgeben
    print("\n--- Übersicht der generierten Anomalien ---")
    print(df_invoices['anomaly_type'].value_counts())
