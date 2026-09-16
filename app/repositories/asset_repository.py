"""_summary_
"""

from sqlalchemy.orm import Session

from app.models.assets import Asset

class AssetRepository:
    """
    
    """
    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_all (self) -> list[Asset]:
        """_summary_

        Returns:
            list[Asset]: _description_
        """
        return(
            self.db.query(Asset).all()
        )

    def get_all_by_user(self, id_user:str) -> list[Asset]