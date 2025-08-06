from typing import List, Dict, Tuple, Union, Optional
from CRUD.constants import MaterialStatus
from CRUD.materials_crud import MaterialCRUD


class MaterialService:
    def __init__(self, db_connection):
        self.crud = MaterialCRUD(db_connection)

    def add_new_material(self, name: str, author: str, publisher: str, type_id: int) -> Tuple[bool, Union[int, str]]:
        """Add a new material"""
        if not all([name.strip(), author.strip()]):
            return False, "The name and author cannot be empty"
        return self.crud.create_material(name, author, publisher, type_id)

    def get_material_details(self, material_id: int) -> Optional[Dict]:
        """Get material details"""
        material = self.crud.get_material(material_id)
        if material:
            material['status_text'] = MaterialStatus(material['status']).name
        return material

    def search_materials(self, keyword: str = None, material_type: int = None) -> List[Dict]:
        """Search for materials"""
        materials = self.crud.get_available_materials()

        # Apply filtering conditions
        if keyword:
            keyword = keyword.lower()
            materials = [m for m in materials
                         if keyword in m['material_name'].lower()
                         or keyword in m['author'].lower()]

        if material_type is not None:
            materials = [m for m in materials if m['type_id'] == material_type]

        # Add status text
        for m in materials:
            m['status_text'] = MaterialStatus(m['status']).name

        return materials

    def update_material_status(self, material_id: int, new_status: int) -> Tuple[bool, str]:
        """Update the material status"""
        if new_status not in [s.value for s in MaterialStatus]:
            return False, f"Invalid status value, available options: {[s.value for s in MaterialStatus]}"
        return self.crud.update_material_status(material_id, new_status)