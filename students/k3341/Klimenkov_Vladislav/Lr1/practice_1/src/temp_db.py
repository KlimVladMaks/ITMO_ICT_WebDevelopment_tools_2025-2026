from .models import Skill, SkillLevel, User


# Временная БД
temp_db = [
    User(
        id=1,
        email="ivan.petrov@example.com",
        full_name="Иван Петров",
        about="Опытный разработчик с 5-летним стажем",
        skills=[
            Skill(id=1, name="Python", level=SkillLevel.advanced),
            Skill(id=2, name="FastAPI", level=SkillLevel.intermediate),
            Skill(id=3, name="PostgreSQL", level=SkillLevel.novice)
        ]
    ),
    User(
        id=2,
        email="maria.sidorova@example.com",
        full_name="Мария Сидорова",
        about="Frontend разработчик, увлекаюсь UI/UX дизайном",
        skills=[
            Skill(id=4, name="JavaScript", level=SkillLevel.advanced),
            Skill(id=5, name="React", level=SkillLevel.intermediate)
        ]
    ),
    User(
        id=3,
        email="alexey.smirnov@example.com",
        full_name="Алексей Смирнов",
        about="Junior разработчик, активно изучаю программирование",
        skills=[]
    )
]
