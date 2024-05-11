import os
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.solution.solution import Solution
from app.repositories.solution.solution_repository import SolutionRepository
from app.utils.handling_file import delete_file, upload_file

class SolutionService:
    def __init__(self, db: Session):
        self.db = db
        self.solution_repository = SolutionRepository(db)
        self.static_folder_image = "static/images/solution/image"
        self.static_folder_logo = "static/images/solution/logo"

    def create_solution(self, file_name: str, solution: Solution, image: UploadFile = None, logo: UploadFile = None, file_extension_image = None, file_extension_logo = None):
        solution.image_url = upload_file(image, self.static_folder_image, file_extension_image,  file_name) if image else ''
        solution.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, file_name) if logo else ''

        return self.solution_repository.create_solution(solution)

    def update_solution(
        self,
        file_name: str,
        exist_solution: Solution, 
        solution: Solution,
        image: UploadFile = None,
        logo: UploadFile = None,
        file_extension_image = None,
        file_extension_logo = None,
    ):
        if image and exist_solution.image_url:
            file_path = os.path.join(self.static_folder_image, exist_solution.image_url)
            delete_file(file_path)
            exist_solution.image_url = upload_file(image, self.static_folder_image, file_extension_image, file_name)
        
        if image and not exist_solution.image_url:
            exist_solution.image_url = upload_file(image, self.static_folder_image, file_extension_image, file_name)

        if logo and exist_solution.logo_url:
            file_path = os.path.join(self.static_folder_logo, exist_solution.logo_url)
            delete_file(file_path)
            exist_solution.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, file_name)

        if logo and not exist_solution.logo_url:
            exist_solution.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, file_name)

        exist_solution.title = solution.title
        exist_solution.is_active = solution.is_active

        return self.solution_repository.update_solution(exist_solution)

    def delete_solution(self, solution_id: str):
        solution = self.solution_repository.read_solution(solution_id)
        if not solution:
            raise ValueError("Solution not found")

        if solution.image_url:
            file_path = os.path.join(self.static_folder_image, solution.image_url)
            delete_file(file_path)
        
        if solution.logo_url:
            file_path = os.path.join(self.static_folder_logo, solution.logo_url)
            delete_file(file_path)

        return self.solution_repository.delete_solution(solution)
