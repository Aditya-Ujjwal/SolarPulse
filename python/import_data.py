import os
import time
import pandas as pd
from sqlalchemy import text
from database import engine


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

GENERATION_FILE = os.path.join(
    DATA_DIR, "Solar_Energy_Generation.csv"
)

WEATHER_FILE = os.path.join(
    DATA_DIR, "Weather_Data_reordered_all.csv"
)

SITE_FILE = os.path.join(
    DATA_DIR, "Solar_Site_Details.csv"
)

MONTHLY_FILE = os.path.join(
    DATA_DIR, "Monthly_Summary_Solar.csv"
)


# ============================================================
# CHECK FILES
# ============================================================

def check_files():

    print("\n" + "=" * 70)
    print("CHECKING DATA FILES")
    print("=" * 70)

    files = {
        "Solar Site Details": SITE_FILE,
        "Monthly Summary": MONTHLY_FILE,
        "Weather Data": WEATHER_FILE,
        "Solar Generation": GENERATION_FILE
    }

    for name, path in files.items():

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{name} file not found:\n{path}"
            )

        size_mb = os.path.getsize(path) / (1024 * 1024)

        print(f"{name:<25} {size_mb:>10.2f} MB")

    print("All files found successfully.")


# ============================================================
# CLEAR TABLES
# ============================================================

def clear_tables():

    print("\n" + "=" * 70)
    print("CLEARING EXISTING DATA")
    print("=" * 70)

    # Only these four tables exist at the moment.
    tables = [
        "monthly_summary",
        "weather_raw",
        "generation_raw",
        "solar_sites"
    ]

    with engine.begin() as connection:

        for table in tables:

            try:

                connection.execute(
                    text(f"TRUNCATE TABLE {table}")
                )

                print(f"Cleared: {table}")

            except Exception as e:

                print(f"Could not clear {table}: {e}")


# ============================================================
# REMOVE INDEXES
# ============================================================

def remove_indexes():

    print("\n" + "=" * 70)
    print("REMOVING INDEXES BEFORE LARGE IMPORT")
    print("=" * 70)

    index_commands = [
        (
            "generation_raw",
            "idx_generation_site_time"
        ),
        (
            "generation_raw",
            "idx_generation_timestamp"
        ),
        (
            "weather_raw",
            "idx_weather_timestamp"
        ),
        (
            "weather_raw",
            "idx_weather_campus_time"
        )
    ]

    with engine.begin() as connection:

        for table, index_name in index_commands:

            try:

                connection.execute(
                    text(
                        f"DROP INDEX {index_name} ON {table}"
                    )
                )

                print(
                    f"Removed {index_name} from {table}"
                )

            except Exception:

                print(
                    f"{index_name} not present - skipping"
                )


# ============================================================
# IMPORT SOLAR SITE DETAILS
# ============================================================

def import_sites():

    print("\n" + "=" * 70)
    print("IMPORTING SOLAR SITE DETAILS")
    print("=" * 70)

    df = pd.read_csv(SITE_FILE)

    print(f"Rows read: {len(df):,}")

    print(
        f"CSV columns:\n{list(df.columns)}"
    )

    # CSV → MySQL mapping
    df = df.rename(
        columns={
            "Number of panels": "Number_of_Panels",
            "lat": "Latitude",
            "Lon": "Longitude"
        }
    )

    # Convert empty strings to NULL
    df = df.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )

    # EXACT MySQL columns
    df = df[
        [
            "CampusKey",
            "SiteKey",
            "kWp",
            "Number_of_Panels",
            "Panel",
            "Inverter",
            "Optimizers",
            "Metric",
            "Latitude",
            "Longitude"
        ]
    ]

    df.to_sql(
        name="solar_sites",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=100
    )

    print(
        f"Successfully imported {len(df):,} site records."
    )


# ============================================================
# IMPORT MONTHLY SUMMARY
# ============================================================

def import_monthly_summary():

    print("\n" + "=" * 70)
    print("IMPORTING MONTHLY SUMMARY")
    print("=" * 70)

    df = pd.read_csv(MONTHLY_FILE)

    print(f"Rows read: {len(df):,}")

    print(
        f"CSV columns:\n{list(df.columns)}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # The CSV contains "Month", but your MySQL table DOES NOT.
    # Therefore we deliberately remove Month from the import.
    # --------------------------------------------------------

    # Convert empty strings to NULL
    df = df.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )

    # Select ONLY columns existing in MySQL
    df = df[
        [
            "SiteKey",
            "Year",
            "DataStatus",
            "AverageSolarGeneration",
            "MaxSolarGeneration",
            "MinSolarGeneration"
        ]
    ]

    # Make sure DataStatus is compatible with MySQL TINYINT
    df["DataStatus"] = pd.to_numeric(
        df["DataStatus"],
        errors="coerce"
    ).astype("Int64")

    # Numeric fields
    numeric_columns = [
        "AverageSolarGeneration",
        "MaxSolarGeneration",
        "MinSolarGeneration"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    print(
        f"Columns being inserted:\n{list(df.columns)}"
    )

    df.to_sql(
        name="monthly_summary",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )

    print(
        f"Successfully imported {len(df):,} monthly records."
    )


# ============================================================
# IMPORT WEATHER DATA
# ============================================================

def import_weather():

    print("\n" + "=" * 70)
    print("IMPORTING WEATHER DATA")
    print("=" * 70)

    total_rows = 0
    start_time = time.time()

    for chunk_number, df in enumerate(
        pd.read_csv(
            WEATHER_FILE,
            chunksize=10000,
            parse_dates=["Timestamp"]
        ),
        start=1
    ):

        # EXACT MySQL column order
        df = df[
            [
                "CampusKey",
                "Timestamp",
                "ApparentTemperature",
                "AirTemperature",
                "DewPointTemperature",
                "RelativeHumidity",
                "WindSpeed",
                "WindDirection"
            ]
        ]

        # Convert blank strings to NULL
        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        # Convert numeric columns explicitly
        numeric_columns = [
            "ApparentTemperature",
            "AirTemperature",
            "DewPointTemperature",
            "RelativeHumidity",
            "WindSpeed",
            "WindDirection"
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df.to_sql(
            name="weather_raw",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=10000,
            method="multi"
        )

        total_rows += len(df)

        if chunk_number % 10 == 0:

            elapsed = time.time() - start_time

            print(
                f"Weather progress: "
                f"{total_rows:,} rows | "
                f"{elapsed / 60:.2f} minutes"
            )

    elapsed = time.time() - start_time

    print("\nWeather import completed.")
    print(f"Total rows: {total_rows:,}")
    print(
        f"Time taken: {elapsed / 60:.2f} minutes"
    )


# ============================================================
# IMPORT SOLAR GENERATION DATA
# ============================================================

def import_generation():

    print("\n" + "=" * 70)
    print("IMPORTING SOLAR GENERATION DATA")
    print("=" * 70)

    total_rows = 0
    start_time = time.time()

    for chunk_number, df in enumerate(
        pd.read_csv(
            GENERATION_FILE,
            chunksize=10000,
            parse_dates=["Timestamp"]
        ),
        start=1
    ):

        # EXACT MySQL column order
        df = df[
            [
                "CampusKey",
                "SiteKey",
                "Timestamp",
                "SolarGeneration"
            ]
        ]

        # Convert blank strings to NULL
        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        # Make sure generation is numeric
        df["SolarGeneration"] = pd.to_numeric(
            df["SolarGeneration"],
            errors="coerce"
        )

        df.to_sql(
            name="generation_raw",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=10000,
            method="multi"
        )

        total_rows += len(df)

        if chunk_number % 20 == 0:

            elapsed = time.time() - start_time

            print(
                f"Generation progress: "
                f"{total_rows:,} rows | "
                f"{elapsed / 60:.2f} minutes"
            )

    elapsed = time.time() - start_time

    print("\nGeneration import completed.")
    print(f"Total rows: {total_rows:,}")
    print(
        f"Time taken: {elapsed / 60:.2f} minutes"
    )


# ============================================================
# RECREATE INDEXES
# ============================================================

def recreate_indexes():

    print("\n" + "=" * 70)
    print("RECREATING INDEXES")
    print("=" * 70)

    with engine.begin() as connection:

        # Generation indexes
        connection.execute(
            text(
                """
                CREATE INDEX idx_generation_site_time
                ON generation_raw (SiteKey, Timestamp)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX idx_generation_timestamp
                ON generation_raw (Timestamp)
                """
            )
        )

        # Weather indexes
        connection.execute(
            text(
                """
                CREATE INDEX idx_weather_timestamp
                ON weather_raw (Timestamp)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX idx_weather_campus_time
                ON weather_raw (CampusKey, Timestamp)
                """
            )
        )

    print("Indexes recreated successfully.")


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_database():

    print("\n" + "=" * 70)
    print("VERIFYING MYSQL DATABASE")
    print("=" * 70)

    expected = {
        "solar_sites": 42,
        "monthly_summary": 1176,
        "weather_raw": 371769,
        "generation_raw": 2731946
    }

    with engine.connect() as connection:

        all_good = True

        for table, expected_count in expected.items():

            result = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM {table}"
                )
            )

            actual_count = result.scalar()

            if actual_count == expected_count:
                status = "✓"
            else:
                status = "✗"
                all_good = False

            print(
                f"{status} "
                f"{table:<25} "
                f"{actual_count:>12,} "
                f"(expected {expected_count:,})"
            )

    print()

    if all_good:
        print(
            "DATABASE VERIFICATION PASSED."
        )
    else:
        print(
            "DATABASE VERIFICATION FAILED."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("              SOLARPULSE DATA IMPORT")
    print("=" * 70)

    start_time = time.time()

    try:

        # Step 1
        check_files()

        # Step 2
        clear_tables()

        # Step 3
        remove_indexes()

        # Step 4
        import_sites()

        # Step 5
        import_monthly_summary()

        # Step 6
        import_weather()

        # Step 7
        import_generation()

        # Step 8
        recreate_indexes()

        # Step 9
        verify_database()

        elapsed = time.time() - start_time

        print("\n" + "=" * 70)
        print("              IMPORT COMPLETED")
        print("=" * 70)

        print(
            f"Total execution time: "
            f"{elapsed / 60:.2f} minutes"
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("              IMPORT FAILED")
        print("=" * 70)

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error: {e}"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()