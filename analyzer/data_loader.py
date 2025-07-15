from typing import List, Dict
from ..utils.database import DatabaseManager

class DataLoader:
    """Handles data loading from multiple sources (Single Responsibility)"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def load_data_from_database(self) -> List[Dict]:
        """Load all scraped data from SQLite database"""
        return self.db_manager.get_posts_for_analysis() 