import bcrypt
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
from app.models.role import Role
from app.models.role_authority import RoleAuthority, RoleAuthorityFeature, RoleAuthorityName

from app.models.user import User

config_env = dotenv_values()

# Step 2: Connect to PostgreSQL
engine = create_engine(config_env['DB'])
connection = engine.connect()

# Create base class
Base = declarative_base()

# Create session
Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# execute to do update and insert data
# role
def role_seeder():
    datas = [
        {
            'role_id': 1,
            'code': 'ADMIN',
            'level': 0,
            'name': 'ADMIN',
            'description': '',
        },
        {
            'role_id': 2,
            'code': 'USER',
            'level': 1,
            'name': 'USER',
            'description': '',
        },
    ]
    for data in datas:
        try:
            role_id = str(data['role_id'])
            code = str(data['code'])
            name = str(data['name'])
            description = str(data['description'])
            level = data['level']
            is_active = True
            # check data
            exist_data = session.query(Role).filter_by(id=role_id).first()
            if not exist_data: # create
                new_data = Role(
                    id=role_id,
                    name=name,
                    code=code,
                    description=description,
                    level=level,
                    is_active=is_active
                )
                session.add(new_data)
                print(f"created role {name} ")
            else: # update
                exist_data.name = name
                exist_data.code = code
                exist_data.description = description
                exist_data.level = level
                exist_data.is_active = is_active
                print(f"update role {name} ")
            session.commit()
        except Exception as e:
            print(f"Error processing data: {str(e)}")

# user
def user_seeder():
    datas = [
        {
            'user_id': 'TEST01',
            'role_id': 1,
            'username': 'ADMIN',
            'email': 'ADMIN@test.com',
            'name': 'ADMIN',
            'gender': 'male',
            'password': '1234',
        },
        {
            'user_id': 'TEST02',
            'role_id': 2,
            'username': 'FRY',
            'email': 'fry@test.com',
            'name': 'FRY',
            'gender': 'male',
            'password': '1234',
        },
    ]
    for data in datas:
        try:
            user_id = str(data['user_id'])
            role_id = str(data['role_id'])
            username = str(data['username'])
            password = str(data['password'])
            email = str(data['email'])
            name = str(data['name'])
            gender = data['gender']
            is_active = True
            # check data
            exist_data = session.query(User).filter_by(id=user_id).first()
            password = str(pwd_context.hash(str(password)))
            if not exist_data: # create
                new_data = User(
                    id=user_id,
                    role_id=role_id,
                    name=name,
                    username=username,
                    email=email,
                    password=password,
                    gender=gender,
                    is_active=is_active
                )
                session.add(new_data)
                print(f"created user {name} ")
            else: # update
                exist_data.role_id = role_id
                exist_data.name = name
                exist_data.username = username
                exist_data.email = email
                exist_data.password = password
                exist_data.gender = gender
                exist_data.is_active = is_active
                print(f"update user {name} ")
            session.commit()
        except Exception as e:
            print(f"Error processing data: {str(e)}")

# role authority
def role_authority_seeder():
    datas = [
        {
            'id': 'A1',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.user.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A2',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.user.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A3',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.user.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A3V',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.user.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A4',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.school.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A5',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.school.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A6',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.school.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A7',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.school.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A8',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.school.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A9',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.company.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A10',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.company.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A11',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.company.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A12',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.company.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A13',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A14',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A15',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 1,
        },
        {
            'id': 'A16',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 1,
        },
         {
            'id': 'B1',
            'name': RoleAuthorityName.assign.value,
            'feature': RoleAuthorityFeature.education.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B2',
            'name': RoleAuthorityName.unassign.value,
            'feature': RoleAuthorityFeature.education.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B3',
            'name': RoleAuthorityName.assign.value,
            'feature': RoleAuthorityFeature.experience.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B4',
            'name': RoleAuthorityName.unassign.value,
            'feature': RoleAuthorityFeature.experience.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B5',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.project.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B6',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.project.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B7',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.project.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B8',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.project.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B9',
            'name': RoleAuthorityName.unassign.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B10',
            'name': RoleAuthorityName.assign.value,
            'feature': RoleAuthorityFeature.skill.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B11',
            'name': RoleAuthorityName.create.value,
            'feature': RoleAuthorityFeature.service.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B12',
            'name': RoleAuthorityName.edit.value,
            'feature': RoleAuthorityFeature.service.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B13',
            'name': RoleAuthorityName.delete.value,
            'feature': RoleAuthorityFeature.service.value,
            'description': '',
            'role_id': 2,
        },
        {
            'id': 'B14',
            'name': RoleAuthorityName.view.value,
            'feature': RoleAuthorityFeature.service.value,
            'description': '',
            'role_id': 2,
        },
    ]
    for data in datas:
        try:
            role_authority_id = str(data['id'])
            role_id = str(data['role_id'])
            name = str(data['name'])
            feature = str(data['feature'])
            description = str(data['description'])
            # check data
            exist_data = session.query(RoleAuthority).filter_by(id=role_authority_id).first()
            if not exist_data: # create
                new_data = RoleAuthority(
                    id=role_authority_id,
                    role_id=role_id,
                    feature=feature,
                    name=name,
                    description=description,
                )
                session.add(new_data)
                print(f"created role authority {name} ")
            session.commit()
        except Exception as e:
            print(f"Error processing data: {str(e)}")

role_seeder()
user_seeder()
role_authority_seeder()

