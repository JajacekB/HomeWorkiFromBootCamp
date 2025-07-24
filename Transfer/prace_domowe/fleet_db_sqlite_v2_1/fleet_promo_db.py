from fleet_models_db import Promotion

def show_promo_banner():
    print("\n" + "=" * 60)
    print(" 🎉 WITAJ W PROGRAMIE KORZYŚCI W NASZEJ WYPOŻYCZALNI 🎉")
    print("-" * 60)
    print(" 🏷️ PROMOCJE:")
    print("   🔹  5% zniżki przy wypożyczeniu na minimum 5 dni")
    print("   🔹  9% zniżki przy wypożyczeniu na minimum 7 dni")
    print("   🔹 20% zniżki przy wypożyczeniu na 14 dni lub dłużej!")
    print()
    print(" 💎 PROGRAM LOJALNOŚCIOWY:")
    print("   🔁 Co 10 wypożyczenie — całkowicie ZA DARMO!")
    print("-" * 60)
    print(" 🚀 Skorzystaj już dziś i ruszaj w drogę z rabatem!")
    print("=" * 60 + "\n")


def show_dynamic_promo_banner(session):
    time_promos = session.query(Promotion).filter_by(type='time').order_by(Promotion.min_days).all()
    loyalty_promos = session.query(Promotion).filter_by(type='loyalty').all()

    print("\n" + "=" * 60)
    print(" 🎉 NASZE AKTUALNE PROMOCJE 🎉")
    print("-" * 60)

    if time_promos:
        print(" 🏷️ Zniżki czasowe:")
        for promo in time_promos:
            print(f"   🔹 {promo.discount_percent:.0f}% zniżki przy wynajmie na minimum {promo.min_days} dni")

    if loyalty_promos:
        print("\n 💎 Program lojalnościowy:")
        for promo in loyalty_promos:
            print(f"   🔁 {promo.description}")

    print("-" * 60)
    print(" 🚀 Zgarnij rabat i wypożycz taniej już dziś!")
    print("=" * 60 + "\n")