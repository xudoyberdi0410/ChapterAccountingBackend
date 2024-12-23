import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.discord import Discord
from app.mangalib import MangaLib
from app.database import session, Workers, Roles, Chapters, Titles

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("CLIENT_SECRET")+"54"
app.config['JWT_SECRET_KEY'] = os.getenv("CLIENT_SECRET")
app.config['JWT_TOKEN_LOCATION'] = ['headers']

discord = Discord()
mangalib = MangaLib()

CORS(app)

jwt = JWTManager(app)

@app.route("/")
def home_page():
    """Домашняя страница"""
    return render_template("index.html")
    

@app.route("/oauth/callback")
def oauth():
    """
    Выполняет процедуру аунтентификации пользователя через Discord. Устанавливает нужные куки файлы.
    """
    
    code = request.args.get("code")
    if not code:
        return {"Error": "Problems with logging. Please, try again."}
    res = discord.login(code=code)

    if res.get("status") == "success":
        discord_access_token, discord_refresh_token = discord.get_tokens()

        access_token = create_access_token(identity=res.get("user_id"))

        worker = session.query(Workers).filter_by(discord_id=res.get("user_id")).first()
        if not worker:
            worker = Workers(nickname=res.get("username"), discord_id=res.get("user_id"), discord_access_token=discord_access_token, discord_refresh_token=discord_refresh_token, access_token=access_token)
            session.add(worker)
        else:
            worker.access_token = access_token
            worker.discord_access_token = discord_access_token
            worker.refresh_token = discord_refresh_token
        session.commit()

        return redirect(f"{os.getenv("FRONT_URL")}/?access_token={access_token}", Response={"status": "success"})
    else:
        return redirect(f"{os.getenv("FRONT_URL")}/", Response={"status": "error"})

@app.route("/login/discord")
def login_discord():
    """
    Генерирует ссылку и перенаправляет на страницу авторизации сервиса Discord.
    """
    
    return redirect(discord.generate_login_link())

@app.route("/api/user_data")
@jwt_required()
def user_data():
    """
    Возвращает данные пользователя.
    """
    
    user_id = get_jwt_identity()
    worker = session.query(Workers).filter_by(discord_id=user_id).first()

    userdata = discord.get_user_data(worker.discord_access_token)
    return jsonify(userdata)

@app.route("/api/manga_list")
@jwt_required()
def get_titles():
    """
    Возвращает список названий манги.
    """

    return jsonify(mangalib.get_manga_list())

@app.route("/api/roles")
@jwt_required()
def get_roles():
    """
    Возвращает список ролей.
    """
    roles = session.query(Roles).all()
    return jsonify([role.role_name for role in roles])

@app.route("/api/add", methods=["POST"])
@jwt_required()
def add_manga():
    """
    Добавляет мангу в список.
    """

    data = request.json
    with session as s:
        title = s.query(Titles).filter(
            or_(Titles.ru_name == data.get("title"), Titles.jp_name == data.get("title"))
        ).first()
        role = s.query(Roles).filter(Roles.role_name == data.get("role")).first()
        worker = s.query(Workers).filter_by(discord_id=get_jwt_identity()).first()
        chapter = Chapters(title_id=title.title_id, chapter=data.get("chapter"), role_id=role.role_id, workers_id=worker.workers_id)
        s.add(chapter)
        s.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route("/api/chapters")
@jwt_required()
def get_chapters():
    """
    Возвращает записи из базы данных в формате json. Поддерживает пагинацию. По умолчании последние 20 записей.
    """
    # get page from request
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    offset = (page - 1) * per_page

    chapters = session.query(Chapters).limit(per_page).offset(offset).all()
    data = []
    for chapter in chapters:
        data.append({
            "title": chapter.title.ru_name if chapter.title.ru_name else chapter.title.jp_name,
            "chapter": chapter.chapter,
            "role": chapter.role.role_name,
            "worker": chapter.worker.nickname
        })
    return jsonify(data)
    
