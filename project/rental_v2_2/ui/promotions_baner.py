# directory: ui
# file: promotions.py

from models.promotions import Promotion


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