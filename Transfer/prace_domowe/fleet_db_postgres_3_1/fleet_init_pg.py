from fleet_models_db import Base  # to twoje modele
from fleet_database import engine  # twój silnik SQLAlchemy

Base.metadata.create_all(engine)
print("✅ Tabele zostały utworzone w PostgreSQL.")
