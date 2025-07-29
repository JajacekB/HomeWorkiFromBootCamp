from datetime import datetime, date

def get_return_date_from_user(session) -> date:
    while True:
        return_date_input_str = input(
            f"Podaj rzeczywistą datę zwrotu (DD-MM-YYYY) Enter = dziś: "
        ).strip().lower()

        try:

            if return_date_input_str:
                return_date_input = datetime.strptime(return_date_input_str, "%d-%m-%Y").date()
            else:
                return_date_input = date.today()
            break

        except ValueError:
            print("❌ Niepoprawny format daty.")
            continue
    return return_date_input